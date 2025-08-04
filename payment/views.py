from django.shortcuts import render, redirect
from cart.cart import Cart
from django.contrib import messages
# Create your views here.
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderIterm
from django.contrib.auth.models import User
from main.models import Product


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
        shipping_address = f"{my_shipping['shipping_address1']}\n {my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_state']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
            create_order = Order(user=user, full_name=full_name,
                                 email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            # CORRECTION: Remove the parentheses from cart_products
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # CORRECTION: Remove the parentheses from quantities
                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderIterm(
                            order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "order placed")
            return redirect('home')
        else:

            create_order = Order(full_name=full_name,
                                 email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            order_id = create_order.pk
            # CORRECTION: Remove the parentheses from cart_products
            for product in cart_products:
                product_id = product.id
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price
                # CORRECTION: Remove the parentheses from quantities
                for key, value in quantities.items():
                    if int(key) == product.id:
                        create_order_item = OrderIterm(
                            order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "order placed")
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
        if request.user.is_authenticated:
            billing_form = PaymentForm()
            return render(request, 'billing_info.html', {
                'cart_products': cart_products,
                'quantities': quantities,
                'totals': totals,
                'shipping_info': request.POST,
                'billing_form': billing_form
            })
        else:
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
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(
            request.POST or None, instance=shipping_user)

        return render(request, 'checkout.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form
        })
    else:
        shipping_form = ShippingForm(
            request.POST or None)
        return render(request, 'checkout.html', {
            'cart_products': cart_products,
            'quantities': quantities,
            'totals': totals,
            'shipping_form': shipping_form
        })
