from django.contrib import admin
from .models import Product, Order, OrderedProduct, OrderItem, Favorite, Discounted

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderedProduct)
admin.site.register(OrderItem)
admin.site.register(Favorite)
admin.site.register(Discounted)
