from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view
import json
#from plotly.offline import plot
#import plotly.express as px
from .models import Commit, Repository, Test
from .forms import UserForm, RegForm, RepoDetailForm, TestParametersFormSet, TestParameters
from .views_utils import TestQueryData, get_filtered_tests, get_charts, get_date

# Home page, 3 latest tests + their commits + links
@api_view(['GET'])
@login_required(login_url='/login')
def home(request):
    return redirect('commits/1')

# Commits with links to their detail page with tests
@api_view(['GET'])
@login_required(login_url='/login')
def commits(request, page=1):
    filter = request.GET.get('search', None)
    if filter:
        query = Q()
        search_query = filter.strip()
        for field in Commit._meta.fields:  
            if field.get_internal_type() in ['CharField', 'TextField']:
                query |= Q(**{f'{field.name}__icontains': search_query})
        
        query |= Q(repository__repo_name__icontains=search_query)
        
        commits = Commit.objects.filter(query).order_by('-timestamp')
    else:
        commits = Commit.objects.all().order_by('-timestamp')

    paginator = Paginator(commits, per_page=20)
    current_page = paginator.get_page(page)
    theme = request.COOKIES.get('theme')
    print(theme)

    return render(request, 'GitChecker/commits.html', {'current_page': current_page, 'theme': theme})

# Repositories with links to their detail page with test parameters
@api_view(['GET'])
@login_required(login_url='/login')
def repos(request, page=1):
    repos = Repository.objects.all()
    theme = request.COOKIES.get('theme')

    data = []
    for repo in repos:
        try:
            test = Test.objects.filter(commit__repository=repo).latest('timestamp')
            latest_test = test
        except Test.DoesNotExist:
            latest_test = -1
            
        data.append((repo, latest_test))

    paginator = Paginator(data, per_page=20)
    current_page = paginator.get_page(page)

    return render(request, 'GitChecker/repos.html', {'current_page': current_page, 'theme': theme})

# Repository detail - test parameters setup
@api_view(['GET', 'POST'])
@login_required(login_url='/login')
def repo_detail(request, id):
    theme = request.COOKIES.get('theme')
    repo = Repository.objects.get(pk=id)
    if request.method == 'GET':
        repository_form = RepoDetailForm(instance=repo)
        formset = TestParametersFormSet(instance=repo)

        return render(request, 'GitChecker/repo.detail.html',
                    {'repo': repo, 'repository_form': repository_form, 'formset': formset, 'theme': theme})
    else:
        repository_form = RepoDetailForm(request.POST, instance=repo)
        formset = TestParametersFormSet(request.POST, instance=repo)

        if repository_form.is_valid() and formset.is_valid():
            repository_form.save()
            formset.save()
            return HttpResponseRedirect(f'/repo/{id}')
        else:
            print(repository_form.errors)
            print(formset.errors)
            return render(request, 'GitChecker/repo.detail.html',
                    {'repo': repo, 'repository_form': repository_form, 'formset': formset, 'theme': theme})
        
# Tests with links to their detail page with logs
@api_view(['GET'])
@login_required(login_url='/login')
def tests(request, page=1):
    filter = request.GET.get('search', None)
    if filter:
        query = Q()
        search_query = filter.strip()
        for field in Test._meta.fields:  
            if field.get_internal_type() in ['CharField', 'TextField']:
                query |= Q(**{f'{field.name}__icontains': search_query})
        
        query |= Q(params__param_name__icontains=search_query)
        query |= Q(commit__repository__repo_name__icontains=search_query)

        tests = Test.objects.filter(query).order_by('-timestamp')
    else:
        tests = Test.objects.all().order_by('-timestamp')

    paginator = Paginator(tests, per_page=20)
    current_page = paginator.get_page(page)

    return render(request, 'GitChecker/tests.html', {'current_page': current_page})

# Test detail - summary, log
@api_view(['GET'])
@login_required(login_url='/login')
def test_detail(request, id):
    test = Test.objects.get(pk=id)

    if not test.params:
        test.params = TestParameters(repository=test.commit.repository, param_name='set deleted', parameters={'not found': True})
        
    json_data = json.dumps(test.params.parameters)

    summary_json = json.loads(test.summary)
    summary = ''
    try:
        for key, value in summary_json.items():
            summary += f'{key}\t{value}\n'
    except:
        # summary is a json list
        for item in json.loads(summary_json):
            summary += f'{item}\n'

    detailed_json = json.loads(test.detailed)
    detailed = ''
    try:
        for key, value in detailed_json.items():
            detailed += f'{key}\t{value}\n'
    except:
        # detailed is a json list
        for item in json.loads(detailed_json):
            detailed += f'{item}\n'

    return render(request, 'GitChecker/test.detail.html', 
                  {'test': test, 'json_data': json_data, 'summary': summary, 'detailed': detailed})

# Test data with charts
@api_view(['GET'])
@login_required(login_url='/login')
def tests_charts(request):
    repos = Repository.objects.all()
    repo_id = request.GET.get('repo', -1)
    if repo_id == -1:
        current_repo = repos.first()
        repo_id = current_repo.id
    else:
        try:
            current_repo = repos.get(pk=repo_id)
        except:
            # No data to render
            if request.htmx:
                return render(request, 'GitChecker/base.charts.html')
            return render(request, 'GitChecker/tests_charts.html')
    
    # Get selected metrics
    metrics_selected = request.GET.getlist('metrics-options', [])

    # Available params
    repo = Repository.objects.get(id=repo_id)
    param_select = ['Any'] 
    param_select.extend(list(TestParameters.objects.filter(repository=repo).values_list('param_name', flat=True).distinct()))

    # Query parameters for set 1
    query1 = TestQueryData()
    query1.param_options = param_select
    query1.param_name = request.GET.get('param-1', 'Any')
    query1.date_from = get_date(request, 'date-from-1')
    query1.date_to = get_date(request, 'date-to-1')

    # Query parameters for set 2
    query2 = TestQueryData()
    query2.param_options = param_select
    query2.param_name = request.GET.get('param-2', 'Any')
    query2.date_from = get_date(request, 'date-from-2')
    query2.date_to = get_date(request, 'date-to-2')

    tests2 = None
    charts2 = None
    # HTMX limitation
    compare_on_str = request.GET.get('compare-on', 'false')
    compare_on = compare_on_str == 'true'

    # Theme cookie
    theme = request.COOKIES.get('theme')

    # Send set1 and metrics
    tests1 = get_filtered_tests(repo_id, query1)
    charts1, metrics_options = get_charts(tests1, metrics_selected, theme)
    # If comparison mode is on send set2 as well
    if compare_on:
        tests2 = get_filtered_tests(repo_id, query2)
        charts2, _ = get_charts(tests2, metrics_selected, theme)

    changed = request.GET.get('changed', False)
    # Only update charts if htmx sent the request
    if request.htmx and not changed:
        template = 'GitChecker/base.charts.html'
    else:
        template = 'GitChecker/tests_charts.html'

    return render(request, template, 
                  {'charts1': charts1, 'charts2': charts2, 'current_repo': current_repo, 
                   'compare_on': compare_on, 'repos': repos, 'query1': query1, 'query2': query2,
                   'metrics_options': metrics_options, 'metrics_selected': metrics_selected})

# Login page
@api_view(['GET', 'POST'])
def user_login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('commits')
        form = UserForm()
        return render(request, 'GitChecker/login.html', {'form': form})
    else:
        form = UserForm(request.POST)
        
        if form.is_valid():
            username = form.cleaned_data['username'].lower()
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                # request._request => django.http.HttpRequest != rest_framework.request.Request
                login(request._request, user)
                return redirect('/commits/1')

        return render(request, 'GitChecker/login.html', {'form': form})
    
# Register page
@api_view(['GET', 'POST'])
def user_register(request):
    if request.method == 'GET':
        form = RegForm()
        return render(request, 'GitChecker/register.html', {'form': form})
    else:
        form = RegForm(request.POST) 
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            return redirect('login')
        else:
            return render(request, 'GitChecker/register.html', {'form': form})

# Logout
@api_view(['GET'])
def user_log_out(request):
    logout(request)
    return redirect('login')  
