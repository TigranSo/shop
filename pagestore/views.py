from collections import Counter
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from .models import Product, Order, Discounted
from decimal import Decimal
from .models import OrderItem, OrderedProduct, Favorite
from django.db.models import Q
from .forms import RegistrationForm, AuthorizationForm, OrderFilterForm
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail



def shop(request):
    # Получаем все 
    all_products = Product.objects.all()
    discoun = Discounted.objects.filter(user=request.user)

    # Извлекаем параметры фильтрации, сортировки и категории из запроса
    filter_price_min = request.GET.get('price_min')
    filter_price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort_by')
    category = request.GET.get('category')

    # Применяем фильтры
    filtered_products = all_products

    if filter_price_min:
        filtered_products = filtered_products.filter(price__gte=filter_price_min)
    if filter_price_max:
        filtered_products = filtered_products.filter(price__lte=filter_price_max)
    if category:
        filtered_products = filtered_products.filter(category=category)

    # Применяем сортировку
    if sort_by == 'price_low':
        filtered_products = filtered_products.order_by('price')
    elif sort_by == 'price_high':
        filtered_products = filtered_products.order_by('-price')

    # Создаем Paginator для отфильтрованных и отсортированных товаров
    paginator = Paginator(filtered_products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_price_min': filter_price_min,
        'filter_price_max': filter_price_max,
        'sort_by': sort_by,
        'category': category,
        'discoun': discoun,
    }

    return render(request, 'pagestore/shop.html', context)


def homepage(request):
    products = Product.objects.all()[:3]
    cart_dict = request.session.get('cart', {})
    if request.user.is_authenticated:
        user = request.user
        total_spending = calculate_total_spending(request.user)
        discount_percentage = apply_discount(total_spending)
        user_favorites = Favorite.objects.get_or_create(user=user)[0].products.all()
        discoun = Discounted.objects.filter(user=request.user)
    else:
        user = None
        total_spending = 0
        discount_percentage = 0
        user_favorites = []
        discoun = None

    for product in products:
        product.quantity_in_cart = cart_dict.get(str(product.id), 0)
        product.discounted_price = float(product.price) - (float(product.price) * (float(discount_percentage) / 100))

    # Извлекаем параметры фильтрации, сортировки и категории из запроса
    filter_price_min = request.GET.get('price_min')
    filter_price_max = request.GET.get('price_max')
    sort_by = request.GET.get('sort_by')
    category = request.GET.get('category')

    # Применяем фильтрацию
    if filter_price_min:
        products = products.filter(price__gte=filter_price_min)
    if filter_price_max:
        products = products.filter(price__lte=filter_price_max)
    if category:
        products = products.filter(category=category)
    print(category)

    # Применяем сортировку
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    if request.user.is_authenticated:
        total_spending = calculate_total_spending(request.user)
    else:
        total_spending = 0
    discount_percentage = apply_discount(total_spending)
    context = {
        'products': products,
        'total_spending': total_spending,
        'discount_percentage': discount_percentage,
        'user_favorites': user_favorites,
        'discoun': discoun
    }

    return render(request, 'pagestore/homepage.html', context)


def apply_discount(total_spending):
    discount_percentage = 0  # Initialize the discount percentage
    if total_spending >= Decimal('1000.00'):
        discount_percentage = 10  # Set the discount percentage to 10% (adjust as needed)

    return discount_percentage


def calculate_total_spending(user):
    user_orders = Order.objects.filter(user=user)
    total_spending = sum(order.total_cost for order in user_orders)
    return total_spending


def signuppage(request):
    if request.method == 'POST':
        print("Received POST request")
        form = RegistrationForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            login(request, user)
            print("User saved and logged in")
            return redirect('homepage')
    else:
        print("Received GET request")
        form = RegistrationForm()
    return render(request, 'pagestore/signuppage.html', {'form': form})


def loginpage(request):
    if request.method == 'GET':
        return render(request, 'pagestore/loginpage.html', {'form': AuthorizationForm()})
    else:
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is None:
            return render(request, 'pagestore/loginpage.html', {'form': AuthorizationForm()})
        else:
            login(request, user)
            return redirect('homepage')


def logoutpage(request):
    if request.method == 'POST':
        logout(request)
        return redirect('homepage')


@login_required(login_url='loginpage')
def add_to_cart(request, product_id):
    if 'cart' not in request.session:
        request.session['cart'] = {}

    cart_items = request.session['cart']
    cart_items[str(product_id)] = cart_items.get(str(product_id), 0) + 1
    request.session.modified = True

    product = Product.objects.get(pk=product_id)
    product.quantity -= 1
    product.save()
 
    path = request.path
    print(path)
    if path == '/shop/':
        return redirect('shop')
    else:
        return redirect('homepage') 


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'pagestore/product_detail.html', {'product': product})


@login_required(login_url='loginpage')
def cart(request):
    cart_dict = request.session.get('cart', {})
    discoun = Discounted.objects.filter(user=request.user)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity_in_cart = cart_dict.get(str(product_id), 0)

        if quantity_in_cart > 0:
            # Удаляем товар из корзины
            cart_dict[str(product_id)] = quantity_in_cart - 1
            request.session['cart'] = cart_dict
            request.session.modified = True

            # Восстанавливаем количество доступных товаров
            product = Product.objects.get(pk=product_id)
            product.quantity += 1
            product.save()

            messages.success(request, f'Removed {product.name} from cart.')

    # Фильтрация товаров с нулевым количеством
    cart_items = []
    for product_id, quantity in cart_dict.items():
        product = get_object_or_404(Product, id=product_id)
        if quantity > 0:
            cart_items.append({'product': product, 'quantity_in_cart': quantity})

    total_cost = Decimal('0.00')
    for item in cart_items:
        item_total = item['product'].price * item['quantity_in_cart']
        total_cost += item_total

    # Применяем скидку
    discount = 0  # Скидка по умолчанию
    if discoun.exists():
        discount = discoun[0].discount  # Если есть скидка в базе данных

    discounted_total = total_cost - (total_cost * discount / 100)

    context = {'cart_items': cart_items, 'total_cost': total_cost, 'discount': discount, 'discounted_total': discounted_total}
    return render(request, 'pagestore/cart.html', context)


@login_required(login_url='loginpage')
def purchase_all(request):
    cart_dict = request.session.get('cart', {})
    total_cost = Decimal('0.00')

    if not cart_dict:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    for product_id, quantity in cart_dict.items():
        product = get_object_or_404(Product, id=product_id)

        if quantity > 0:
            item_cost = product.price * quantity
            total_cost += item_cost
            
    discount_percentage = apply_discount(total_cost)
    discount_percentage_decimal = Decimal(str(discount_percentage))
    total_cost_with_discount = total_cost - (total_cost * (discount_percentage_decimal / 100))

    phone = request.POST.get('phone')
    addres = request.POST.get('addres')
    payment = request.POST.get('payment')

    user = request.user
    order = Order.objects.create(user=user, total_cost=total_cost_with_discount, phone=phone, addres=addres, payment=payment)
    for product_id, quantity in cart_dict.items():
        product = get_object_or_404(Product, id=product_id)

        if quantity > 0:
            product.quantity - quantity
            product.save()
            order_item = OrderItem.objects.create(order=order, product=product, quantity=quantity)
    
    # email_subject = 'Новый заказ'
    # email_message = f'Новый заказ от {user}. Сумма заказа: ${total_cost_with_discount}\n\n'
    # email_message += f'Phone: {phone}\n'
    # email_message += f'Address: {addres}\n'
    # email_message += f'Payment Method: {payment}'
    
    # send_mail(email_subject, email_message, 'ToledoBilbao96@gmail.com', ['ToledoBilbao96@gmail.com'], fail_silently=False)

    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request,
                     f'You have successfully purchased all items in your cart. Total cost: ${total_cost_with_discount}')

    return redirect('homepage')


@login_required(login_url='loginpage')
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'pagestore/orders.html', {'user_orders': user_orders})


@login_required(login_url='loginpage')
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)  # Получаем все элементы заказа
    return render(request, 'pagestore/order_detail.html', {'order': order, 'order_items': order_items})



@login_required(login_url='loginpage')
def order_list(request):
    form = OrderFilterForm(request.GET)
    orders = Order.objects.all()

    if form.is_valid():
        sort_by = form.cleaned_data['sort_by']
        min_price = form.cleaned_data['min_price']
        max_price = form.cleaned_data['max_price']

        if sort_by == 'price_low_to_high':
            orders = orders.order_by('total_cost')
        elif sort_by == 'price_high_to_low':
            orders = orders.order_by('-total_cost')

        if min_price:
            orders = orders.filter(total_cost__gte=min_price)
        if max_price:
            orders = orders.filter(total_cost__lte=max_price)

    context = {
        'form': form,
        'orders': orders,
    }
    return render(request, 'order_list.html', context)


def apply_discount(total_spending):
    discount_percentage = 0  # Initialize the discount percentage
    if total_spending >= Decimal('5000.00'):
        discount_percentage = min(30, 10)

    return discount_percentage


@login_required(login_url='loginpage')
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user

    # Check if the product is already in the user's favorites
    favorites, created = Favorite.objects.get_or_create(user=user)
    favorites.products.add(product)

    return redirect('homepage')


@login_required(login_url='loginpage')
def favorite_products(request):
    user = request.user
    favorites, created = Favorite.objects.get_or_create(user=user)
    favorite_products = favorites.products.all()

    context = {
        'favorite_products': favorite_products,
    }

    return render(request, 'pagestore/favorites.html', context)


@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user

    # Check if the product is in the user's favorites
    favorites, created = Favorite.objects.get_or_create(user=user)
    if product in favorites.products.all():
        favorites.products.remove(product)

    return redirect('favorite_products')


@login_required
def toggle_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user = request.user

    # Get or create the user's favorites
    favorites, created = Favorite.objects.get_or_create(user=user)

    # Check if the product is in favorites
    if product in favorites.products.all():
        favorites.products.remove(product)
    else:
        favorites.products.add(product)

    return redirect('homepage')