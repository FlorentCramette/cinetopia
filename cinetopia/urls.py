"""
URL configuration for cinetopia project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from myapp_cinetopia import views
from myapp_cinetopia.weather_api import weather_api
from myapp_cinetopia.search_api import search_autocomplete, search_by_title, get_popular_searches

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login_page'),
    path('signup/', views.signup_view, name='signup'),
    path('home/', views.home_view, name='home'),
    path('movie/', views.movie_view, name='movie'),
    path('results/', views.results_view, name='results'),
    path('recommend/', views.recommend_view, name='recommend'),
    
    # APIs
    path('api/weather/', weather_api, name='weather_api'),
    path('api/search/autocomplete/', search_autocomplete, name='search_autocomplete'),
    path('api/search/title/', search_by_title, name='search_by_title'),
    path('api/search/popular/', get_popular_searches, name='popular_searches'),
    
    # Test
    path('test-background/', views.test_background, name='test_background'),
]

# Servir les fichiers statiques et media en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
