"""
Issue serializers.
"""

from typing import Optional

from rest_framework import serializers
from .models import (
    Issue,
    IssueComment,
    IssueAttachment,
    IssueSubtask,
    IssueRelation,
    IssueStatusHistory,
    Customer,
    CustomerWarranty,
)
from common.utils import (
    calculate_warranty_status,
    summarize_warranties,
    warranty_date_to_datetime,
)


class IssueSerializer(serializers.ModelSerializer):
    """Issue 基本序列化器"""
    
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_warranty_due = serializers.SerializerMethodField()
    warranty = serializers.PrimaryKeyRelatedField(
        queryset=CustomerWarranty.objects.all(),
        required=False,
        allow_null=True,
    )
    warranty_info = serializers.SerializerMethodField()
    hardware_warranty_status = serializers.SerializerMethodField()
    software_warranty_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'priority', 'status', 'source',
            'project', 'project_name', 'customer', 'customer_name', 'site', 'asset',
            'assignee', 'assignee_name', 'reporter', 'reporter_name',
            'due_date', 'warranty_due', 'first_response_at', 'resolved_at',
            'warranty', 'warranty_info',
            'hardware_warranty_status', 'software_warranty_status',
            'customer_warranty_due',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_customer_warranty_due(self, obj):
        customer = obj.customer
        if not customer:
            return None
        warranty = customer.warranties.filter(
            type=CustomerWarranty.TYPE_HARDWARE,
            end_date__isnull=False,
        ).order_by('end_date').first()
        if not warranty or not warranty.end_date:
            return None
        due_datetime = warranty_date_to_datetime(warranty.end_date)
        return due_datetime

    def get_warranty_info(self, obj):
        warranty = obj.warranty
        if not warranty:
            return None
        status = calculate_warranty_status(warranty.end_date)
        return {
            'id': warranty.id,
            'title': warranty.title,
            'type': warranty.type,
            'end_date': warranty.end_date,
            'status': status,
        }

    def validate(self, attrs):
        customer = attrs.get('customer') or getattr(self.instance, 'customer', None)
        warranty = attrs.get('warranty') or getattr(self.instance, 'warranty', None)

        if warranty and customer and warranty.customer_id != customer.id:
            raise serializers.ValidationError({
                'warranty': '選擇的保固不屬於該客戶。'
            })
        return super().validate(attrs)

    def _apply_warranty_due(self, issue: Issue, warranty: Optional[CustomerWarranty]):
        if warranty and warranty.end_date:
            issue.warranty_due = warranty_date_to_datetime(warranty.end_date)
        else:
            issue.warranty_due = None

    def create(self, validated_data):
        warranty = validated_data.get('warranty')
        issue = super().create(validated_data)
        self._apply_warranty_due(issue, warranty)
        issue.save(update_fields=['warranty_due'])
        return issue

    def _get_customer_warranties(self, obj: Issue, warranty_type: str):
        customer = obj.customer
        if not customer:
            return []

        warranties = getattr(customer, 'warranties', None)
        if warranties is None:
            return customer.warranties.filter(type=warranty_type)

        # QuerySet may already be evaluated (prefetched); filter in-memory to avoid extra queries
        if hasattr(warranties, 'all'):
            warranties = warranties.all()
        return [w for w in warranties if w.type == warranty_type]

    def get_hardware_warranty_status(self, obj):
        warranties = self._get_customer_warranties(obj, CustomerWarranty.TYPE_HARDWARE)
        summary = summarize_warranties(warranties)
        return summary.get('status')

    def get_software_warranty_status(self, obj):
        warranties = self._get_customer_warranties(obj, CustomerWarranty.TYPE_SOFTWARE)
        summary = summarize_warranties(warranties)
        return summary.get('status')

    def update(self, instance, validated_data):
        warranty = validated_data.get('warranty', instance.warranty)
        issue = super().update(instance, validated_data)
        self._apply_warranty_due(issue, warranty)
        issue.save(update_fields=['warranty_due'])
        return issue


class IssueSubtaskSerializer(serializers.ModelSerializer):
    """子任務序列化器"""
    
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    
    class Meta:
        model = IssueSubtask
        fields = ['id', 'title', 'status', 'assignee', 'assignee_name', 'due_date', 'created_at', 'updated_at']


class IssueRelationSerializer(serializers.ModelSerializer):
    """關聯序列化器"""
    
    related_issue_title = serializers.CharField(source='related_issue.title', read_only=True)
    
    class Meta:
        model = IssueRelation
        fields = ['id', 'related_issue', 'related_issue_title', 'relation_type', 'created_at']


class IssueCommentSerializer(serializers.ModelSerializer):
    """評論序列化器"""
    
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = IssueComment
        fields = ['id', 'author', 'author_name', 'body', 'mentions', 'created_at']


class CustomerWarrantySerializer(serializers.ModelSerializer):
    """客戶保固批次序列化器"""

    status = serializers.SerializerMethodField()
    type_label = serializers.SerializerMethodField()

    class Meta:
        model = CustomerWarranty
        fields = [
            'id', 'type', 'type_label', 'title',
            'end_date', 'notes',
            'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'type_label', 'status']

    def get_status(self, obj):
        return calculate_warranty_status(obj.end_date)

    def get_type_label(self, obj):
        return dict(CustomerWarranty.TYPE_CHOICES).get(obj.type, obj.type)


class CustomerSerializer(serializers.ModelSerializer):
    """客戶序列化器"""
    
    warranties = CustomerWarrantySerializer(many=True, required=False)
    hardware_summary = serializers.SerializerMethodField()
    software_summary = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'code', 'contact_person', 'contact_email',
            'business_owner',
            'handover_completed', 'training_completed', 'internal_network_connected',
            'warranty_due',  # Deprecated; 保留以維持兼容性
            'warranties',
            'hardware_summary', 'software_summary',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        warranties_data = validated_data.pop('warranties', [])
        customer = super().create(validated_data)
        self._sync_warranties(customer, warranties_data)
        return customer

    def update(self, instance, validated_data):
        warranties_data = validated_data.pop('warranties', None)
        customer = super().update(instance, validated_data)
        if warranties_data is not None:
            self._sync_warranties(customer, warranties_data)
        return customer

    def _sync_warranties(self, customer: Customer, warranties_data):
        existing_ids = []
        for data in warranties_data:
            warranty_id = data.get('id')
            fields = {
                'type': data.get('type', CustomerWarranty.TYPE_HARDWARE),
                'title': data.get('title', ''),
                'end_date': data.get('end_date'),
                'notes': data.get('notes', ''),
            }

            if warranty_id:
                warranty = customer.warranties.filter(id=warranty_id).first()
                if not warranty:
                    continue
                for attr, value in fields.items():
                    setattr(warranty, attr, value)
                warranty.save()
                existing_ids.append(warranty.id)
            else:
                warranty = customer.warranties.create(**fields)
                existing_ids.append(warranty.id)

        # 清除不在提交資料中的舊保固
        if existing_ids:
            customer.warranties.exclude(id__in=existing_ids).delete()
        else:
            customer.warranties.all().delete()

        # 更新舊欄位（取最近的硬體保固日期）
        earliest_hardware = customer.warranties.filter(
            type=CustomerWarranty.TYPE_HARDWARE,
            end_date__isnull=False,
        ).order_by('end_date').first()
        customer.warranty_due = warranty_date_to_datetime(
            earliest_hardware.end_date if earliest_hardware else None
        )
        customer.save(update_fields=['warranty_due'])

    def get_hardware_summary(self, obj):
        return summarize_warranties(
            list(obj.warranties.filter(type=CustomerWarranty.TYPE_HARDWARE))
        )

    def get_software_summary(self, obj):
        return summarize_warranties(
            list(obj.warranties.filter(type=CustomerWarranty.TYPE_SOFTWARE))
        )


class IssueStatusHistorySerializer(serializers.ModelSerializer):
    """狀態歷史序列化器"""
    
    changed_by_name = serializers.CharField(source='changed_by.username', read_only=True)
    
    class Meta:
        model = IssueStatusHistory
        fields = ['id', 'from_status', 'to_status', 'changed_at', 'changed_by', 'changed_by_name']


class IssueAttachmentSerializer(serializers.ModelSerializer):
    """附件序列化器"""
    
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_size = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = IssueAttachment
        fields = ['id', 'filename', 'file', 'file_size', 'file_url', 'uploaded_by', 'uploaded_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_file_size(self, obj):
        """取得檔案大小（KB）"""
        if obj.file:
            return round(obj.file.size / 1024, 2)
        return 0
    
    def get_file_url(self, obj):
        """取得檔案 URL"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class IssueDetailSerializer(IssueSerializer):
    """Issue 詳細序列化器（含活動、子任務、關聯、附件）"""
    
    subtasks = IssueSubtaskSerializer(many=True, read_only=True)
    relations = IssueRelationSerializer(many=True, read_only=True)
    comments = IssueCommentSerializer(many=True, read_only=True)
    status_history = IssueStatusHistorySerializer(many=True, read_only=True)
    attachments_count = serializers.IntegerField(source='attachments.count', read_only=True)
    hardware_warranties = serializers.SerializerMethodField()
    software_warranties = serializers.SerializerMethodField()
    
    class Meta(IssueSerializer.Meta):
        fields = IssueSerializer.Meta.fields + [
            'subtasks',
            'relations',
            'comments',
            'status_history',
            'attachments_count',
            'hardware_warranties',
            'software_warranties',
        ]

    def get_hardware_warranties(self, obj):
        warranties = self._get_customer_warranties(obj, CustomerWarranty.TYPE_HARDWARE)
        serializer = CustomerWarrantySerializer(warranties, many=True)
        return serializer.data

    def get_software_warranties(self, obj):
        warranties = self._get_customer_warranties(obj, CustomerWarranty.TYPE_SOFTWARE)
        serializer = CustomerWarrantySerializer(warranties, many=True)
        return serializer.data

