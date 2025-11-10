"""
Settings URLs.
"""

from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('dictionaries/', views.DictionaryListView.as_view(), name='dictionaries'),
    path('dictionaries/<str:dict_type>/', views.DictionaryListView.as_view(), name='dictionary-detail'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
]

