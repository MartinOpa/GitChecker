from django.db import models

class Repository(models.Model):
    repo_id = models.BigIntegerField()
    repo_name = models.CharField(max_length=100)
    actions = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    test_dir = models.TextField()
    test_command = models.TextField()

class Commit(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField('commit timestamp')
    commit_message = models.TextField()
    commit_url = models.CharField(max_length=300)
    hash = models.CharField(max_length=40)
    added_files = models.JSONField(default=dict)
    modified_files = models.JSONField(default=dict)
    deleted_files = models.JSONField(default=dict)
    
class TestParameters(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    version = models.CharField(max_length=16, default='python3.10')
    param_name = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict, null=True, blank=True)

class Test(models.Model):
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)
    commit = models.ForeignKey(Commit, on_delete=models.CASCADE)
    params = models.ForeignKey(TestParameters, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField('test timestamp')
    summary = models.JSONField(default=dict)
    detailed = models.JSONField(default=dict)
    