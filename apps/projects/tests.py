from django.urls import reverse
from rest_framework import status
from apps.projects.models import Project, Task
import pytest


@pytest.mark.django_db
class TestProjectViewSet:
    def test_list_projects(self, authenticated_client, project):
        url = reverse('project-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_project(self, authenticated_client, user):
        url = reverse('project-list')
        data = {
            'title': 'New Project',
            'description': 'Project Description',
            'owner': user.pk
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Project.objects.filter(title='New Project').exists()

    def test_get_project_detail(self, authenticated_client, project):
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == project.title

    def test_update_project(self, authenticated_client, project):
        url = reverse('project-detail', kwargs={'pk': project.pk})
        data = {'title': 'Updated Title'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.title == 'Updated Title'

    def test_delete_project(self, authenticated_client, project):
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_other_user_cannot_delete_project(self, authenticated_client, other_user, project):
        project.owner = other_user
        project.save()
        
        url = reverse('project-detail', kwargs={'pk': project.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTaskViewSet:
    def test_list_tasks(self, authenticated_client, task):
        url = reverse('task-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_task(self, authenticated_client, project, user):
        url = reverse('task-list')
        data = {
            'project': project.pk,
            'title': 'New Task',
            'assigned_to': user.pk,
            'status': 'TODO'
        }
        response = authenticated_client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title='New Task').exists()

    def test_update_task_status(self, authenticated_client, task):
        url = reverse('task-detail', kwargs={'pk': task.pk})
        data = {'status': 'IN_PROGRESS'}
        response = authenticated_client.patch(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'IN_PROGRESS'

    def test_delete_task(self, authenticated_client, task):
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(pk=task.pk).exists()

    def test_filter_tasks_by_status(self, authenticated_client, task):
        url = f"{reverse('task-list')}?status=TODO"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_filter_tasks_by_project(self, authenticated_client, project, task):
        url = f"{reverse('task-list')}?project={project.pk}"
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMyTasks:
    def test_get_my_tasks(self, authenticated_client, user, task):
        url = reverse('my-tasks')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK