"""
Common URLs.
"""

from django.urls import path
from . import views

app_name = 'common'

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('customers/', views.CustomerListView.as_view(), name='customer-list'),
    path('customers/<int:pk>/', views.CustomerDetailView.as_view(), name='customer-detail'),
]

