from operator import itemgetter
from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from geopy import distance

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    new_orders = Order.objects.filter(status='new').calculate_orders_price()

    restaurants_items = {}
    for restaurant in Restaurant.objects.prefetch_related('menu_items'):
        restaurant_items = set()
        restaurant_items = {item.product for item in restaurant.menu_items.all()}
        restaurants_items[restaurant] = restaurant_items
    
    for order in new_orders:
        customer_coords = order.geo_location.lat, order.geo_location.long
        relevant_restaurants = []
        ordering_products = set()
        ordering_products = {product.product for product in order.items.all()}
        
        for restaurant, restaurant_items in restaurants_items.items():

            if ordering_products.issubset(restaurant_items):
                
                restaurant_coords = (
                    restaurant.geo_location.lat,
                    restaurant.geo_location.long
                )
                restaurant.distance = distance.distance(
                    restaurant_coords,
                    customer_coords).km
                
                relevant_restaurants.append(
                    (restaurant, restaurant.distance)
                )   

        order.relevant_restaurants = sorted(
            relevant_restaurants,
            key=itemgetter(1)
        )

    return render(request, template_name='order_items.html', context={
        "orders": new_orders,
    })
