"""
URL configuration for maritime project.

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
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings
from apps.resources.views import TokenLoginView, csrf_token_view

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path('login/', TokenLoginView.as_view(), name='login'),  # Direct login endpoint
    path('csrf-token/', csrf_token_view, name='csrf-token'),  # CSRF token endpoint
]


apps = [path('', include(f"apps.{app['name']}.urls")) for app in settings.APPS_LOCAL]

urlpatterns += i18n_patterns(
    # Add first page's url for the project.
    # path('', ),
    path('admin/', admin.site.urls), 
    path('api/', include("apps.resources.urls")),
    path('api/geography/', include("apps.geography.urls")),

    *apps,
    prefix_default_language=False
)
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)