from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category)
    notify_answers_by_mail = models.BooleanField(default=True)
    answer = models.ForeignKey(Answer)
    answered = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title
    
class Answer(models.Model):
    description = models.TextField()
    author = models.ForeignKey(User)
    accepted = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    

    def __unicode__(self):
        return "Answer to %s" % self.question
    
    def save(self, *args, **kwargs):
        self.question.answered = True
        if self.accepted:
            self.question.resolved = True
        super(Answer,self).save(*args, **kwargs)
        
class Category(models.Model):
    name = models.CharField(max_length=255)
    questions = models.ForeignKey(Question)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    
    def __unicode__(self):
        return self.name
    
class Suggestion(models.Model):
    
    UNDER_REVIEW = 1
    QUEUED_FOR_DEVELOPMENT = 2
    UNDER_DEVELOPMENT = 3
    COMPLETED = 4
    REJECTED = 5
    
    STATUS_CHOICES = (
        (UNDER_REVIEW, "under review"),
        (QUEUED_FOR_DEVELOPMENT, "queued for development"),
        (UNDER_DEVELOPMENT, "under development"),
        (COMPLETED, "completed"),
        (REJECTED, "rejected"),
    )
    
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    description = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNDER_REVIEW)
    admin_update = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    
class Post(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(User)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add = True, editable=False)
    email_chefs = models.BooleanField(default = False)
    
    