from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Project, Task
from .serializers import ProjectSerializer, ProjectListSerializer, ProjectCreateUpdateSerializer
from .task_serializers import TaskSerializer, TaskListSerializer, TaskCreateUpdateSerializer
# Import Celery tasks
from .tasks import send_task_assignment_email, send_task_status_update_email


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to edit their projects.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class ProjectListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all projects or create a new project.
    """
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProjectCreateUpdateSerializer
        return ProjectListSerializer
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    def get_queryset(self):
        user = self.request.user
        # Return projects owned by user or where user has tasks assigned
        return Project.objects.filter(
            owner=user
        ) | Project.objects.filter(
            tasks__assigned_to=user
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to get, update, or delete a project.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(owner=user)


# ====================
# Task Views
# ====================

class TaskListCreateView(generics.ListCreateAPIView):
    """
    API endpoint to list all tasks or create a new task.
    """
    queryset = Task.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskListSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Return tasks from projects owned by user or assigned to user
        return Task.objects.filter(
            project__owner=user
        ) | Task.objects.filter(
            assigned_to=user
        )


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint to get, update, or delete a task.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            project__owner=user
        ) | Task.objects.filter(
            assigned_to=user
        )


class TaskAssignView(APIView):
    """
    API endpoint to assign a task to a user.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        user_id = request.data.get('assigned_to')
        
        # Check if user is project owner
        if task.project.owner != request.user:
            return Response(
                {'error': 'Only project owner can assign tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            user = User.objects.get(pk=user_id)
            # Store old assignment for email
            old_assigned = task.assigned_to
            task.assigned_to = user
            task.save()
            
            # Send async email notification
            if user.email:
                send_task_assignment_email.delay(
                    task_id=task.id,
                    user_email=user.email,
                    task_title=task.title,
                    project_title=task.project.title
                )
            
            return Response(TaskSerializer(task).data)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class TaskCompleteView(APIView):
    """
    API endpoint to mark a task as completed.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        
        # Check if user is project owner or assigned to task
        if task.project.owner != request.user and task.assigned_to != request.user:
            return Response(
                {'error': 'You do not have permission to complete this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        task.status = 'DONE'
        task.save()
        return Response(TaskSerializer(task).data)


class ProjectTasksView(generics.ListCreateAPIView):
    """
    API endpoint to list tasks for a specific project or create a task in that project.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateUpdateSerializer
        return TaskListSerializer
    
    def get_queryset(self):
        project_pk = self.kwargs['project_pk']
        user = self.request.user
        return Task.objects.filter(
            project_id=project_pk,
            project__owner=user
        ) | Task.objects.filter(
            project_id=project_pk,
            assigned_to=user
        )
    
    def perform_create(self, serializer):
        from django.shortcuts import get_object_or_404
        project = get_object_or_404(Project, pk=self.kwargs['project_pk'], owner=self.request.user)
        task = serializer.save(project=project)
        
        # Send async email if task is assigned during creation
        if task.assigned_to and task.assigned_to.email:
            send_task_assignment_email.delay(
                task_id=task.id,
                user_email=task.assigned_to.email,
                task_title=task.title,
                project_title=project.title
            )


class MyTasksView(generics.ListAPIView):
    """
    API endpoint to list tasks assigned to the current user.
    """
    serializer_class = TaskListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
