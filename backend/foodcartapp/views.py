from django.http import JsonResponse
from django.templatetags.static import static
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer, ListField

from geo_location.models import GeoLocation

from .models import Product, Order, OrderingProduct
from geo_location.views import fetch_coordinates


class OrderingProductSerializer(ModelSerializer):
    class Meta:
        model = OrderingProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = ListField(
        child=OrderingProductSerializer(),
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'products',
            'firstname', 'lastname',
            'phonenumber', 'address'
        ]


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    ordering_product = serializer.validated_data

    geo_location, is_created = GeoLocation.objects.get_or_create(
        address=ordering_product['address'],
    )

    if is_created:
        customer_coords = fetch_coordinates(
            settings.YANDEX_APIKEY,
            ordering_product['address']
        )
        if customer_coords:
            geo_location.long, geo_location.lat = customer_coords
            geo_location.save()

    order = Order.objects.create(
        firstname=ordering_product['firstname'],
        lastname=ordering_product['lastname'],
        phonenumber=ordering_product['phonenumber'],
        address=ordering_product['address'],
        geo_location=geo_location
    )

    ordering_products = [
        OrderingProduct(
            product=product['product'],
            order=order,
            quantity=product['quantity'],
            price=Product.objects.get(name=product['product']).price
        )
        for product in ordering_product['products']
    ]
    OrderingProduct.objects.bulk_create(ordering_products)

    return Response(serializer.data)
