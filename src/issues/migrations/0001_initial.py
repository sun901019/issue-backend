from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name='Project',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('code', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                        ('description', models.TextField(blank=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                    ],
                    options={
                        'db_table': 'projects',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Customer',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('code', models.CharField(blank=True, max_length=50, null=True, unique=True)),
                        ('contact_person', models.CharField(blank=True, max_length=100)),
                        ('contact_email', models.EmailField(blank=True, max_length=254)),
                        ('business_owner', models.CharField(blank=True, max_length=100, verbose_name='所屬業務')),
                        ('handover_completed', models.BooleanField(default=False, verbose_name='點交驗收完成')),
                        ('training_completed', models.BooleanField(default=False, verbose_name='教育訓練完成')),
                        ('internal_network_connected', models.BooleanField(default=False, verbose_name='接回內網')),
                        ('warranty_due', models.DateTimeField(blank=True, null=True, verbose_name='保固日期')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'db_table': 'customers',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Site',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('address', models.TextField(blank=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sites', to='issues.customer')),
                    ],
                    options={
                        'db_table': 'sites',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Asset',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('name', models.CharField(max_length=255)),
                        ('asset_code', models.CharField(blank=True, max_length=100)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='issues.site')),
                    ],
                    options={
                        'db_table': 'assets',
                        'ordering': ['name'],
                    },
                ),
                migrations.CreateModel(
                    name='Issue',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('title', models.CharField(max_length=255)),
                        ('description', models.TextField()),
                        ('category', models.CharField(max_length=100)),
                        ('priority', models.CharField(choices=[('Low', '低'), ('Medium', '中'), ('High', '高')], max_length=20)),
                        ('status', models.CharField(choices=[('Open', '待處理'), ('In Progress', '處理中'), ('Closed', '已完成'), ('Pending', '暫停')], default='Open', max_length=20)),
                        ('source', models.CharField(max_length=50)),
                        ('due_date', models.DateTimeField(blank=True, null=True)),
                        ('warranty_due', models.DateTimeField(blank=True, null=True)),
                        ('first_response_at', models.DateTimeField(blank=True, null=True)),
                        ('resolved_at', models.DateTimeField(blank=True, null=True)),
                        ('asset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='issues.asset')),
                        ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_issues', to=settings.AUTH_USER_MODEL)),
                        ('customer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='issues.customer')),
                        ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='issues.project')),
                        ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reported_issues', to=settings.AUTH_USER_MODEL)),
                        ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='issues', to='issues.site')),
                    ],
                    options={
                        'db_table': 'issues',
                        'ordering': ['-updated_at'],
                    },
                ),
                migrations.CreateModel(
                    name='IssueStatusHistory',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('from_status', models.CharField(max_length=20)),
                        ('to_status', models.CharField(max_length=20)),
                        ('changed_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                        ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='status_history', to='issues.issue')),
                        ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'issue_status_history',
                        'ordering': ['-changed_at'],
                    },
                ),
                migrations.CreateModel(
                    name='IssueComment',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('body', models.TextField()),
                        ('mentions', models.JSONField(blank=True, default=list)),
                        ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                        ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                        ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='issues.issue')),
                    ],
                    options={
                        'db_table': 'issue_comments',
                        'ordering': ['created_at'],
                    },
                ),
                migrations.CreateModel(
                    name='IssueAttachment',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('filename', models.CharField(max_length=255)),
                        ('file', models.FileField(blank=True, max_length=500, null=True, upload_to='attachments/%Y/%m/%d/')),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='issues.issue')),
                        ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='uploaded_attachments', to=settings.AUTH_USER_MODEL)),
                    ],
                    options={
                        'db_table': 'issue_attachments',
                        'ordering': ['-created_at'],
                    },
                ),
                migrations.CreateModel(
                    name='IssueSubtask',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title', models.CharField(max_length=255)),
                        ('status', models.CharField(choices=[('Open', '待處理'), ('In Progress', '處理中'), ('Closed', '已完成')], default='Open', max_length=20)),
                        ('due_date', models.DateTimeField(blank=True, null=True)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                        ('assignee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                        ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subtasks', to='issues.issue')),
                    ],
                    options={
                        'db_table': 'issue_subtasks',
                        'ordering': ['created_at'],
                    },
                ),
                migrations.CreateModel(
                    name='IssueRelation',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('relation_type', models.CharField(choices=[('relates', '相關'), ('duplicates', '重複'), ('blocks', '阻擋'), ('is_blocked_by', '被阻擋')], max_length=20)),
                        ('created_at', models.DateTimeField(auto_now_add=True)),
                        ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='relations', to='issues.issue')),
                        ('related_issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reverse_relations', to='issues.issue')),
                    ],
                    options={
                        'db_table': 'issue_relations',
                        'unique_together': {('issue', 'related_issue', 'relation_type')},
                    },
                ),
            ],
        ),
    ]

