"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

# Static settings
from django.conf import settings
from django.conf.urls.static import static

# Admin custom
admin.site.site_title = "Admin"
admin.site.site_header = "IPU Lms"
admin.site.index_title = "Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),

    # Landing
    path('', include('apps.main.urls', namespace='main')),

    # Accounts
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),

    # Courses
    path('courses/', include('apps.courses.urls', namespace='courses')),

    # Assessments
    path('assessments/', include('apps.assessments.urls', namespace='assessments')),

    # Attendance
    path('attendance/', include('apps.attendance.urls', namespace='attendance')),

    # Analytics
    path('analytics/', include('apps.analytics.urls', namespace='analytics')),

    # Content
    path('content/', include('apps.content.urls', namespace='content')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)