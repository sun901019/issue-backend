from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0002_customerwarranty'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customerwarranty',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='customerwarranty',
            name='quantity',
        ),
        migrations.RemoveField(
            model_name='customerwarranty',
            name='serial_numbers',
        ),
    ]

