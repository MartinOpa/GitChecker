from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import json
from .test_action import run_test
from .models import Commit, Repository

@api_view(['POST'])
@csrf_exempt
def postCommit(request):
    body = request.data

    repo = Repository.objects.filter(repo_id=body['repository']['id']).first()
    if repo == None:        
        repo = Repository()
        repo.repo_id = body['repository']['id']
        repo.repo_name = body['repository']['full_name']
        repo.actions = json.dumps(body['hook']['events'])
        repo.url = body['repository']['html_url']
        repo.save()
        
    if 'head_commit' in body:   
        commit = Commit()
        commit.repository = repo
        commit.author_name = body['head_commit']['author']['name']
        commit.timestamp = body['head_commit']['timestamp']
        commit.commit_message = body['head_commit']['message']
        commit.commit_url = body['head_commit']['url']
        commit.hash = body['after']
        commit.added_files = json.dumps(body['head_commit']['added'])
        commit.modified_files = json.dumps(body['head_commit']['modified'])
        commit.deleted_files = json.dumps(body['head_commit']['removed'])
        commit.save()

        run_test(commit)
        
    return Response({}, status=status.HTTP_200_OK)
