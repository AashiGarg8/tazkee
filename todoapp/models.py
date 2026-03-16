from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class Task(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE) #(User) this is built in user so we will import it aswell.
#     title = models.CharField(max_length=255)
#     description = models.TextField()
#     due_date = models.DateField()
#     priority = models.CharField(
#         max_length=10,
#         choices=[
#             ('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')],
#             default='Low'
#     )
#     completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#using pgiadmin  #relationship
class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    title = models.CharField(max_length=200, db_index=True)     #Indexing  #This makes search queries faster.
    description = models.TextField()
    due_date = models.DateField()
    priority = models.CharField(
        max_length=10,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], 
            default='Low'
    )
    completed = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    
    
    def __str__(self):
        return self.title
    
