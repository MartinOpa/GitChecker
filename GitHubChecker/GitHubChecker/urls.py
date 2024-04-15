"""
URL configuration for GitHubChecker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from GitChecker import views, webhook

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('webhooks/commit', webhook.post_commit),
    path('runtests', views.run_tests_manual),
    path('tests_charts/', views.tests_charts, name='tests_charts'),
    path('commits/<int:page>', views.commits, name='commits'),
    path('repos/<int:page>', views.repos, name='repos'),
    path('repo/<int:id>', views.repo_detail, name='repo_detail'),
    path('tests/<int:page>', views.tests, name='tests'),
    path('test/<int:id>', views.test_detail, name='test'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_log_out, name='logout')
]  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
