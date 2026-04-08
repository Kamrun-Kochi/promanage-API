from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    TaskListCreateView,
    TaskDetailView,
    TaskAssignView,
    TaskCompleteView,
    ProjectTasksView
)

urlpatterns = [
    # Project URLs
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    
    # Task URLs
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<uuid:pk>/assign/', TaskAssignView.as_view(), name='task-assign'),
    path('tasks/<uuid:pk>/complete/', TaskCompleteView.as_view(), name='task-complete'),
    
    # Project-specific tasks
    path('<uuid:project_pk>/tasks/', ProjectTasksView.as_view(), name='project-tasks'),
]
