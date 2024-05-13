from django.db import models

class Status(models.IntegerChoices):
    INACTIVE = 0, 'Inactive'
    ACTIVE = 1, 'Active'


class Group(models.Model):
    name = models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(choices=Status.choices, default=Status.ACTIVE)
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self) -> str:
        return self.name


class Competence(models.Model):    
    name = models.CharField(max_length=150)    
    competence_group = models.ForeignKey(Group,
                                         on_delete=models.CASCADE,
                                         blank=False,
                                         null=False,
                                         related_name='competence_group')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.BooleanField(choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['competence_group__name', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['competence_group', 'name']),
        ]

    def __str__(self) -> str:
        return self.name
