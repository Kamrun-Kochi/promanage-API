"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from apps.users.template_views import (
    home, user_login, user_signup, user_logout, 
    dashboard, profile, profile_update, password_change
)
from apps.projects.template_views import (
    project_list, project_create, project_detail, project_edit,
    task_create, task_edit, my_tasks
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home & Authentication
    path('', home, name='home'),
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    
    # Dashboard & Profile
    path('dashboard/', dashboard, name='dashboard'),
    path('profile/', profile, name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/password/', password_change, name='password_change'),
    
    # My Tasks
    path('my-tasks/', my_tasks, name='my_tasks'),
    
    # Projects
    path('projects/', project_list, name='project_list'),
    path('projects/create/', project_create, name='project_create'),
    path('projects/<uuid:project_id>/', project_detail, name='project_detail'),
    path('projects/<uuid:project_id>/edit/', project_edit, name='project_edit'),
    path('projects/<uuid:project_id>/tasks/', project_detail, name='project_tasks'),
    path('projects/<uuid:project_id>/tasks/create/', task_create, name='task_create'),
    path('projects/<uuid:project_id>/tasks/<uuid:task_id>/edit/', task_edit, name='task_edit'),
    
    # REST API URLs
    path('api/users/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
]

# Serve media and static files in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
