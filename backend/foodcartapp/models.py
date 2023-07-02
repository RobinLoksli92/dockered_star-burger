from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import F, Sum
from django.utils import timezone

from geo_location.models import GeoLocation


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )
    geo_location = models.ForeignKey(
        GeoLocation,
        related_name='restaurants_locations',
        verbose_name='Координаты ресторана',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):

    def calculate_orders_price(self):
        return self.annotate(
            total_price=Sum(F('items__quantity') * F('items__price'))
        )

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Необработанный'),
        ('preparing', 'Готовится'),
        ('delivering', 'В доставке'),
        ('ready', 'Выполнен')
    ]
    firstname = models.CharField('Имя', max_length=50)
    lastname = models.CharField('Фамилия', max_length=50)
    phonenumber = PhoneNumberField('Номер телефона', db_index=True)
    address = models.CharField('Адрес', max_length=100)

    status = models.CharField(
        'Статус',
        max_length=10,
        default='new',
        choices=STATUS_CHOICES,
        db_index=True
    )

    comment = models.TextField('Комментарий', blank=True)
    registrated_at = models.DateTimeField('Создан в', default=timezone.now)
    called_at = models.DateTimeField('Время звонка', blank=True, null=True)
    delivered_at = models.DateTimeField(
        'Время доставки',
        blank=True,
        null=True
    )

    payment_type = models.CharField(
        'Способ оплаты',
        max_length=10,
        choices=[
            ('cash', 'Наличные'),
            ('online', 'Оплата онлайн')
        ],
        blank=True,
        db_index=True
    )

    confirmed_restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        verbose_name='Ресторан, готовящий заказ',
        related_name='orders',
        blank=True,
        null=True
    )

    geo_location = models.ForeignKey(
        GeoLocation,
        related_name='customers_locations',
        verbose_name='Координаты заказчика',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.id}'


class OrderingProduct(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='ordering_products'
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказанные товары',
        related_name='items'
    )
    quantity = models.IntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f'{self.product}'
