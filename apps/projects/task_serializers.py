from rest_framework import serializers
from .models import Task
from apps.users.serializers import UserListSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for Task model.
    """
    assigned_to_details = UserListSerializer(source='assigned_to', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Task
        fields = ('id', 'project', 'project_title', 'title', 'assigned_to', 
                  'assigned_to_details', 'status', 'due_date', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class TaskListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing tasks.
    """
    assigned_to_name = serializers.SerializerMethodField()
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = Task
        fields = ('id', 'project', 'project_title', 'title', 'assigned_to', 
                  'assigned_to_name', 'status', 'due_date')
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return obj.assigned_to.get_full_name() or obj.assigned_to.username
        return None


class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating tasks.
    """
    class Meta:
        model = Task
        fields = ('id', 'project', 'title', 'assigned_to', 'status', 'due_date')
        read_only_fields = ('id',)


class TaskAssignSerializer(serializers.Serializer):
    """
    Serializer for assigning a task to a user.
    """
    assigned_to = serializers.IntegerField()


class TaskStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating task status.
    """
    status = serializers.ChoiceField(choices=Task.STATUS_CHOICES)
