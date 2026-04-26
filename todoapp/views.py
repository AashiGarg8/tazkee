import json
import random
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Task
from .tasks import send_task_email, send_email


# Create your views here.
# CACHE HELPER FUNCTION
def _get_cached_tasks_for_user(user):
    cache_key = f"tasks_{user.id}"
    cached_tasks = cache.get(cache_key)

    if cached_tasks is None:
        tasks = list(Task.objects.filter(user=user).values())
        cache.set(cache_key, json.dumps(tasks, default=str), timeout=3600)
        return tasks

    return json.loads(cached_tasks)

# landing page
def landing(request):
    return render(request, 'landing.html')


# task list view 
@login_required
def task_list(request):
    tasks = _get_cached_tasks_for_user(request.user)
    return render(request, "task_list.html" , {'tasks':tasks})

# add task 
@login_required
def add_task(request):
    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        due_date = request.POST.get('due_date')
        description = request.POST.get('description', '').strip()
        priority = request.POST.get('priority', 'Low')

        #create new task
        task = Task.objects.create(
            user=request.user,
            title=title,
            due_date=due_date,
            description=description,
            priority=priority
        )
        # Invalidate cache after data change
        cache.delete(f"tasks_{request.user.id}")
        
        # Send email asynchronously if email exists
        if request.user.email:
            send_task_email.delay(
                request.user.email,
                task.id,
                task.title,
                str(task.created_at),
                str(task.due_date),
            )



        return redirect('task_list')

    return render(request, "add_task.html")



# update task 
@login_required
def update_task(request, id):
    #Ensures user can only update their own task
    task = get_object_or_404(Task, id=id, user=request.user)

    if request.method == "POST":
        old_due_date = task.due_date
        old_completed = task.completed

        # Update fields
        task.title = request.POST.get('title')
        task.due_date = request.POST.get('due_date')
        task.completed = request.POST.get('completed') == 'on'

        # Reset reminder if task is modified significantly
        if str(old_due_date) != str(task.due_date) or (old_completed and not task.completed):
            task.reminder_sent = False

        task.save()

        # Clear cache after update
        cache.delete(f"tasks_{request.user.id}")
        return redirect('task_list')

    return render(request, 'update_task.html', {'task': task})




# Delete task
@login_required
def delete_task(request, id):
    # Delete a task belonging to the logged-in user.
    task = get_object_or_404(Task, id=id, user=request.user)
    task.delete()
    # Clear cache after deletion
    cache.delete(f"tasks_{request.user.id}")
    return redirect('task_list')

# user register with otp 
#Register new user with OTP verification.
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm = request.POST["confirm_password"]

        # Validation checks
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        # Generate OTP
        otp = str(random.randint(1000, 9999))

        # Store OTP in cache (valid for 5 minutes)
        cache.set(f"otp_{email}", otp, timeout=300)

        # Store temporary user data in session
        request.session["temp_user"] = {
            "username": username,
            "email": email,
            "password": password,
        }

        # Send OTP email asynchronously
        send_email.delay(
            "OTP Verification",
            f"Your OTP is {otp}",
            email
        )
        return redirect("verify_otp")

    return render(request, "register.html")


# OTP VERIFICATION
def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST["otp"]
        temp_user = request.session.get("temp_user")

        if not temp_user:
            messages.error(request, "Session expired. Please register again.")
            return redirect("register")

        email = temp_user["email"]
        stored_otp = cache.get(f"otp_{email}")

        # Validate OTP
        if stored_otp == user_otp:
            user = User.objects.create_user(
                username=temp_user["username"],
                email=temp_user["email"],
                password=temp_user["password"]
            )
            # Send success email
            send_email.delay(
                "Registration Successful",
                f"Hello {user.username}, your account has been successfully created.",
                email
            )

            cache.delete(f"otp_{email}")
            del request.session["temp_user"]

            messages.success(request, "Account created successfully")
            return redirect("login")

        else:
            messages.error(request, "Invalid OTP")

    return render(request, "verify_otp.html")


#get tasks
@login_required
def get_tasks(request):
    tasks = _get_cached_tasks_for_user(request.user)
    return JsonResponse({"tasks": tasks})



#Create task
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
        # Clear cache after creation
        cache.delete(f"tasks_{request.user.id}")
        # send_task_email.delay(request.user.email)
        # Send async email notification
        if request.user.email:
            send_task_email.delay(
                request.user.email,
                task.id,
                task.title,
                str(task.created_at),
                str(task.due_date),
            )



        return JsonResponse({"message": "Task created", "task_id": task.id})

    return JsonResponse({"error": "Invalid request"}, status=400)

    

