import datetime

from django.db import models
from django.utils import timezone
# P.97 for slugify
from django.template.defaultfilters import slugify


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    # add for chapter 6 p.97
    # slug = models.SlugField()
    # edit it ch6 p.99
    # slug = models.SlugField(blank=True) # p.100 replace it
    # ch6 p.100 we can ensure that the slug field is also unique 
    # by adding the constraint to the slug field. 
    slug = models.SlugField(unique=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    # typo within the admin interface (Categorys, not Categories) can be fixed by adding a nested Meta class 
    # into your model definitions with the verbose_name_plural attribute.
    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Page(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)
    def __str__(self):
        return self.title

# p.83 Official Tutorial
# https://docs.djangoproject.com/en/2.1/intro/tutorial02/
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')
    def __str__(self):
        return self.question_text
    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    def __str__(self):
        return self.choice_text