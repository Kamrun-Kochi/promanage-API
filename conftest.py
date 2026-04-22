import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User
from apps.projects.models import Project, Task


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='otherpass123'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def project(db, user):
    return Project.objects.create(
        title='Test Project',
        description='Test Description',
        owner=user
    )


@pytest.fixture
def task(db, project, user):
    return Task.objects.create(
        project=project,
        title='Test Task',
        assigned_to=user,
        status='TODO'
    )