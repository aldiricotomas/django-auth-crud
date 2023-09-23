from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import CreateTaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'GET':    
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Register user
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()

                login(request, user)

                return redirect('tasks') 
            
            except IntegrityError as error:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'Username already exists'
                })
        
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Password do not match'
        })


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):

    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Username or password is incorrect'
            })
        else: 
            login(request, user)
            return redirect('tasks')


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)

    return render(request, 'tasks.html', {
        'tasks': tasks
    })


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')

    return render(request, 'tasks.html', {
        'tasks': tasks
    })


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': CreateTaskForm
        })
    else:
        try:
            form = CreateTaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
        except ValueError as error: 
            return render(request, 'create_task.html', {
                'form': CreateTaskForm,
                'error': 'Please, provide valid data' 
            })

        return redirect('tasks')


@login_required
def task_detail(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    if request.method == 'GET':
        form = CreateTaskForm(instance=task)
        return render(request, 'task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            form = CreateTaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError as error:
            return render(request, 'task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error updating task' 
            })


@login_required
def complete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    
    if request.method == 'POST':
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')
    

@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')


