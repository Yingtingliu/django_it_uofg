import datetime

from django.contrib import admin
from rango.models import Category, Page
from django.utils import timezone

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')

# admin.site.register(Category)
admin.site.register(Page, PageAdmin)

"""
p.99 add this to solve blank slug, refer to rango/model.py 
code: slug = models.SlugField(blank=True)
customise the admin interface so that it automatically pre-populates the slug
field as you type in the category name
"""

# Add in this class to customise the Admin Interface
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('name',)}
# Update the registration to include this customised interface
admin.site.register(Category, CategoryAdmin)

# https://docs.djangoproject.com/en/2.1/ref/contrib/admin/

from .models import Choice, Question

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['question_text']}),
        ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
    ]
    inlines = [ChoiceInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'

admin.site.register(Question, QuestionAdmin)
