"""
Issue URLs.
"""

from django.urls import path
from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.IssueListView.as_view(), name='list'),
    path('batch-update/', views.IssueBatchUpdateView.as_view(), name='batch-update'),
    path('import/', views.IssueImportView.as_view(), name='import'),
    path('export/', views.IssueExportView.as_view(), name='export'),
    path('<int:pk>/', views.IssueDetailView.as_view(), name='detail'),
    path('<int:pk>/status/', views.IssueStatusUpdateView.as_view(), name='status-update'),
    path('<int:pk>/comments/', views.IssueCommentView.as_view(), name='comments'),
    path('<int:pk>/comments/<int:comment_id>/', views.IssueCommentDetailView.as_view(), name='comment-detail'),
    path('<int:pk>/relations/', views.IssueRelationView.as_view(), name='relations'),
    path('<int:pk>/relations/<int:relation_id>/', views.IssueRelationDetailView.as_view(), name='relation-detail'),
    path('<int:pk>/attachments/', views.IssueAttachmentView.as_view(), name='attachments'),
    path('<int:pk>/attachments/<int:attachment_id>/', views.IssueAttachmentView.as_view(), name='attachment-detail'),
]

