from django.shortcuts import render, redirect
from .models import Task
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .tasks import send_task_email
from .forms import RegisterForm


# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, "task_list.html" , {'tasks':tasks})


# @login_required
# def add_task(request):
#     if request.method == "POST":
#         title = request.POST.get('title', '').strip()
#         due_date = request.POST.get('due_date')
#         description = request.POST.get('description', '').strip()
#         priority = request.POST.get('priority', 'Low')
#         Task.objects.create(
#             user=request.user,
#             title=title,
#             due_date=due_date,
#             description=description,
#             priority=priority
#         )
#         return redirect('task_list')
    
#     return render(request, "add_task.html")

@login_required
def add_task(request):
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'Low')

        task = Task.objects.create(
            user=request.user,
            title=title,
            due_date=due_date,
            description=description,
            priority=priority
        )

        cache.delete(f"tasks_{request.user.id}")
        
        send_task_email.delay(
            request.user.email,
            task.id,
            task.title,
            str(task.created_at),
            str(task.due_date),
        )


        return redirect('task_list')

    return render(request, "add_task.html")


# @login_required
# def update_task(request, id):
#     # task = Task.objects.get(id=id)
#     task = get_object_or_404(Task, id=id, user=request.user)
#     if request.method=="POST":
#         task.title = request.POST.get('title')
#         task.due_date = request.POST.get('due_date')
#         task.completed = request.POST.get('completed') == 'on'
#         task.save()
#         return redirect('task_list')
    
#     return render(request, 'update_task.html', {'task':task})

@login_required
def update_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)

    if request.method == "POST":
        task.title = request.POST.get('title')
        task.due_date = request.POST.get('due_date')
        task.completed = request.POST.get('completed') == 'on'
        task.save()

        cache.delete(f"tasks_{request.user.id}")
        return redirect('task_list')

    return render(request, 'update_task.html', {'task': task})



# @login_required
# def delete_task(request, id):
#     # task = Task.objects.get(id=id)
#     task = get_object_or_404(Task, id=id, user=request.user)
#     task.delete()
#     return redirect('task_list')

@login_required
def delete_task(request, id):
    task = get_object_or_404(Task, id=id, user=request.user)
    task.delete()
    cache.delete(f"tasks_{request.user.id}")
    return redirect('task_list')

    

def register(request):
    form = RegisterForm()
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    
    return render(request, "register.html", {'form':form})


# @login_required
# def get_tasks(request):
#     tasks = cache.get("tasks")
#     if not tasks:
#         # tasks = list(Task.objects.values())
#         tasks = list(Task.objects.filter(user=request.user).values())
        
#         cache.set("tasks", tasks, timeout=60)

#     return JsonResponse({"tasks": tasks})


@login_required
def get_tasks(request):
    cache_key = f"tasks_{request.user.id}"
    tasks = cache.get(cache_key)

    if tasks is None:
        tasks = list(Task.objects.filter(user=request.user).values())
        cache.set(cache_key, tasks, timeout=60)
    return JsonResponse({"tasks": tasks})


# @login_required
# def create_task(request):
#     if request.method == "POST":
#         task = Task.objects.create(
#             user=request.user,
#             title=request.POST['title'],
#             description=request.POST['description'],
#             due_date=request.POST['due_date'],
#             priority=request.POST.get('priority', 'Low'),
#         )

#         send_task_email.delay(request.user.email)
#         return JsonResponse({"message": "Task created"})

#     return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def create_task(request):
    if request.method == "POST":
        task = Task.objects.create(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            due_date=request.POST['due_date'],
            priority=request.POST.get('priority', 'Low'),
        )

        cache.delete(f"tasks_{request.user.id}")
        # send_task_email.delay(request.user.email)
        send_task_email.delay(
            request.user.email,
            task.id,
            task.title,
            str(task.created_at),
            str(task.due_date),
        )


        return JsonResponse({"message": "Task created", "task_id": task.id})

    return JsonResponse({"error": "Invalid request"}, status=400)

    

