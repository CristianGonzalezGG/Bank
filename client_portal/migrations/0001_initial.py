# Generated by Django 5.0.4 on 2025-03-12 16:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('blog', '0007_twofactorcode'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_type', models.CharField(choices=[('SAVINGS', 'Cuenta de Ahorros'), ('CHECKING', 'Cuenta Corriente'), ('FIXED', 'Depósito a Plazo Fijo'), ('SALARY', 'Cuenta Sueldo')], max_length=20)),
                ('initial_deposit', models.DecimalField(decimal_places=2, max_digits=10)),
                ('status', models.CharField(choices=[('PENDING', 'Pendiente'), ('APPROVED', 'Aprobada'), ('REJECTED', 'Rechazada')], default='PENDING', max_length=20)),
                ('reason', models.TextField(blank=True, help_text='Razón por la que desea abrir esta cuenta')),
                ('advisor_notes', models.TextField(blank=True, help_text='Notas del asesor (solo visibles para asesores)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='account_requests', to='blog.client')),
                ('processed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='processed_accounts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_type', models.CharField(choices=[('ACCOUNT_OPENING', 'Apertura de Cuenta'), ('LOAN_REQUEST', 'Solicitud de Préstamo'), ('FINANCIAL_ADVICE', 'Asesoría Financiera'), ('CARD_REQUEST', 'Solicitud de Tarjeta'), ('OTHER', 'Otro')], max_length=20)),
                ('preferred_date', models.DateField()),
                ('preferred_time', models.TimeField()),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pendiente'), ('APPROVED', 'Aprobada'), ('REJECTED', 'Rechazada'), ('CANCELLED', 'Cancelada'), ('COMPLETED', 'Completada')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('advisor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_appointments', to=settings.AUTH_USER_MODEL)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_requests', to='blog.client')),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('CLIENT', 'Cliente'), ('ADVISOR', 'Asesor'), ('MANAGER', 'Gerente')], default='CLIENT', max_length=20)),
                ('client', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blog.client')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
