from cart.cart import Cart
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Category, Customer, Order, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, UpdatePasswordForm, UserInfoForm
from django import forms
from django.db.models import Q
import json
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.views.decorators.csrf import csrf_protect


def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    return render(request, 'home.html', {
        'products': products,
        'categories': categories,
    })


def about(request):
    categories = Category.objects.all()
    return render(request, 'about.html', {'categories': categories})


def product(request, pk):
    categories = Category.objects.all()
    product = get_object_or_404(Product, id=pk)
    extra_images = product.images.all()
    return render(request, 'product.html', {
        'product': product,
        'extra_images': extra_images,
        'categories': categories,
    })


def category_view(request, slug):
    try:
        category = Category.objects.get(slug=slug)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {
            'products': products,
            'categories': Category.objects.all(),
        })
    except Category.DoesNotExist:
        messages.error(request, "That category doesn't exist.")
        return redirect('home')


@csrf_protect
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            current_user, created = Profile.objects.get_or_create(user=user)
            saved_cart = current_user.old_cart

            if saved_cart:
                converted_cart = json.loads(saved_cart)
                cart = Cart(request)
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, 'You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)

            messages.success(request, "Registration successful.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please try again.")
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})


def contact(request):
    categories = Category.objects.all()
    return render(request, 'contact.html', {'categories': categories})


def update_user(request):
    if request.user.is_authenticated:
        current_user = request.user
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if request.method == 'POST' and user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "Profile updated successfully.")
            return redirect('home')

        return render(request, 'update_user.html', {'user_form': user_form})
    else:
        messages.error(
            request, "You must be logged in to update your profile.")
        return redirect('login')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        if request.method == 'POST':
            form = UpdatePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Password updated successfully.")
                login(request, current_user)
                return redirect('home')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = UpdatePasswordForm(current_user)
        return render(request, 'update_password.html', {'form': form})
    else:
        messages.error(
            request, "You must be logged in to update your password.")
        return redirect('login')


def update_info(request):
    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)
        shipping, _ = ShippingAddress.objects.get_or_create(user=request.user)

        form = UserInfoForm(request.POST or None, instance=profile)
        shipping_form = ShippingForm(request.POST or None, instance=shipping)

        if request.method == 'POST' and form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Info updated successfully.")
            return redirect('home')

        return render(request, 'update_info.html', {
            'form': form,
            'shipping_form': shipping_form
        })
    else:
        messages.error(
            request, "You must be logged in to update your profile.")
        return redirect('home')


def search(request):
    if request.method == "POST":
        query = request.POST.get('searched', '')
        results = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query))
        if not results.exists():
            messages.success(
                request, "We don't have that product. Please search again.")
        return render(request, 'search.html', {'searched': results})
    return render(request, 'search.html')
