from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from .models import Task

@shared_task
def send_task_email(user_email, task_id, title, created_at, due_date):
    subject = "Task Created"

    message = (
        f"Your task was successfully created.\n\n"
        f"Task ID: {task_id}\n"
        f"Title: {title}\n"
        f"Created At: {created_at}\n"
        f"Due Date: {due_date}\n"
    )

    send_mail(
        subject,
        message,
        None,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_due_reminder(user_email, task_title, due_date):
    send_mail(
        "Task Reminder",
        (
            f"Reminder: {task_title} is due soon.\n\n"
            f"Due Date: {due_date}\n"
        ),
        None,
        [user_email],
        fail_silently=False,
    )


@shared_task
def send_due_reminders():
    tomorrow = timezone.localdate() + timezone.timedelta(days=1)
    due_tasks = Task.objects.filter(
        completed=False,
        reminder_sent=False,
        due_date=tomorrow,
        user__email__isnull=False,
    ).exclude(user__email="")

    for task in due_tasks.select_related("user"):
        send_due_reminder.delay(task.user.email, task.title, str(task.due_date))
        task.reminder_sent = True
        task.save(update_fields=["reminder_sent"])
