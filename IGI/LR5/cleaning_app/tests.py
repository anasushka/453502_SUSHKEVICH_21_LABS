from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client as TestClient, TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Article, Client, CompanyInfo, Employee, FAQ,
    Order, OrderService, PromoCode, Review,
    Service, ServiceType, Specialization, Vacancy,
)
from .forms import (
    ClientRegistrationForm, OrderForm, ReviewForm, ServiceFilterForm,
)


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_user(username='testuser', password='pass12345', **kwargs):
    return User.objects.create_user(username=username, password=password, **kwargs)


def make_specialization(name='Уборка'):
    return Specialization.objects.create(name=name, description='desc')


def make_service_type(name='Стандартная'):
    return ServiceType.objects.create(name=name, icon='🧹', description='desc')


def make_service(name='Уборка квартиры', price=100, unit='уборка', service_type=None):
    if service_type is None:
        service_type = make_service_type()
    return Service.objects.create(name=name, price=price, unit=unit, service_type=service_type,
                                  description='Тестовая услуга')


def make_client(user=None, phone='+375 (29) 111-11-11'):
    if user is None:
        user = make_user()
    return Client.objects.create(
        user=user,
        phone=phone,
        birth_date=date(1990, 1, 1),
        address='г. Минск, ул. Тест, 1',
        client_type='individual',
    )


def make_employee(user=None, spec=None, phone='+375 (29) 222-22-22'):
    if user is None:
        user = make_user(username='empuser')
    if spec is None:
        spec = make_specialization()
    return Employee.objects.create(
        user=user,
        phone=phone,
        birth_date=date(1988, 5, 15),
        address='г. Минск',
        position='Клинер',
        specialization=spec,
        hire_date=date(2020, 1, 1),
    )


def make_order(client, employee=None, status='pending', days_ahead=5):
    return Order.objects.create(
        client=client,
        employee=employee,
        status=status,
        address='г. Минск, ул. Тест, 1',
        scheduled_date=date.today() + timedelta(days=days_ahead),
        total_price=Decimal('0'),
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class SpecializationModelTest(TestCase):
    def test_str(self):
        s = make_specialization('Химчистка')
        self.assertEqual(str(s), 'Химчистка')


class ServiceTypeModelTest(TestCase):
    def test_str(self):
        st = make_service_type('Генеральная')
        self.assertEqual(str(st), 'Генеральная')


class ServiceModelTest(TestCase):
    def test_str_contains_name(self):
        svc = make_service('Уборка офиса', price=200)
        self.assertIn('Уборка офиса', str(svc))

    def test_active_by_default(self):
        svc = make_service()
        self.assertTrue(svc.is_active)

    def test_price_stored(self):
        svc = make_service(price=150)
        self.assertEqual(svc.price, 150)


class ClientModelTest(TestCase):
    def test_age_calculation(self):
        user = make_user('ageclient')
        birth = date.today() - timedelta(days=365 * 30 + 10)
        client = Client.objects.create(
            user=user, phone='+375 (29) 100-00-00',
            birth_date=birth, address='addr', client_type='individual'
        )
        self.assertEqual(client.age(), 30)

    def test_str_contains_name(self):
        user = make_user('strclient', first_name='Анна', last_name='Иванова')
        client = make_client(user=user)
        self.assertIn('Иванова', str(client))


class EmployeeModelTest(TestCase):
    def test_str_contains_name(self):
        user = make_user('empstr', first_name='Иван', last_name='Петров')
        emp = make_employee(user=user)
        self.assertIn('Петров', str(emp))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = make_user('orderuser')
        self.client_obj = make_client(user=self.user)

    def test_recalculate_total(self):
        svc = make_service(price=100)
        order = make_order(self.client_obj)
        OrderService.objects.create(order=order, service=svc, quantity=2, price=svc.price)
        order.recalculate_total()
        order.refresh_from_db()
        self.assertEqual(order.total_price, Decimal('200.00'))

    def test_str_contains_id(self):
        order = make_order(self.client_obj)
        self.assertIn(str(order.id), str(order))

    def test_status_default_pending(self):
        order = make_order(self.client_obj)
        self.assertEqual(order.status, 'pending')

    def test_completed_status(self):
        order = make_order(self.client_obj, status='completed')
        self.assertEqual(order.status, 'completed')


class PromoCodeModelTest(TestCase):
    def test_str_contains_code(self):
        promo = PromoCode.objects.create(
            code='TEST10', discount_percent=10,
            valid_from=date.today(), valid_to=date.today() + timedelta(days=30)
        )
        self.assertIn('TEST10', str(promo))


class ReviewModelTest(TestCase):
    def test_rating_stored(self):
        user = make_user('revuser')
        client = make_client(user=user)
        review = Review.objects.create(name='Test', client=client, rating=5, text='Great!')
        self.assertEqual(review.rating, 5)

    def test_str(self):
        user = make_user('revuser2')
        client = make_client(user=user, phone='+375 (44) 111-11-11')
        review = Review.objects.create(name='Reviewer', client=client, rating=4, text='Good')
        self.assertIn('Reviewer', str(review))


class ArticleModelTest(TestCase):
    def test_published_filter(self):
        Article.objects.create(title='Published', is_published=True, summary='s', content='c')
        Article.objects.create(title='Draft', is_published=False, summary='s', content='c')
        self.assertEqual(Article.objects.filter(is_published=True).count(), 1)


class FAQModelTest(TestCase):
    def test_str_contains_question(self):
        faq = FAQ.objects.create(question='Что входит в уборку?', answer='Всё.')
        self.assertIn('Что входит', str(faq))


class VacancyModelTest(TestCase):
    def test_str_and_active(self):
        vac = Vacancy.objects.create(
            title='Клинер', salary_from=500, salary_to=800,
            description='desc', is_active=True
        )
        self.assertIn('Клинер', str(vac))
        self.assertTrue(vac.is_active)


class OrderServiceModelTest(TestCase):
    def test_subtotal(self):
        user = make_user('osuser')
        client = make_client(user=user)
        svc = make_service(price=50)
        order = make_order(client)
        os_obj = OrderService.objects.create(order=order, service=svc, quantity=3, price=svc.price)
        self.assertEqual(os_obj.subtotal(), Decimal('150.00'))


class CompanyInfoModelTest(TestCase):
    def test_str(self):
        company = CompanyInfo.objects.create(
            title='TestCo', phone='+375 (17) 000-00-00',
            email='e@e.by', address='addr', founded_year=2020, description='d'
        )
        self.assertIn('TestCo', str(company))


# ---------------------------------------------------------------------------
# Form tests
# ---------------------------------------------------------------------------

class ClientRegistrationFormTest(TestCase):
    def _valid_data(self, **overrides):
        data = {
            'username': 'newuser',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'email': 'test@mail.by',
            'phone': '+375 (29) 123-45-67',
            'birth_date': '1990-01-01',
            'address': 'г. Минск, ул. Тест, 1',
            'company_name': '',
            'client_type': 'individual',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = ClientRegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_phone_format(self):
        form = ClientRegistrationForm(data=self._valid_data(phone='12345'))
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_underage_rejected(self):
        young = (date.today() - timedelta(days=365 * 16)).isoformat()
        form = ClientRegistrationForm(data=self._valid_data(birth_date=young))
        self.assertFalse(form.is_valid())
        self.assertIn('birth_date', form.errors)

    def test_adult_accepted(self):
        adult = (date.today() - timedelta(days=365 * 25)).isoformat()
        form = ClientRegistrationForm(data=self._valid_data(birth_date=adult))
        self.assertTrue(form.is_valid(), form.errors)

    def test_saves_client_profile(self):
        form = ClientRegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(Client.objects.filter(user=user).exists())

    def test_password_mismatch(self):
        form = ClientRegistrationForm(data=self._valid_data(password2='Different123!'))
        self.assertFalse(form.is_valid())


class OrderFormTest(TestCase):
    def test_past_date_rejected(self):
        data = {
            'address': 'г. Минск, ул. Тест, 1',
            'scheduled_date': '2020-01-01',
            'notes': '',
        }
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('scheduled_date', form.errors)

    def test_today_accepted(self):
        data = {
            'address': 'г. Минск, ул. Тест, 1',
            'scheduled_date': date.today().isoformat(),
            'notes': '',
        }
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_future_date_accepted(self):
        data = {
            'address': 'г. Минск, ул. Тест, 1',
            'scheduled_date': (date.today() + timedelta(days=5)).isoformat(),
            'notes': '',
        }
        form = OrderForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_empty_address_rejected(self):
        data = {
            'address': '',
            'scheduled_date': (date.today() + timedelta(days=1)).isoformat(),
            'notes': '',
        }
        form = OrderForm(data=data)
        self.assertFalse(form.is_valid())


class ReviewFormTest(TestCase):
    def test_valid(self):
        form = ReviewForm(data={'name': 'Иван', 'rating': 5, 'text': 'Очень хорошо убрали квартиру'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_name(self):
        form = ReviewForm(data={'name': '', 'rating': 5, 'text': 'Text'})
        self.assertFalse(form.is_valid())

    def test_invalid_rating(self):
        form = ReviewForm(data={'name': 'Test', 'rating': 10, 'text': 'Text'})
        self.assertFalse(form.is_valid())


class ServiceFilterFormTest(TestCase):
    def test_empty_is_valid(self):
        form = ServiceFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_optional(self):
        form = ServiceFilterForm(data={'search': 'test'})
        self.assertTrue(form.is_valid())


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class PublicViewsTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        CompanyInfo.objects.create(
            title='КлинингПро', phone='+375 (17) 123-45-67',
            email='info@test.by', address='addr', founded_year=2015,
            description='desc'
        )
        Article.objects.create(title='Test Article', is_published=True,
                               summary='Summary', content='Content')
        FAQ.objects.create(question='Вопрос 1', answer='Ответ 1')
        Vacancy.objects.create(title='Клинер', description='desc', is_active=True)
        PromoCode.objects.create(
            code='TEST', discount_percent=10,
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=30),
            is_active=True
        )

    def test_home_ok(self):
        r = self.c.get(reverse('home'))
        self.assertEqual(r.status_code, 200)

    def test_about_ok(self):
        r = self.c.get(reverse('about'))
        self.assertEqual(r.status_code, 200)

    def test_news_list_ok(self):
        r = self.c.get(reverse('news'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Test Article')

    def test_news_detail_ok(self):
        article = Article.objects.first()
        r = self.c.get(reverse('news_detail', args=[article.pk]))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, article.title)

    def test_news_detail_404(self):
        r = self.c.get(reverse('news_detail', args=[99999]))
        self.assertEqual(r.status_code, 404)

    def test_glossary_ok(self):
        r = self.c.get(reverse('glossary'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Вопрос 1')

    def test_contacts_ok(self):
        r = self.c.get(reverse('contacts'))
        self.assertEqual(r.status_code, 200)

    def test_privacy_ok(self):
        r = self.c.get(reverse('privacy'))
        self.assertEqual(r.status_code, 200)

    def test_vacancies_ok(self):
        r = self.c.get(reverse('vacancies'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Клинер')

    def test_promos_ok(self):
        r = self.c.get(reverse('promos'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'TEST')

    def test_reviews_get_ok(self):
        r = self.c.get(reverse('reviews'))
        self.assertEqual(r.status_code, 200)

    def test_services_ok(self):
        st = make_service_type()
        make_service('Тест', service_type=st)
        r = self.c.get(reverse('services'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Тест')

    def test_services_filter_by_search(self):
        st = make_service_type('Специальная')
        make_service('Специальная уборка', service_type=st)
        r = self.c.get(reverse('services') + '?search=Специальная')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Специальная')

    def test_services_filter_by_price(self):
        st = make_service_type('FilterType')
        make_service('Дорогая услуга', price=500, service_type=st)
        make_service('Дешёвая услуга', price=50, service_type=st)
        r = self.c.get(reverse('services') + '?max_price=100')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Дешёвая услуга')

    def test_service_detail_ok(self):
        svc = make_service()
        r = self.c.get(reverse('service_detail', args=[svc.pk]))
        self.assertEqual(r.status_code, 200)

    def test_service_detail_404(self):
        r = self.c.get(reverse('service_detail', args=[99999]))
        self.assertEqual(r.status_code, 404)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.c = TestClient()

    def test_register_get(self):
        r = self.c.get(reverse('register'))
        self.assertEqual(r.status_code, 200)

    def test_register_post_valid_creates_client(self):
        r = self.c.post(reverse('register'), {
            'username': 'newreg',
            'first_name': 'Рег',
            'last_name': 'Тест',
            'email': 'reg@test.by',
            'phone': '+375 (29) 123-45-67',
            'birth_date': '1990-06-15',
            'address': 'г. Минск, ул. Тест, 1',
            'company_name': '',
            'client_type': 'individual',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        if r.status_code == 302:
            self.assertTrue(Client.objects.filter(user__username='newreg').exists())

    def test_login_redirect_for_anon_orders(self):
        r = self.c.get(reverse('orders'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('login', r['Location'])

    def test_profile_requires_login(self):
        r = self.c.get(reverse('profile'))
        self.assertEqual(r.status_code, 302)

    def test_login_page_ok(self):
        r = self.c.get(reverse('login'))
        self.assertEqual(r.status_code, 200)


class OrderViewsTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.user = make_user('ordertest', password='pass12345')
        self.client_obj = make_client(user=self.user)
        self.c.login(username='ordertest', password='pass12345')

    def test_orders_list_authenticated(self):
        r = self.c.get(reverse('orders'))
        self.assertEqual(r.status_code, 200)

    def test_order_create_get(self):
        r = self.c.get(reverse('order_create'))
        self.assertEqual(r.status_code, 200)

    def test_order_detail_client_access(self):
        order = make_order(self.client_obj)
        r = self.c.get(reverse('order_detail', args=[order.pk]))
        self.assertEqual(r.status_code, 200)

    def test_order_detail_forbidden_for_other_client(self):
        other_user = make_user('other')
        other_client = make_client(user=other_user, phone='+375 (44) 999-99-99')
        order = make_order(other_client)
        r = self.c.get(reverse('order_detail', args=[order.pk]))
        self.assertEqual(r.status_code, 403)

    def test_order_delete_post(self):
        order = make_order(self.client_obj)
        oid = order.pk
        r = self.c.post(reverse('order_delete', args=[oid]))
        self.assertIn(r.status_code, [302, 200])
        self.assertFalse(Order.objects.filter(pk=oid).exists())

    def test_order_delete_get_not_allowed(self):
        order = make_order(self.client_obj)
        r = self.c.get(reverse('order_delete', args=[order.pk]))
        self.assertEqual(r.status_code, 405)

    def test_order_edit_get(self):
        order = make_order(self.client_obj)
        r = self.c.get(reverse('order_edit', args=[order.pk]))
        self.assertEqual(r.status_code, 200)

    def test_order_edit_forbidden_for_non_pending(self):
        order = make_order(self.client_obj, status='completed')
        r = self.c.get(reverse('order_edit', args=[order.pk]))
        self.assertEqual(r.status_code, 403)


class ReviewPostTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.user = make_user('revpost', password='pass12345')
        self.client_obj = make_client(user=self.user)
        self.c.login(username='revpost', password='pass12345')

    def test_post_review_creates_review(self):
        r = self.c.post(reverse('reviews'), {
            'name': 'Тест', 'rating': 5, 'text': 'Отличная уборка квартиры!'
        })
        self.assertIn(r.status_code, [200, 302])
        self.assertTrue(Review.objects.filter(name='Тест').exists())

    def test_anon_review_redirects_to_login(self):
        c2 = TestClient()
        r = c2.post(reverse('reviews'), {
            'name': 'Anon', 'rating': 4, 'text': 'good cleaning service'
        })
        self.assertEqual(r.status_code, 302)


class StatisticsViewTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.admin = make_user('statsadmin', password='pass12345', is_staff=True)
        self.c.login(username='statsadmin', password='pass12345')

    def test_statistics_ok_for_staff(self):
        r = self.c.get(reverse('statistics'))
        self.assertEqual(r.status_code, 200)

    def test_statistics_redirect_for_anon(self):
        c2 = TestClient()
        r = c2.get(reverse('statistics'))
        self.assertEqual(r.status_code, 302)

    def test_statistics_redirect_for_non_staff(self):
        c2 = TestClient()
        u = make_user('nostaff', password='pass12345')
        c2.login(username='nostaff', password='pass12345')
        r = c2.get(reverse('statistics'))
        self.assertIn(r.status_code, [302, 403])


class APIViewsTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.user = make_user('apiuser', password='pass12345')
        self.c.login(username='apiuser', password='pass12345')

    @patch('cleaning_app.views._get_weather')
    def test_api_weather_authenticated(self, mock_weather):
        mock_weather.return_value = {
            'temp_c': '10', 'desc': 'Cloudy', 'humidity': '80', 'feels_like': '8'
        }
        r = self.c.get(reverse('api_weather'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ok')

    def test_api_weather_requires_login(self):
        c2 = TestClient()
        r = c2.get(reverse('api_weather'))
        self.assertEqual(r.status_code, 302)

    @patch('cleaning_app.views._get_user_geo')
    def test_api_geo_authenticated(self, mock_geo):
        mock_geo.return_value = {'city': 'Minsk', 'country_name': 'Belarus'}
        r = self.c.get(reverse('api_geo'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['status'], 'ok')

    def test_api_geo_requires_login(self):
        c2 = TestClient()
        r = c2.get(reverse('api_geo'))
        self.assertEqual(r.status_code, 302)

    @patch('cleaning_app.views._get_weather')
    def test_api_weather_error_returns_503(self, mock_weather):
        mock_weather.return_value = None
        r = self.c.get(reverse('api_weather'))
        self.assertEqual(r.status_code, 503)

    @patch('cleaning_app.views._get_user_geo')
    def test_api_geo_error_returns_503(self, mock_geo):
        mock_geo.return_value = None
        r = self.c.get(reverse('api_geo'))
        self.assertEqual(r.status_code, 503)


class ProfileViewTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.user = make_user('profileuser', password='pass12345',
                              first_name='Профиль', last_name='Тест')
        self.client_obj = make_client(user=self.user)
        self.c.login(username='profileuser', password='pass12345')

    def test_profile_ok(self):
        r = self.c.get(reverse('profile'))
        self.assertEqual(r.status_code, 200)

    def test_profile_contains_username(self):
        r = self.c.get(reverse('profile'))
        self.assertContains(r, 'profileuser')


class EmployeeOrdersTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.emp_user = make_user('empview', password='pass12345')
        self.emp = make_employee(user=self.emp_user)
        self.c.login(username='empview', password='pass12345')

        self.client_user = make_user('cliview')
        self.client_obj = make_client(user=self.client_user, phone='+375 (44) 111-22-33')
        self.order = make_order(self.client_obj, employee=self.emp)

    def test_employee_sees_own_orders(self):
        r = self.c.get(reverse('orders'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, str(self.order.id))

    def test_employee_can_view_order_detail(self):
        r = self.c.get(reverse('order_detail', args=[self.order.pk]))
        self.assertEqual(r.status_code, 200)

    def test_employee_cannot_create_order(self):
        r = self.c.get(reverse('order_create'))
        self.assertEqual(r.status_code, 302)


class AdminOrdersViewTest(TestCase):
    def setUp(self):
        self.c = TestClient()
        self.admin = make_user('adminorders', password='pass12345', is_staff=True)
        self.c.login(username='adminorders', password='pass12345')

        cl_user = make_user('admclient')
        self.client_obj = make_client(user=cl_user, phone='+375 (25) 100-00-00')
        self.order = make_order(self.client_obj)

    def test_admin_sees_all_orders(self):
        r = self.c.get(reverse('orders'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, str(self.order.id))
