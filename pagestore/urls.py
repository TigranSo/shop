from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    # Home
    path('', views.homepage, name='homepage'),
    path('shop/', views.shop, name='shop'),
    # Auth
    path('signup/', views.signuppage, name='signuppage'),
    path('login/', views.loginpage, name='loginpage'),
    path('logout/', views.logoutpage, name='logoutpage'),
    # Cart
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('purchase_all/', views.purchase_all, name='purchase_all'),
    path('orders/', views.orders, name='orders'),
    path('order_list/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    #Fav
    path('add_to_favorites/<str:product_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/', views.favorite_products, name='favorite_products'),
    path('remove_from_favorites/<str:product_id>/', views.remove_from_favorites, name='remove_from_favorites'),
    path('toggle_favorites/<int:product_id>/', views.toggle_favorites, name='toggle_favorites'),
]