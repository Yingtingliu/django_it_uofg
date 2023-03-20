from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.urls import reverse
from rango.models import Category
from rango.models import Page
# ch7
from rango.forms import CategoryForm
from django.shortcuts import redirect
from django.template.loader import get_template, select_template
# ch7 excercise
from rango.forms import PageForm
# ch9
from django.shortcuts import render
from .forms import UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ch13
from rango.bing_search import run_query

def index(request):
    """
    Construct a dictionary to pass to the template engine as its context.
    Note the key boldmessage matches to {{ boldmessage }} in the template!
    context_dict = {'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!'}
    Return a rendered response to send to the client.
    We make use of the shortcut function to make our lives easier.
    Note that the first parameter is the template we wish to use.

    -------Chapter 6 ----------
    Query the database for a list of ALL categories currently stored.
    Order the categories by the number of likes in descending order.
    Retrieve the top 5 only -- or all if less than 5.
    Place the list in our context_dict dictionary (with our boldmessage!)
    that will be passed to the template engine.
    """

    category_list = Category.objects.order_by(
        '-likes')[:5]  # this shows the top 5 categories
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # ch10 excercise: still calculating the number of visits, but not render to page
    # Call the helper function to handle the sessions    
    visitor_cookie_handler(request) 
    context_dict['visits'] = request.session['visits']

    # This is using cookies
    # context_dict['visits'] = request.COOKIES.get('visits', '1')
    # Obtain our Response object early so we can add cookie information.
    response = render(request, 'index.html', context=context_dict)

    # Call the helper function to handle the cookies
    # visitor_cookie_handler(request, response)

    # Return response back to the user, updating any cookies that need changed.
    return response


def about(request):

    context_dict = {}
    # Call the helper function to handle the sessions
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']


    response = render(request, 'about.html' ,context=context_dict)
    return response




def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass
    # to the template rendering engine.
    context_dict = {}
    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        # updated ch15 - order by views
        pages = Page.objects.filter(category=category).order_by('-views')
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from
        # the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything -
        # the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None
        # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                # probably better to use a redirect here.
            return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form':form, 'category': category}

    return render(request, 'rango/add_page.html', context_dict)


@login_required
def restricted(request):
    return render(request,'rango/restricted.html')

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val

# Updated the function definition
def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                                    'last_visit',str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's been more than a day since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        # Update the last visit cookie now that we have updated the count
        request.session['last_visit'] = str(datetime.now())
    else:
        # Set the last visit cookie
        request.session['last_visit'] = last_visit_cookie
    # Update/set the visits cookie
    request.session['visits'] = visits

def search(request):
    result_list = []
    query = ''
    if request.method == 'POST':
        query = request.POST['query'].strip()
    if query:
    # Run our Bing function to get the results list!
        result_list = run_query(query)
    return render(request, 'rango/search.html', {'result_list': result_list})

def goto_url(request):
   
    if request.method == 'GET':
        page_id = request.GET.get('page_id')
        try:
            selected_page = Page.objects.get(id=page_id)
        except Page.DoesNotExist:
            return redirect(reverse('rango:index'))
        selected_page.views = selected_page.views + 1
        selected_page.save()
        return redirect(selected_page.url)
    
    return redirect(reverse('rango:index'))
