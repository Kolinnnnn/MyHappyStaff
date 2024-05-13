from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from competence.models import Competence

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_employee = models.BooleanField(default=True, blank=False)
    is_employer = models.BooleanField(default=False, blank=False)

    def __str__(self) -> str:
        return f'{self.user.username}'


class Employee(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    address = models.CharField(max_length=250, blank=False, null=False)
    post_code = models.CharField(max_length=6, blank=False, null=False)
    city = models.CharField(max_length=150, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(_('active'), default=True)
    competences = models.ManyToManyField(Competence,
                                         related_name='competence_joined',
                                         blank=True)
    description = models.TextField(blank=True, null=True)
    belbin_test_result = models.CharField(max_length=10, blank=False, default='N/A', null=False)

    def get_absolute_url(self):
        return reverse("employee-update", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        u = self.account.user
        return u.first_name + ' ' + u.last_name


class Employer(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=250, 
                                    unique=True,
                                    blank=False, 
                                    null=False)
    address = models.CharField(max_length=250, blank=False, null=False)
    post_code = models.CharField(max_length=6, blank=False, null=False)
    city = models.CharField(max_length=150, blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['company_name']),
        ]

    def __str__(self) -> str:
        return self.company_name


class Project(models.Model):
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, blank=False, null=False)
    title = models.CharField(max_length=150, blank=False, null=False)
    code = models.CharField(max_length=30, blank=False, null=False, unique=True)
    description = models.TextField(blank=True, null=True)
    competences = models.ManyToManyField(Competence,
                                         related_name='project_competence_joined',
                                         blank=True)
    employees = models.ManyToManyField(Employee, related_name='projects', blank=True)
    
    class Meta:
        ordering = ['code']
        indexes = [
            models.Index(fields=['code'])
        ]

    def get_absolute_url(self):
        return reverse("project-list")

    def __str__(self) -> str:
        return self.title    
