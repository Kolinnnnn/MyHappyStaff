# Generated by Django 4.2.9 on 2024-01-19 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('competence', '0001_initial'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='competences',
            field=models.ManyToManyField(blank=True, related_name='competence_joined', to='competence.competence'),
        ),
    ]
