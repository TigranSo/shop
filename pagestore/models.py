from _decimal import Decimal
from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    url = models.TextField(max_length=300, blank=True, null=True)
    photo = models.ImageField(upload_to='img', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=50, blank=True, null=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def discounted_price(self):
        discount = Decimal(self.discount_percentage) / Decimal(100)
        discounted_price = self.price - (self.price * discount)
        return discounted_price

    def __str__(self):
        return self.name


class Discounted(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.user} - {self.discount}'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50, blank=True, null=True)
    addres = models.CharField(max_length=100, blank=True, null=True)
    payment = models.CharField(max_length=50, blank=True, null=True)
    products = models.ManyToManyField(Product, related_name="orders")
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.products}'



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Добавляем поле product
    quantity = models.PositiveIntegerField(default=0)


class OrderedProduct(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)