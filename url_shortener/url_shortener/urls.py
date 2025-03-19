"""
URL configuration for url_shortener project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import shorten_url_api, redirect_to_original, url_stats, home, register_view, login_view, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('shorten/', shorten_url_api, name='shorten_url_api'),
    path('stats/<str:short_code>/', url_stats, name='url_stats'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('<str:short_code>/', redirect_to_original, name='redirect_to_original'),
]
