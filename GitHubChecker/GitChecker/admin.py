from django.contrib import admin
from .models import Commit, Repository, Test, TestParameters

admin.site.register(Commit)
admin.site.register(Repository)
admin.site.register(Test)
admin.site.register(TestParameters)
