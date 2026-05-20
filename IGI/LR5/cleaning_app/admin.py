from django.contrib import admin
from .models import (
    Article, Client, CompanyInfo, Employee, FAQ,
    Order, OrderService, PromoCode, Review,
    Service, ServiceType, Specialization, Vacancy,
)


@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(ServiceType)
class ServiceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'description')
    search_fields = ('name',)


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ('name', 'price', 'unit', 'is_active')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'price', 'unit', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'service_type')
    search_fields = ('name', 'description')
    list_editable = ('is_active', 'price')
    ordering = ('service_type', 'name')
    date_hierarchy = 'created_at'


class OrderServiceInline(admin.TabularInline):
    model = OrderService
    extra = 1
    fields = ('service', 'quantity', 'price')
    readonly_fields = ()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'employee', 'status', 'total_price', 'scheduled_date', 'created_at', 'updated_at')
    list_filter = ('status', 'scheduled_date', 'employee')
    search_fields = ('client__user__last_name', 'client__user__first_name', 'address')
    list_editable = ('status',)
    inlines = [OrderServiceInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Основное', {
            'fields': ('client', 'employee', 'status', 'address', 'scheduled_date')
        }),
        ('Финансы', {
            'fields': ('total_price', 'notes')
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'specialization', 'phone', 'hire_date', 'is_active')
    list_filter = ('is_active', 'specialization')
    search_fields = ('user__last_name', 'user__first_name', 'phone', 'position')
    list_editable = ('is_active',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_type', 'phone', 'company_name', 'created_at')
    list_filter = ('client_type',)
    search_fields = ('user__last_name', 'user__first_name', 'phone', 'company_name')
    date_hierarchy = 'created_at'


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_from', 'valid_to')
    list_filter = ('is_active',)
    search_fields = ('code', 'description')
    list_editable = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'client', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('name', 'text')
    date_hierarchy = 'created_at'


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'email', 'phone', 'founded_year', 'updated_at')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'summary', 'content')
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'created_at')
    search_fields = ('question', 'answer')
    date_hierarchy = 'created_at'


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'salary_from', 'salary_to', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
