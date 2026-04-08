from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import Http404
from apps.projects.models import Project, Task

User = get_user_model()


@login_required
def project_list(request):
    """List all projects owned by the user."""
    projects = Project.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    """Create a new project."""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        
        project = Project.objects.create(
            title=title,
            description=description,
            owner=request.user
        )
        
        messages.success(request, 'Project created successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/project_form.html', {'form_title': 'Create Project'})


@login_required
def project_detail(request, project_id):
    """View project details."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        raise Http404("Project not found")
    
    tasks = project.tasks.all().order_by('-created_at')
    
    return render(request, 'projects/project_detail.html', {
        'project': project,
        'tasks': tasks
    })


@login_required
def project_edit(request, project_id):
    """Edit a project."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        raise Http404("Project not found")
    
    if request.method == 'POST':
        project.title = request.POST.get('title')
        project.description = request.POST.get('description')
        project.save()
        
        messages.success(request, 'Project updated successfully!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'projects/project_form.html', {
        'form_title': 'Edit Project',
        'project': project
    })


@login_required
def task_create(request, project_id):
    """Create a new task in a project."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        raise Http404("Project not found")
    
    if request.method == 'POST':
        title = request.POST.get('title')
        status = request.POST.get('status', 'TODO')
        assigned_to_id = request.POST.get('assigned_to')
        due_date = request.POST.get('due_date')
        
        assigned_to = None
        if assigned_to_id:
            try:
                assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                pass
        
        Task.objects.create(
            project=project,
            title=title,
            status=status,
            assigned_to=assigned_to,
            due_date=due_date or None
        )
        
        messages.success(request, 'Task created successfully!')
        return redirect('project_detail', project_id=project.id)
    
    users = User.objects.all()
    return render(request, 'projects/task_form.html', {
        'form_title': 'Create Task',
        'project_id': project_id,
        'users': users
    })


@login_required
def task_edit(request, project_id, task_id):
    """Edit a task."""
    try:
        project = Project.objects.get(id=project_id, owner=request.user)
    except Project.DoesNotExist:
        raise Http404("Project not found")
    
    try:
        task = Task.objects.get(id=task_id, project=project)
    except Task.DoesNotExist:
        raise Http404("Task not found")
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        task.due_date = request.POST.get('due_date') or None
        
        if assigned_to_id:
            try:
                task.assigned_to = User.objects.get(id=assigned_to_id)
            except User.DoesNotExist:
                task.assigned_to = None
        else:
            task.assigned_to = None
        
        task.save()
        
        messages.success(request, 'Task updated successfully!')
        return redirect('project_detail', project_id=project.id)
    
    users = User.objects.all()
    return render(request, 'projects/task_form.html', {
        'form_title': 'Edit Task',
        'project_id': project_id,
        'task': task,
        'users': users
    })


@login_required
def my_tasks(request):
    """List all tasks assigned to the user."""
    tasks = Task.objects.filter(assigned_to=request.user).order_by('status', '-created_at')
    return render(request, 'projects/my_tasks.html', {'tasks': tasks})
