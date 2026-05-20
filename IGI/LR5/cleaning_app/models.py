import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone


phone_regex = RegexValidator(
    regex=r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$',
    message="Номер телефона должен быть в формате: '+375 (29) XXX-XX-XX'"
)


def validate_adult(value):
    today = timezone.now().date()
    age = (today - value).days // 365
    if age < 18:
        raise ValidationError('Возраст должен быть 18 лет и старше.')


class Specialization(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')

    class Meta:
        verbose_name = 'Специализация'
        verbose_name_plural = 'Специализации'
        ordering = ['name']

    def __str__(self):
        return self.name


class ServiceType(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    icon = models.CharField(max_length=50, default='🧹', verbose_name='Иконка')

    class Meta:
        verbose_name = 'Тип услуги'
        verbose_name_plural = 'Типы услуг'
        ordering = ['name']

    def __str__(self):
        return self.name


class Service(models.Model):
    # ForeignKey: много услуг — один тип
    service_type = models.ForeignKey(
        ServiceType, on_delete=models.CASCADE,
        related_name='services', verbose_name='Тип услуги'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0)], verbose_name='Цена (BYN)'
    )
    unit = models.CharField(max_length=50, default='услуга', verbose_name='Единица измерения')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['service_type', 'name']

    def __str__(self):
        return f'{self.name} — {self.price} BYN'


class Employee(models.Model):
    # OneToOneField: один пользователь — один профиль сотрудника
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='employee_profile', verbose_name='Пользователь'
    )
    # ForeignKey: много сотрудников — одна специализация
    specialization = models.ForeignKey(
        Specialization, on_delete=models.SET_NULL, null=True,
        related_name='employees', verbose_name='Специализация'
    )
    phone = models.CharField(validators=[phone_regex], max_length=20, verbose_name='Телефон')
    birth_date = models.DateField(validators=[validate_adult], verbose_name='Дата рождения')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    photo = models.ImageField(upload_to='employees/', blank=True, null=True, verbose_name='Фото')
    hire_date = models.DateField(default=datetime.date.today, verbose_name='Дата найма')
    position = models.CharField(max_length=200, default='Клинер', verbose_name='Должность')
    work_description = models.TextField(blank=True, verbose_name='Описание работ')
    email = models.EmailField(blank=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.position})'

    def age(self):
        return (timezone.now().date() - self.birth_date).days // 365


class Client(models.Model):
    CLIENT_TYPE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('legal', 'Юридическое лицо'),
    ]
    # OneToOneField: один пользователь — один профиль клиента
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='client_profile', verbose_name='Пользователь'
    )
    phone = models.CharField(validators=[phone_regex], max_length=20, verbose_name='Телефон')
    birth_date = models.DateField(validators=[validate_adult], verbose_name='Дата рождения')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    company_name = models.CharField(max_length=200, blank=True, verbose_name='Название компании')
    client_type = models.CharField(
        max_length=20, choices=CLIENT_TYPE_CHOICES,
        default='individual', verbose_name='Тип клиента'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.get_client_type_display()})'

    def age(self):
        return (timezone.now().date() - self.birth_date).days // 365


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждён'),
        ('in_progress', 'Выполняется'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    ]
    # ForeignKey: один клиент — много заказов
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='orders', verbose_name='Клиент'
    )
    # ForeignKey: один сотрудник — много заказов
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='orders', verbose_name='Сотрудник'
    )
    # ManyToManyField: заказ включает много услуг, услуга — в многих заказах
    services = models.ManyToManyField(
        Service, through='OrderService',
        related_name='orders', verbose_name='Услуги'
    )
    address = models.CharField(max_length=300, verbose_name='Адрес выполнения работ')
    scheduled_date = models.DateField(verbose_name='Дата проведения работ')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Статус'
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        default=0, verbose_name='Итоговая стоимость (BYN)'
    )
    notes = models.TextField(blank=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} — {self.client} ({self.get_status_display()})'

    def recalculate_total(self):
        total = sum(
            item.quantity * item.price
            for item in self.orderservice_set.all()
        )
        self.total_price = total
        self.save(update_fields=['total_price'])


class OrderService(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, verbose_name='Услуга')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Цена за единицу (BYN)'
    )

    class Meta:
        verbose_name = 'Услуга в заказе'
        verbose_name_plural = 'Услуги в заказе'
        unique_together = ('order', 'service')

    def __str__(self):
        return f'{self.service.name} × {self.quantity}'

    def subtotal(self):
        return self.quantity * self.price


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name='Код')
    description = models.TextField(verbose_name='Описание')
    discount_percent = models.PositiveIntegerField(
        validators=[MaxValueValidator(100)], verbose_name='Скидка %'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    valid_from = models.DateField(verbose_name='Действует с')
    valid_to = models.DateField(verbose_name='Действует до')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды и купоны'
        ordering = ['-valid_to']

    def __str__(self):
        return f'{self.code} (-{self.discount_percent}%)'

    def is_currently_valid(self):
        today = timezone.now().date()
        return self.is_active and self.valid_from <= today <= self.valid_to


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    # ForeignKey: клиент может оставить много отзывов
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE,
        related_name='reviews', verbose_name='Клиент'
    )
    name = models.CharField(max_length=100, verbose_name='Имя')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    text = models.TextField(verbose_name='Текст отзыва')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.name} ({self.rating}/5)'


class CompanyInfo(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    founded_year = models.IntegerField(verbose_name='Год основания')
    address = models.CharField(max_length=300, verbose_name='Адрес')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(validators=[phone_regex], max_length=20, verbose_name='Телефон')
    logo = models.ImageField(upload_to='company/', blank=True, null=True, verbose_name='Логотип')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Информация о компании'
        verbose_name_plural = 'Информация о компании'

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField(max_length=300, verbose_name='Заголовок')
    summary = models.CharField(max_length=500, verbose_name='Краткое содержание')
    content = models.TextField(verbose_name='Полное содержание')
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name='Изображение')
    is_published = models.BooleanField(default=True, verbose_name='Опубликована')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=500, verbose_name='Вопрос / Термин')
    answer = models.TextField(verbose_name='Ответ / Определение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Вопрос-ответ'
        verbose_name_plural = 'Словарь терминов и понятий'
        ordering = ['-created_at']

    def __str__(self):
        return self.question


class Vacancy(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название вакансии')
    description = models.TextField(verbose_name='Описание')
    requirements = models.TextField(verbose_name='Требования')
    salary_from = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Зарплата от (BYN)'
    )
    salary_to = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True, verbose_name='Зарплата до (BYN)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
