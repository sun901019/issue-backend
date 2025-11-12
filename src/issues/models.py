"""
Issue models.
"""

from django.db import models
from django.contrib.auth.models import User
from common.models import TimestampedModel


class Project(models.Model):
    """專案"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'projects'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Customer(models.Model):
    """客戶"""
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # 新增字段
    business_owner = models.CharField(max_length=100, blank=True, verbose_name='所屬業務')
    handover_completed = models.BooleanField(default=False, verbose_name='點交驗收完成')
    training_completed = models.BooleanField(default=False, verbose_name='教育訓練完成')
    internal_network_connected = models.BooleanField(default=False, verbose_name='接回內網')
    warranty_due = models.DateTimeField(null=True, blank=True, verbose_name='保固日期')  # TODO: Deprecated, kept for backward compatibility
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerWarranty(TimestampedModel):
    """客戶保固批次"""

    TYPE_HARDWARE = 'hardware'
    TYPE_SOFTWARE = 'software'
    TYPE_CHOICES = [
        (TYPE_HARDWARE, '硬體'),
        (TYPE_SOFTWARE, '軟體'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='warranties')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, help_text='批次或保固描述，例如：主系統 + 3 感測器')
    end_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'customer_warranties'
        ordering = ['end_date', 'id']

    def __str__(self):
        return f"{self.customer.name} - {self.title}"


class Site(models.Model):
    """場域"""
    name = models.CharField(max_length=255)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sites')
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sites'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.customer.name} - {self.name}"


class Asset(models.Model):
    """資產/設備"""
    name = models.CharField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='assets')
    asset_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'assets'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Issue(TimestampedModel):
    """問題/Issue"""
    
    PRIORITY_CHOICES = [
        ('Low', '低'),
        ('Medium', '中'),
        ('High', '高'),
    ]
    
    STATUS_CHOICES = [
        ('Open', '待處理'),
        ('In Progress', '處理中'),
        ('Closed', '已完成'),
        ('Pending', '暫停'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=100)  # 字典表：設備/系統/系統功能/網路/其他
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    source = models.CharField(max_length=50)  # 字典表：業務回報/現場發現/自主發現/業主回報/Line/Email/電話
    
    # 外鍵關聯
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    
    # 人員
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_issues')
    reporter = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reported_issues')
    
    # 日期
    due_date = models.DateTimeField(null=True, blank=True)
    warranty_due = models.DateTimeField(null=True, blank=True)
    first_response_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    warranty = models.ForeignKey(CustomerWarranty, on_delete=models.SET_NULL, null=True, blank=True, related_name='issues')
    
    class Meta:
        db_table = 'issues'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['status', '-updated_at']),
            models.Index(fields=['project', 'created_at']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['assignee', 'status']),
        ]
    
    def __str__(self):
        return self.title


class IssueStatusHistory(models.Model):
    """狀態變更歷史"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='status_history')
    from_status = models.CharField(max_length=20)
    to_status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True, db_index=True)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'issue_status_history'
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['issue', '-changed_at']),
        ]
    
    def __str__(self):
        return f"{self.issue.title} - {self.from_status} → {self.to_status}"


class IssueComment(models.Model):
    """評論"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    body = models.TextField()
    mentions = models.JSONField(default=list, blank=True)  # @mention 使用者 ID 列表
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'issue_comments'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['issue', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comment on {self.issue.title}"


class IssueCommentAttachment(models.Model):
    """評論附件"""
    comment = models.ForeignKey(IssueComment, on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='comment_attachments/%Y/%m/%d/', max_length=500)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_comment_attachments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'issue_comment_attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename


class IssueAttachment(models.Model):
    """附件"""
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='attachments')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='attachments/%Y/%m/%d/', max_length=500, null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_attachments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'issue_attachments'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.filename


class IssueSubtask(models.Model):
    """子任務"""
    STATUS_CHOICES = [
        ('Open', '待處理'),
        ('In Progress', '處理中'),
        ('Closed', '已完成'),
    ]
    
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    assignee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'issue_subtasks'
        ordering = ['created_at']
    
    def __str__(self):
        return self.title


class IssueRelation(models.Model):
    """Issue 關聯"""
    RELATION_TYPES = [
        ('relates', '相關'),
        ('duplicates', '重複'),
    ]
    
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='relations')
    related_issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='reverse_relations')
    relation_type = models.CharField(max_length=20, choices=RELATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'issue_relations'
        unique_together = ['issue', 'related_issue', 'relation_type']
    
    def __str__(self):
        return f"{self.issue.title} {self.get_relation_type_display()} {self.related_issue.title}"

