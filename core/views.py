from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
import json
import datetime
from .forms import SignupForm
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages

from django.contrib.auth.decorators import login_required

from .models import *
from .forms import SignupForm
from .utils import cookieCart, cartData

# Create your views here.


def index(request):
    items = Product.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()
    data = cartData(request)
    cartItems = data['cartItems']
        
    products = Product.objects.all()
    context = {
        'products' :products,
        'cartItems' : cartItems,
        'items':items,
        'categories':categories,
        }
    return render(request, 'core/index.html', context)

@login_required(login_url='login')
def cart(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
                
    context={
        'items':items,
        'order':order,
        'cartItems' : cartItems
    }
    return render(request, 'core/cart.html', context)

def itemdetail( request, pk):
    items = get_object_or_404(Product, pk =pk)
    related_items = Product.objects.filter(category = items.category, is_sold=False).exclude(pk=pk)[0:3]
    data = cartData(request)
    order = data['order']
    cartItems = data['cartItems']
    
    context ={
        'items' : items,
        'cartItems' : cartItems,
        'order':order,
        'related_items': related_items,
    }
    return render(request, 'core/itemdetail.html', context)

@login_required(login_url='login')
def checkout(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
            
    context={
        'items':items,
        'order':order,
        'cartItems' : cartItems
    }
    return render(request, 'core/checkout.html', context)

def contact(request):
    context={}
    return render(request, 'core/contact.html', context)

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    print('Action:',action)
    print('productId:',productId)
    
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse('Item was added', safe=False)



@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        if order.shipping == True:
            ShippingAddress.objects.create(
                customer = customer,
                order = order,
                address = data['shipping']['address'],
                city = data['shipping']['city'],
                state = data['shipping']['state'],
                zipcode = data['shipping']['zipcode'],
                )
        
    else:
        print('User is not logged in...')
    return JsonResponse('Payment complete', safe=False)

@csrf_exempt
def SignupPage(request):
    
    form = SignupForm()
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            Customer.objects.create(user=user, name=user.username, email=user.email) 
            
            messages.success(request, 'Account was created ' )
            
            return redirect('login')
        
        
            
    context = {
        'form': form
    }
    return render (request, 'core/signup.html', context)

def LoginPage(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user=authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.info(request, 'Username or Password is incorrect')
            
        
        
    return render (request, 'core/login.html')

def logoutUser(request):
    logout(request)
    return redirect('index')