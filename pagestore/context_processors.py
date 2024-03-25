from .models import OrderItem, Order, Product, Favorite
from _decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404

def cart_items(request):
    cart_dict = request.session.get('cart', {})
    cart_count = sum(cart_dict.values())

    # Calculate the total cost
    total_cost = Decimal('0.00')
    for product_id, quantity in cart_dict.items():
        product = get_object_or_404(Product, id=product_id)
        total_cost += product.price * quantity

    return {'cart_count': cart_count, 'total_cost': total_cost}


def favorite(request):
    if request.user.is_authenticated:
        user = request.user
        favorites, created = Favorite.objects.get_or_create(user=user)
        favorite_products = favorites.products.all()
    else:
        favorite_products = []

    return {'favorite_products': favorite_products}


