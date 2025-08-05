from django.shortcuts import render, redirect
from cart.cart import Cart
from django.contrib import messages
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderIterm
from main.models import Product, Profile
import datetime


def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderIterm.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            if status == "true":
                order = Order.objects.filter(id=pk)
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                order = Order.objects.filter(id=pk)

                order.update(shipped=False)
            messages.success(request, "delivered")
            return redirect('home')
        return render(request, "orders.html", {'order': order, 'items': items})

    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def not_shipped(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)

        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            orders = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            orders.update(shipped=True, date_shipped=now)
            messages.success(request, "delivered")
            return redirect('home')

        return render(request, "not_shipped.html", {'orders': orders})
    else:

        messages.success(request, "Access Denied")
        return redirect('home')


def shipped(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            orders = Order.objects.filter(id=num)
            now = datetime.datetime.now()
            orders.update(shipped=False)
            messages.success(request, "delivered")
            return redirect('home')
        return render(request, "shipped.html", {'orders': orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def process_order(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get('my_shipping')

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id = create_order.pk

            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                if str(product_id) in quantities:
                    create_order_item = OrderIterm(
                        order_id=order_id,
                        product_id=product_id,
                        user=user,
                        quantity=quantities[str(product_id)],
                        price=price
                    )
                    create_order_item.save()

        else:
            create_order = Order(full_name=full_name, email=email,
                                 shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            order_id = create_order.pk

            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price
                if str(product_id) in quantities:
                    create_order_item = OrderIterm(
                        order_id=order_id,
                        product_id=product_id,
                        quantity=quantities[str(product_id)],
                        price=price
                    )
                    create_order_item.save()

        # Clear cart
        if "session_key" in request.session:
            del request.session["session_key"]

        current_user = Profile.objects.filter(user__id=request.user.id)
        current_user.update(old_cart="")
        messages.success(request, "Order placed")
        return redirect('home')
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_total()

        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        billing_form = PaymentForm()

        return render(request, 'billing_info.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_info': request.POST,
            'billing_form': billing_form
        })
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def payment_success(request):
    return render(request, "payment_success.html", {})


def payment_cancel(request):
    return render(request, "payment_cancel.html", {})


def payment_error(request):
    return render(request, "payment_error.html", {})


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_total()

    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(
                user__id=request.user.id)
            shipping_form = ShippingForm(
                request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            shipping_form = ShippingForm(request.POST or None)
    else:
        shipping_form = ShippingForm(request.POST or None)

    return render(request, 'checkout.html', {
        'cart_products': cart_products,
        'quantities': quantities,
        'totals': totals,
        'shipping_form': shipping_form
    })
