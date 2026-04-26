from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views #alias name to views

login_view = auth_views.LoginView.as_view(
    template_name='login.html',
    next_page='task_list',
    redirect_authenticated_user=True,
)

urlpatterns = [
    path('', views.landing, name='landing'),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path('tasks/', views.task_list, name="task_list"),
    path('api/tasks/', views.get_tasks, name='get_tasks'),
    path('add/', views.add_task, name="add_task"),
    path('update/<int:id>/', views.update_task, name="update_task"),
    path('delete/<int:id>/', views.delete_task , name="delete_task"),
    path('accounts/login/', login_view),
    path('register/', views.register, name="register"),
    path('login/', login_view, name="login"),
    path('logout/', auth_views.LogoutView.as_view(next_page='register'), name="logout"),
]

