from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .test_action import run_test
from .models import Commit, Repository

@api_view(['POST'])
def post_commit(request):
    body = request.data

    # Check if repo already exists
    repo = Repository.objects.filter(repo_id=body['repository']['id']).first()
    if repo == None:        
        repo = Repository()
        repo.repo_id = body['repository']['id']

    # In case the repository info has been changed
    repo.repo_name = body['repository']['full_name']
    repo.url = body['repository']['html_url']
    repo.save()
        
    # Unless it's a new repo, a commit triggered the webhook
    if 'head_commit' in body:   
        commit = Commit()
        commit.repository = repo
        commit.author_name = body['head_commit']['author']['name']
        commit.timestamp = body['head_commit']['timestamp']
        commit.commit_message = body['head_commit']['message']
        commit.commit_url = body['head_commit']['url']
        commit.hash = body['after']
        commit.save()

        run_test(commit)
        
    return Response({}, status=status.HTTP_200_OK)
