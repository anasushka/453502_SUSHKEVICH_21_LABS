from django.urls import path, re_path
from . import views

urlpatterns = [
    # Home
    re_path(r'^$', views.home, name='home'),

    # Static pages
    re_path(r'^about/$', views.about, name='about'),
    re_path(r'^glossary/$', views.glossary, name='glossary'),
    re_path(r'^contacts/$', views.contacts, name='contacts'),
    re_path(r'^privacy/$', views.privacy, name='privacy'),
    re_path(r'^vacancies/$', views.vacancies, name='vacancies'),
    re_path(r'^promos/$', views.promos, name='promos'),

    # News
    re_path(r'^news/$', views.news_list, name='news'),
    re_path(r'^news/(?P<pk>\d+)/$', views.news_detail, name='news_detail'),

    # Reviews
    re_path(r'^reviews/$', views.reviews_list, name='reviews'),

    # Services
    re_path(r'^services/$', views.services_list, name='services'),
    re_path(r'^services/(?P<pk>\d+)/$', views.service_detail, name='service_detail'),

    # Orders (CRUD)
    re_path(r'^orders/$', views.orders_list, name='orders'),
    re_path(r'^orders/create/$', views.order_create, name='order_create'),
    re_path(r'^orders/(?P<pk>\d+)/$', views.order_detail, name='order_detail'),
    re_path(r'^orders/(?P<pk>\d+)/edit/$', views.order_edit, name='order_edit'),
    re_path(r'^orders/(?P<pk>\d+)/delete/$', views.order_delete, name='order_delete'),

    # Auth / Profile
    re_path(r'^accounts/register/$', views.register, name='register'),
    re_path(r'^profile/$', views.profile, name='profile'),

    # Statistics (admin)
    re_path(r'^statistics/$', views.statistics_view, name='statistics'),

    # API endpoints
    re_path(r'^api/weather/$', views.api_weather, name='api_weather'),
    re_path(r'^api/geo/$', views.api_geo, name='api_geo'),
]
