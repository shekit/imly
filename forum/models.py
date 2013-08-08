from django.db import models

class Question(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category)
    notify_answers_by_mail = models.BooleanField(default=True)
    answer = models.ForeignKey(Answer)
    answered = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __unicode__(self):
        return self.title
    
class Answer(models.Model):
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    accepted = models.BooleanField(default=False)

    def __unicode__(self):
        return "Answer to %s" % self.question
    
    def save(self, *args, **kwargs):
        self.question.answered = True
        super(Answer,self).save(*args, **kwargs)
        
class Category(models.Model):
    name = models.CharField(max_length=255)
    questions = models.ForeignKey(Question)
    
class Suggestion(models.Model):
    
    UNDER_REVIEW = 1
    UNDER_DEVELOPMENT = 2
    COMPLETED = 3
    REJECTED = 4
    
    
    STATUS_CHOICES = (
        (UNDER_REVIEW, "under review"),
        (UNDER_DEVELOPMENT, "under development"),
        (COMPLETED, "completed"),
        (REJECTED, "rejected"),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    votes = models.IntegerField(default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=UNDER_REVIEW)
    admin_update = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    
class Post(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add = True, editable=False)
    email_chefs = models.BooleanField(default = False)