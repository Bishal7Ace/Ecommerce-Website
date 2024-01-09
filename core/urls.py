from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('',views.index, name='index'),
    path('cart/',views.cart, name="cart"),
    path('<int:pk>/',views.itemdetail, name="itemdetail"),
    path('checkout/',views.checkout,name='checkout'),
    path('contact/',views.contact,name='contact'),
    
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    
    path('signup/',views.SignupPage,name='signup'),
    path('login/',views.LoginPage,name='login'),
    path('logout/', views.logoutUser,name='logout')
    
    
    
]
