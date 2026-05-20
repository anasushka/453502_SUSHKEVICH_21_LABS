import calendar
import json
import logging
import statistics
from datetime import date

import requests
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count, Sum, Q
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import (
    ClientRegistrationForm, OrderFilterForm, OrderForm,
    OrderServiceFormSet, ReviewForm, ServiceFilterForm,
)
from .models import (
    Article, Client, CompanyInfo, Employee, FAQ,
    Order, OrderService, PromoCode, Review, Service, ServiceType, Vacancy,
)

logger = logging.getLogger('cleaning_app')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_calendar_text(year=None, month=None):
    now = timezone.localtime(timezone.now())
    year = year or now.year
    month = month or now.month
    cal = calendar.TextCalendar(calendar.MONDAY)
    return cal.formatmonth(year, month)


def _utc_and_local_now():
    utc_now = timezone.now()
    local_now = timezone.localtime(utc_now)
    return utc_now, local_now


def _common_context():
    utc_now, local_now = _utc_and_local_now()
    return {
        'utc_now': utc_now,
        'local_now': local_now,
        'calendar_text': _get_calendar_text(),
        'current_date': local_now.strftime('%d/%m/%Y'),
        'timezone_name': timezone.get_current_timezone_name(),
    }


def _get_weather():
    from django.conf import settings
    try:
        resp = requests.get(settings.WEATHER_API_URL, timeout=5)
        data = resp.json()
        current = data.get('current_condition', [{}])[0]
        return {
            'temp_c': current.get('temp_C', 'N/A'),
            'desc': current.get('weatherDesc', [{}])[0].get('value', 'N/A'),
            'humidity': current.get('humidity', 'N/A'),
            'feels_like': current.get('FeelsLikeC', 'N/A'),
        }
    except Exception as exc:
        logger.warning('Weather API error: %s', exc)
        return None


def _get_user_geo(request):
    from django.conf import settings
    try:
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', ''))
        if ',' in ip:
            ip = ip.split(',')[0].strip()
        if ip in ('127.0.0.1', 'localhost', '::1', ''):
            ip = '8.8.8.8'
        url = settings.IP_API_URL.format(ip=ip)
        resp = requests.get(url, timeout=5)
        return resp.json()
    except Exception as exc:
        logger.warning('IP API error: %s', exc)
        return None


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

def home(request):
    latest_article = Article.objects.filter(is_published=True).first()
    company = CompanyInfo.objects.first()
    weather = _get_weather()
    geo = _get_user_geo(request)
    ctx = {**_common_context(), 'latest_article': latest_article,
           'company': company, 'weather': weather, 'geo': geo}
    logger.info('Home page visited by %s', request.user)
    return render(request, 'cleaning_app/home.html', ctx)


def about(request):
    company = CompanyInfo.objects.first()
    ctx = {**_common_context(), 'company': company}
    return render(request, 'cleaning_app/about.html', ctx)


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    ctx = {**_common_context(), 'articles': articles}
    return render(request, 'cleaning_app/news.html', ctx)


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    ctx = {**_common_context(), 'article': article}
    return render(request, 'cleaning_app/news_detail.html', ctx)


def glossary(request):
    faqs = FAQ.objects.all()
    ctx = {**_common_context(), 'faqs': faqs}
    return render(request, 'cleaning_app/glossary.html', ctx)


def contacts(request):
    employees = Employee.objects.filter(is_active=True).select_related('user', 'specialization')
    ctx = {**_common_context(), 'employees': employees}
    return render(request, 'cleaning_app/contacts.html', ctx)


def privacy(request):
    ctx = _common_context()
    return render(request, 'cleaning_app/privacy.html', ctx)


def vacancies(request):
    vacs = Vacancy.objects.filter(is_active=True)
    ctx = {**_common_context(), 'vacancies': vacs}
    return render(request, 'cleaning_app/vacancies.html', ctx)


def reviews_list(request):
    reviews = Review.objects.select_related('client__user').all()
    form = ReviewForm()
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.warning(request, 'Для добавления отзыва необходимо войти в систему.')
            return redirect('login')
        client = _get_client(request.user)
        if not client:
            messages.error(request, 'Только клиенты могут оставлять отзывы.')
            return redirect('reviews')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.client = client
            review.save()
            messages.success(request, 'Ваш отзыв успешно добавлен!')
            logger.info('Review added by client %s', client)
            return redirect('reviews')
    ctx = {**_common_context(), 'reviews': reviews, 'form': form}
    return render(request, 'cleaning_app/reviews.html', ctx)


def promos(request):
    today = date.today()
    active_promos = PromoCode.objects.filter(
        is_active=True, valid_from__lte=today, valid_to__gte=today
    )
    archive_promos = PromoCode.objects.filter(
        Q(is_active=False) | Q(valid_to__lt=today)
    )
    ctx = {**_common_context(), 'active_promos': active_promos, 'archive_promos': archive_promos}
    return render(request, 'cleaning_app/promos.html', ctx)


# ---------------------------------------------------------------------------
# Services (CRUD)
# ---------------------------------------------------------------------------

def services_list(request):
    form = ServiceFilterForm(request.GET or None)
    qs = Service.objects.filter(is_active=True).select_related('service_type')

    search = request.GET.get('search', '')
    stype = request.GET.get('service_type', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    sort_by = request.GET.get('sort_by', 'name')

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if stype:
        qs = qs.filter(service_type_id=stype)
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except ValueError:
            pass
    if sort_by in ('name', '-name', 'price', '-price'):
        qs = qs.order_by(sort_by)

    service_types = ServiceType.objects.all()
    ctx = {**_common_context(), 'services': qs, 'form': form, 'service_types': service_types}
    return render(request, 'cleaning_app/services.html', ctx)


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    ctx = {**_common_context(), 'service': service}
    return render(request, 'cleaning_app/service_detail.html', ctx)


# ---------------------------------------------------------------------------
# Orders (CRUD — login required)
# ---------------------------------------------------------------------------

def _get_client(user):
    try:
        return user.client_profile
    except Client.DoesNotExist:
        return None


def _get_employee(user):
    try:
        return user.employee_profile
    except Employee.DoesNotExist:
        return None


@login_required
def orders_list(request):
    form = OrderFilterForm(request.GET or None)
    if request.user.is_staff:
        qs = Order.objects.select_related('client__user', 'employee__user').all()
    elif _get_employee(request.user):
        employee = _get_employee(request.user)
        qs = Order.objects.filter(employee=employee).select_related('client__user')
    elif _get_client(request.user):
        client = _get_client(request.user)
        qs = Order.objects.filter(client=client).select_related('employee__user')
    else:
        return HttpResponseForbidden('Профиль не найден.')

    status = request.GET.get('status', '')
    search = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', '-created_at')

    if status:
        qs = qs.filter(status=status)
    if search:
        qs = qs.filter(
            Q(address__icontains=search) |
            Q(client__user__first_name__icontains=search) |
            Q(client__user__last_name__icontains=search)
        )
    allowed_sorts = ('-created_at', 'created_at', '-total_price', 'total_price', 'scheduled_date')
    if sort_by in allowed_sorts:
        qs = qs.order_by(sort_by)

    ctx = {**_common_context(), 'orders': qs, 'form': form}
    return render(request, 'cleaning_app/orders.html', ctx)


@login_required
def order_create(request):
    client = _get_client(request.user)
    if not client:
        messages.error(request, 'Только клиенты могут создавать заказы.')
        return redirect('services')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()
            formset = OrderServiceFormSet(request.POST, instance=order)
            if formset.is_valid():
                instances = formset.save(commit=False)
                for inst in instances:
                    inst.price = inst.service.price
                    inst.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                order.recalculate_total()
                messages.success(request, f'Заказ #{order.id} успешно создан!')
                logger.info('Order #%s created by client %s', order.id, client)
                return redirect('order_detail', pk=order.pk)
            else:
                order.delete()
        else:
            formset = OrderServiceFormSet(request.POST)
    else:
        form = OrderForm()
        formset = OrderServiceFormSet()

    ctx = {**_common_context(), 'form': form, 'formset': formset, 'title': 'Создать заказ'}
    return render(request, 'cleaning_app/order_form.html', ctx)


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not _can_access_order(request.user, order):
        return HttpResponseForbidden('Доступ запрещён.')
    order_services = order.orderservice_set.select_related('service').all()
    ctx = {**_common_context(), 'order': order, 'order_services': order_services}
    return render(request, 'cleaning_app/order_detail.html', ctx)


@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not _can_edit_order(request.user, order):
        return HttpResponseForbidden('Доступ запрещён.')

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderServiceFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            form.save()
            instances = formset.save(commit=False)
            for inst in instances:
                inst.price = inst.service.price
                inst.save()
            for obj in formset.deleted_objects:
                obj.delete()
            order.recalculate_total()
            messages.success(request, 'Заказ успешно обновлён.')
            logger.info('Order #%s updated', order.pk)
            return redirect('order_detail', pk=order.pk)
    else:
        form = OrderForm(instance=order)
        formset = OrderServiceFormSet(instance=order)

    ctx = {**_common_context(), 'form': form, 'formset': formset, 'order': order, 'title': 'Редактировать заказ'}
    return render(request, 'cleaning_app/order_form.html', ctx)


@login_required
@require_http_methods(['POST'])
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if not _can_edit_order(request.user, order):
        return HttpResponseForbidden('Доступ запрещён.')
    order_id = order.id
    order.delete()
    messages.success(request, f'Заказ #{order_id} удалён.')
    logger.info('Order #%s deleted', order_id)
    return redirect('orders')


def _can_access_order(user, order):
    if user.is_staff:
        return True
    client = _get_client(user)
    if client and order.client == client:
        return True
    employee = _get_employee(user)
    if employee and order.employee == employee:
        return True
    return False


def _can_edit_order(user, order):
    if user.is_staff:
        return True
    client = _get_client(user)
    if client and order.client == client and order.status == 'pending':
        return True
    return False


# ---------------------------------------------------------------------------
# Auth / Profile
# ---------------------------------------------------------------------------

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
            logger.info('New client registered: %s', user.username)
            return redirect('profile')
    else:
        form = ClientRegistrationForm()
    ctx = {**_common_context(), 'form': form}
    return render(request, 'cleaning_app/register.html', ctx)


@login_required
def profile(request):
    client = _get_client(request.user)
    employee = _get_employee(request.user)
    recent_orders = None
    if client:
        recent_orders = Order.objects.filter(client=client).order_by('-created_at')[:5]
    elif employee:
        recent_orders = Order.objects.filter(employee=employee).order_by('-created_at')[:5]
    ctx = {**_common_context(), 'client': client, 'employee': employee, 'recent_orders': recent_orders}
    return render(request, 'cleaning_app/profile.html', ctx)


# ---------------------------------------------------------------------------
# Statistics (admin only)
# ---------------------------------------------------------------------------

@staff_member_required
def statistics_view(request):
    completed_orders = Order.objects.filter(status='completed')
    prices = list(completed_orders.values_list('total_price', flat=True))
    prices_float = [float(p) for p in prices]

    stats = {}
    if prices_float:
        stats['mean_price'] = round(statistics.mean(prices_float), 2)
        stats['median_price'] = round(statistics.median(prices_float), 2)
        try:
            stats['mode_price'] = round(statistics.mode(prices_float), 2)
        except statistics.StatisticsError:
            stats['mode_price'] = 'Нет моды'
        stats['total_revenue'] = round(sum(prices_float), 2)
    else:
        stats['mean_price'] = stats['median_price'] = stats['mode_price'] = 0
        stats['total_revenue'] = 0

    clients = Client.objects.all()
    ages = [c.age() for c in clients]
    if ages:
        stats['avg_client_age'] = round(statistics.mean(ages), 1)
        stats['median_client_age'] = round(statistics.median(ages), 1)
    else:
        stats['avg_client_age'] = stats['median_client_age'] = 0

    popular = (
        Service.objects
        .annotate(order_count=Count('orders'))
        .order_by('-order_count')
        .first()
    )
    stats['most_popular_service'] = popular

    profitable_type = (
        ServiceType.objects
        .annotate(revenue=Sum('services__orders__total_price'))
        .order_by('-revenue')
        .first()
    )
    stats['most_profitable_type'] = profitable_type

    services_alpha = (
        Service.objects
        .annotate(order_count=Count('orders'))
        .order_by('name')
    )

    clients_spending = (
        Client.objects
        .annotate(total_spent=Sum('orders__total_price'))
        .order_by('user__last_name')
    )

    status_data = list(
        Order.objects.values('status').annotate(cnt=Count('id')).order_by('status')
    )
    status_labels_map = dict(Order.STATUS_CHOICES)
    status_labels = [status_labels_map.get(d['status'], d['status']) for d in status_data]
    status_counts = [d['cnt'] for d in status_data]

    type_revenue_qs = list(
        ServiceType.objects
        .annotate(revenue=Sum('services__orders__total_price'))
        .values('name', 'revenue')
        .order_by('name')
    )
    type_labels = [d['name'] for d in type_revenue_qs]
    type_revenues = [float(d['revenue'] or 0) for d in type_revenue_qs]

    ctx = {
        **_common_context(),
        'stats': stats,
        'services_alpha': services_alpha,
        'clients_spending': clients_spending,
        'status_labels': json.dumps(status_labels, ensure_ascii=False),
        'status_counts': json.dumps(status_counts),
        'type_labels': json.dumps(type_labels, ensure_ascii=False),
        'type_revenues': json.dumps(type_revenues),
        'total_orders': Order.objects.count(),
        'total_clients': Client.objects.count(),
        'total_services': Service.objects.filter(is_active=True).count(),
    }
    return render(request, 'cleaning_app/statistics.html', ctx)


# ---------------------------------------------------------------------------
# API endpoints (require login — restrict for unauthorized)
# ---------------------------------------------------------------------------

@login_required
def api_weather(request):
    data = _get_weather()
    if data:
        return JsonResponse({'status': 'ok', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Не удалось получить данные о погоде'}, status=503)


@login_required
def api_geo(request):
    data = _get_user_geo(request)
    if data:
        return JsonResponse({'status': 'ok', 'data': data})
    return JsonResponse({'status': 'error', 'message': 'Не удалось определить геолокацию'}, status=503)
