"""
Issue serializers.
"""

from rest_framework import serializers
from .models import (
    Issue, IssueComment, IssueAttachment,
    IssueSubtask, IssueRelation, IssueStatusHistory,
    Customer,
)


class IssueSerializer(serializers.ModelSerializer):
    """Issue 基本序列化器"""
    
    assignee_name = serializers.CharField(source='assignee.username', read_only=True)
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_warranty_due = serializers.DateTimeField(source='customer.warranty_due', read_only=True, allow_null=True)
    
    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'category', 'priority', 'status', 'source',
            'project', 'project_name', 'customer', 'customer_name', 'site', 'asset',
            'assignee', 'assignee_name', 'reporter', 'reporter_name',
            'due_date', 'warranty_due', 'first_response_at', 'resolved_at',
            'customer_warranty_due',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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


class CustomerSerializer(serializers.ModelSerializer):
    """客戶序列化器"""
    
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'code', 'contact_person', 'contact_email',
            'business_owner',
            'handover_completed', 'training_completed', 'internal_network_connected',
            'warranty_due',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
    
    class Meta(IssueSerializer.Meta):
        fields = IssueSerializer.Meta.fields + [
            'subtasks', 'relations', 'comments', 'status_history', 'attachments_count',
        ]

