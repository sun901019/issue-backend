from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerWarranty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('hardware', '硬體'), ('software', '軟體')], max_length=20)),
                ('title', models.CharField(help_text='批次或保固描述，例如：主系統 + 3 感測器', max_length=255)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('serial_numbers', models.TextField(blank=True, help_text='序號或設備明細，多筆可換行')),
                ('notes', models.TextField(blank=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warranties', to='issues.customer')),
            ],
            options={
                'db_table': 'customer_warranties',
                'ordering': ['end_date', 'id'],
            },
        ),
        migrations.AddField(
            model_name='issue',
            name='warranty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='issues.customerwarranty'),
        ),
    ]

