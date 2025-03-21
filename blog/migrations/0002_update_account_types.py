from django.db import migrations, models

def update_old_account_types(apps, schema_editor):
    Account = apps.get_model('blog', 'Account')
    # Actualizar todas las cuentas existentes de tipo 'SAVINGS' a 'SAVINGS_NORMAL'
    Account.objects.filter(account_type='SAVINGS').update(account_type='SAVINGS_NORMAL')

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),  # Asegúrate de que este sea el nombre de tu migración inicial
    ]

    operations = [
        # Primero actualizamos el campo con las nuevas opciones
        migrations.AlterField(
            model_name='account',
            name='account_type',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('SAVINGS_NORMAL', 'Cuenta de Ahorros Normal'),
                    ('SAVINGS_NOMINA', 'Cuenta Nómina'),
                    ('SAVINGS_AMIGA', 'Cuenta Amiga'),
                    ('CHECKING', 'Cuenta Corriente'),
                    ('FIXED', 'Depósito a Plazo Fijo'),
                ],
            ),
        ),
        # Luego ejecutamos la función para actualizar los datos existentes
        migrations.RunPython(update_old_account_types, reverse_code=migrations.RunPython.noop),
    ] 