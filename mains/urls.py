from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from mains import views

urlpatterns = [
    path('api/v1/', views.api_root),
    path('api/v1/profiles/', views.profile_list, name='profile-list'),
    path('api/v1/profiles/<str:pk>/',
         views.ProfileDetail.as_view(), name='profile-detail'),
    path('api/v1/profiles/<str:profile_pk>/addresses/',
         views.address_list, name='address-list'),
    path('api/v1/profiles/<str:profile_pk>/addresses/<str:address_pk>/',
         views.AddressDetail.as_view(), name='address-detail'),
    path('api/v1/profiles/<str:profile_pk>/jobs/',
         views.JobList.as_view(), name='job-list'),
    path('api/v1/profiles/<str:profile_pk>/jobs/<str:job_pk>/',
         views.JobDetail.as_view(), name='job-detail'),
    path('api/v1/profiles/<str:profile_pk>/educations/',
         views.EducationList.as_view(), name='education-list'),
    path('api/v1/profiles/<str:profile_pk>/educations/<str:edu_pk>/',
         views.EducationDetail.as_view(), name='education-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
