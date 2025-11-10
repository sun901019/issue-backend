"""
Reports URLs.
"""

from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.DashboardSummaryView.as_view(), name='dashboard'),
    path('summary/', views.ReportSummaryView.as_view(), name='summary'),
    path('trend/', views.ReportTrendView.as_view(), name='trend'),
    path('dimensions/', views.ReportDimensionsView.as_view(), name='dimensions'),
]

