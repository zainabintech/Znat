# Generated by Django 4.2.11 on 2025-05-07 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_customuser_options_alter_customuser_role'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('can_view_admin_dashboard', 'Can view admin dashboard'), ('can_manage_courses', 'Can manage courses'), ('can_take_quizzes', 'Can take quizzes')]},
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('Admin', 'Admin'), ('Employee', 'Employee')], max_length=10),
        ),
    ]
