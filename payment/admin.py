from .models import ShippingAddress, Order, OrderIterm
from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .forms import ShippingForm


admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderIterm)


class OrderItemInline(admin.StackedInline):
    model = OrderIterm
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = [
        "user", "full_name", "email", "shipping_address",
        "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]


admin.site.unregister(Order)

admin.site.register(Order, OrderAdmin)
