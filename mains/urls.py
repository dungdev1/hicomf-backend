from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from mains import views

urlpatterns = [
    path('', views.api_root),
    path('profiles/', views.profile_list, name='profile-list'),
    path('profiles/<str:pk>/', views.profile_detail, name='profile-detail'),
    path('addresses/', views.address_list, name='address-list'),
    path('addresses/<str:pk>/', views.address_detail, name='address-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)