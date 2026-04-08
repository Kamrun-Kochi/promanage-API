from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from apps.projects.models import Project, Task

User = get_user_model()


def home(request):
    """Home page - redirects to dashboard if logged in, else shows landing page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def user_login(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'registration/login.html')


def user_signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        bio = request.POST.get('bio', '')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/signup.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'registration/signup.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'registration/signup.html')
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio
        )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'registration/signup.html')


def user_logout(request):
    """User logout view."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')


@login_required
def dashboard(request):
    """Dashboard view showing user stats and recent items."""
    user = request.user
    
    # Get user's projects
    projects = Project.objects.filter(owner=user)[:5]
    
    # Get user's tasks
    my_tasks = Task.objects.filter(assigned_to=user)
    my_task_list = my_tasks[:5]
    
    # Stats
    total_projects = Project.objects.filter(owner=user).count()
    completed_tasks = my_tasks.filter(status='DONE').count()
    in_progress_tasks = my_tasks.filter(status='IN_PROGRESS').count()
    
    context = {
        'projects': projects,
        'my_task_list': my_task_list,
        'total_projects': total_projects,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'my_tasks': my_tasks.count(),
    }
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """User profile view."""
    return render(request, 'registration/profile.html')


@login_required
def profile_update(request):
    """Update user profile."""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.bio = request.POST.get('bio', '')
        user.save()
        messages.success(request, 'Profile updated successfully!')
    return redirect('profile')


@login_required
@require_http_methods(["POST"])
def password_change(request):
    """Change user password."""
    user = request.user
    old_password = request.POST.get('old_password')
    new_password = request.POST.get('new_password')
    new_password_confirm = request.POST.get('new_password_confirm')
    
    if not user.check_password(old_password):
        messages.error(request, 'Current password is incorrect.')
        return redirect('profile')
    
    if new_password != new_password_confirm:
        messages.error(request, 'New passwords do not match.')
        return redirect('profile')
    
    user.set_password(new_password)
    user.save()
    
    # Re-login the user after password change
    from django.contrib.auth import update_session_auth_hash
    update_session_auth_hash(request, user)
    
    messages.success(request, 'Password changed successfully!')
    return redirect('profile')
