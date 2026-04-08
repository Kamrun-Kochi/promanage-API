from rest_framework import serializers
from .models import Project, Task
from apps.users.serializers import UserListSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for Project model.
    """
    owner_details = UserListSerializer(source='owner', read_only=True)
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'owner', 'owner_details', 
                  'tasks_count', 'completed_tasks_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(status='DONE').count()


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for listing projects.
    """
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    tasks_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ('id', 'title', 'owner', 'owner_name', 'tasks_count', 'created_at')
    
    def get_tasks_count(self, obj):
        return obj.tasks.count()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating projects.
    """
    class Meta:
        model = Project
        fields = ('id', 'title', 'description', 'owner')
        read_only_fields = ('id',)
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
