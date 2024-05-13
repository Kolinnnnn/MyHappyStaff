from django.contrib import admin
from .models import Account, Employer, Employee

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_employee', 'is_employer']
    ordering = ['user']


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ['company_name']
    search_fields = ['company_name']
    ordering = ['company_name']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['account']
