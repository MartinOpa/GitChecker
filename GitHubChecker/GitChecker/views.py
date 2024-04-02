from django.contrib.auth.decorators import login_required 
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect
from rest_framework.decorators import api_view
import json
import pandas as pd
from plotly.offline import plot
import plotly.express as px
from .models import Commit, Repository, Test
from .forms import UserForm, RegForm, RepoDetailForm, TestParametersFormSet, TestParameters

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

    return render(request, 'GitChecker/commits.html', {'current_page': current_page})

# Repositories with links to their detail page with test parameters
@api_view(['GET'])
@login_required(login_url='/login')
def repos(request, page=1):
    repos = Repository.objects.all()

    data = []
    for repo in repos:
        try:
            test = Test.objects.filter(repository=repo).latest('timestamp')
            latest_test = test
        except Test.DoesNotExist:
            latest_test = -1
            
        data.append((repo, latest_test))

    paginator = Paginator(data, per_page=20)
    current_page = paginator.get_page(page)

    return render(request, 'GitChecker/repos.html', {'current_page': current_page})

# Repository detail - test parameters setup
@api_view(['GET', 'POST'])
@login_required(login_url='/login')
def repo_detail(request, id):
    repo = Repository.objects.get(pk=id)
    if request.method == 'GET':
        repository_form = RepoDetailForm(instance=repo)
        formset = TestParametersFormSet(instance=repo)

        return render(request, 'GitChecker/repo.detail.html',
                    {'repo': repo, 'repository_form': repository_form, 'formset': formset})
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
                    {'repo': repo, 'repository_form': repository_form, 'formset': formset})
        
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
        query |= Q(repository__repo_name__icontains=search_query)

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
        test.params = TestParameters(repository=test.repository, param_name='set deleted', parameters={'not found': True})
        
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
def tests_charts(request, filter=None):
    tests = Test.objects.all()
    
    if tests:
        # data = [
        #     {
        #         'commit': x.commit.id,
        #         'timestamp': x.timestamp,
        #         'duration': x.duration,
        #         'errors': x.errors
        #     } for x in tests
        # ]
        data = [
            {
                'commit': 1,
                'timestamp': 12,
                'duration': 1,
                'errors': 0
            }
        ]

        df = pd.DataFrame(data)
        fig = px.scatter(df, y="duration", x="timestamp", color="commit")
        fig.update_layout(plot_bgcolor='#b4b4b4', paper_bgcolor='#1a242c', font=dict(color='#f0f8ff'))
        fig.update_yaxes(range = [0, None])
        tests_plot = plot(fig, output_type='div')
    else:
        tests_plot = ''

    return render(request, 'GitChecker/tests_charts.html', {'tests_plot': tests_plot})

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
