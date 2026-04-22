from django.urls import path
from .views import (
    ProjectListCreateView,
    ProjectDetailView,
    TaskListCreateView,
    TaskDetailView,
    TaskAssignView,
    TaskCompleteView,
    ProjectTasksView,
    MyTasksView
)

urlpatterns = [
    # Project URLs - use UUID
    path('', ProjectListCreateView.as_view(), name='project-list'),
    path('<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    
    # Task URLs
    path('tasks/', TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<uuid:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/<uuid:pk>/assign/', TaskAssignView.as_view(), name='task-assign'),
    path('tasks/<uuid:pk>/complete/', TaskCompleteView.as_view(), name='task-complete'),
    
    # Project-specific tasks
    path('<uuid:project_pk>/tasks/', ProjectTasksView.as_view(), name='project-tasks'),
    
    # My tasks (assigned to current user)
    path('my-tasks/', MyTasksView.as_view(), name='my-tasks'),
]
