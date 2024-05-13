from django.contrib import admin
from .models import Group, Competence

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'status']
    list_filter = ['name', 'status']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'competence_group', 'status']
    list_filter = ['name', 'status']
    raw_id_fields = ['competence_group']
    search_fields = ['name']
    ordering = ['competence_group', 'name']
