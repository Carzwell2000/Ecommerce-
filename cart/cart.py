from main.models import Product, Profile


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.request = request
        cart = self.session.get('session_key')
        if not cart:
            cart = self.session['session_key'] = {}
        self.cart = cart

    def db_add(self, product, quantity):

        product_id = str(product)
        quantity = int(quantity)

        if product_id in self.cart:
            self.cart[product_id] += quantity  # increase existing quantity
        else:
            self.cart[product_id] = quantity

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))

    def add(self, product, quantity):
        product_id = str(product.id)
        quantity = int(quantity)

        if product_id in self.cart:
            self.cart[product_id] += quantity  # increase existing quantity
        else:
            self.cart[product_id] = quantity

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))

    def update(self, product, quantity):
        product_id = str(product)
        quantity = int(quantity)
        update_quantity = self.cart
        update_quantity[product_id] = quantity

        self.session.modified = True
        thing = self.cart

        if self.request.user.is_authenticated:
            current_user = Profile.objects.filter(
                user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))
        return thing

    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session.modified = True
            if self.request.user.is_authenticated:
                current_user = Profile.objects.filter(
                    user__id=self.request.user.id)
                carty = str(self.cart)
                carty = carty.replace("\'", "\"")
                current_user.update(old_cart=str(carty))

    def cart_total(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        quantities = self.cart
        total = 0
        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total += product.sale_price * value
                    else:
                        total += product.price * value
        return total

    def __len__(self):
        return sum(self.cart.values())

    def get_prods(self):
        product_ids = self.cart.keys()
        return Product.objects.filter(id__in=product_ids)

    def get_quants(self):
        return self.cart
