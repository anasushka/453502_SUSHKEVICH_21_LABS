import re
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import (
    Client, Employee, Order, OrderService,
    Review, Service, Specialization
)


def validate_phone(value):
    pattern = r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$'
    if not re.match(pattern, value):
        raise ValidationError('Номер телефона должен быть в формате: +375 (29) XXX-XX-XX')


def validate_adult_date(value):
    today = timezone.now().date()
    age = (today - value).days // 365
    if age < 18:
        raise ValidationError('Возраст должен быть 18 лет и старше.')


class ClientRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50, label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    last_name = forms.CharField(
        max_length=50, label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    phone = forms.CharField(
        max_length=20, label='Телефон',
        validators=[validate_phone],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+375 (29) XXX-XX-XX',
            'pattern': r'\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}',
            'required': 'required'
        })
    )
    birth_date = forms.DateField(
        label='Дата рождения',
        validators=[validate_adult_date],
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'required'})
    )
    address = forms.CharField(
        max_length=300, label='Адрес',
        widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'required'})
    )
    company_name = forms.CharField(
        max_length=200, label='Название компании', required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    client_type = forms.ChoiceField(
        label='Тип клиента',
        choices=Client.CLIENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Client.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                birth_date=self.cleaned_data['birth_date'],
                address=self.cleaned_data['address'],
                company_name=self.cleaned_data.get('company_name', ''),
                client_type=self.cleaned_data['client_type'],
            )
        return user


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['address', 'scheduled_date', 'notes']
        widgets = {
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'minlength': '5'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        labels = {
            'address': 'Адрес выполнения работ',
            'scheduled_date': 'Дата проведения работ',
            'notes': 'Примечания',
        }

    def clean_scheduled_date(self):
        date = self.cleaned_data.get('scheduled_date')
        if date and date < timezone.now().date():
            raise ValidationError('Дата не может быть в прошлом.')
        return date


class OrderServiceForm(forms.ModelForm):
    class Meta:
        model = OrderService
        fields = ['service', 'quantity']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100',
                'required': 'required'
            }),
        }
        labels = {
            'service': 'Услуга',
            'quantity': 'Количество',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_active=True)


OrderServiceFormSet = forms.inlineformset_factory(
    Order, OrderService,
    form=OrderServiceForm,
    extra=1, can_delete=True, min_num=1, validate_min=True
)


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'minlength': '2'
            }),
            'rating': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'required': 'required',
                'minlength': '10'
            }),
        }
        labels = {
            'name': 'Ваше имя',
            'rating': 'Оценка',
            'text': 'Текст отзыва',
        }


class ServiceFilterForm(forms.Form):
    search = forms.CharField(
        required=False, label='Поиск',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по названию...'})
    )
    service_type = forms.ModelChoiceField(
        queryset=None, required=False, label='Тип услуги',
        empty_label='Все типы',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False, label='Цена от',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
    max_price = forms.DecimalField(
        required=False, label='Цена до',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'})
    )
    sort_by = forms.ChoiceField(
        required=False, label='Сортировка',
        choices=[
            ('name', 'По названию (А-Я)'),
            ('-name', 'По названию (Я-А)'),
            ('price', 'По цене (возр.)'),
            ('-price', 'По цене (убыв.)'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        from .models import ServiceType
        super().__init__(*args, **kwargs)
        self.fields['service_type'].queryset = ServiceType.objects.all()


class OrderFilterForm(forms.Form):
    search = forms.CharField(
        required=False, label='Поиск',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск...'})
    )
    status = forms.ChoiceField(
        required=False, label='Статус',
        choices=[('', 'Все статусы')] + Order.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        required=False, label='Сортировка',
        choices=[
            ('-created_at', 'Дата (новые)'),
            ('created_at', 'Дата (старые)'),
            ('-total_price', 'Стоимость (убыв.)'),
            ('total_price', 'Стоимость (возр.)'),
            ('scheduled_date', 'Дата работ'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
