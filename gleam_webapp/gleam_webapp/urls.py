"""gleam_webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from candidate_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.home_page, name='home_page'),
    path('observation_create/', views.observation_create),
    path('candidate_create/', views.candidate_create),
    path('token_manage/', views.token_manage, name='token_manage'),
    path('token_create/', views.token_create),
    path('candidate_rating/<int:id>/', views.candidate_rating, name='candidate_rating'),
    path('candidate_rating/random/', views.candidate_random, name='candidate_random'),
    path('candidate_update_rating/<int:id>/', views.candidate_update_rating, name='candidate_update_rating'),
    path('candidate_update_simbad/<int:id>/', views.candidate_update_simbad, name='candidate_update_simbad'),
    path('candidate_table/', views.candidate_table),
    path('survey_status/', views.survey_status),
]

# allow media files to be linked and viewed directly
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)