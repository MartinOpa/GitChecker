import os
import subprocess
import shutil
import json
import datetime
from .models import Commit, Repository, Test, TestParameters
from django.utils import timezone

class LogNotFoundException(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

# Check out repo @commit
def checkout_repo(repo_url, dest_dir, commit_hash):
    subprocess.run(['git', 'init', dest_dir])
    subprocess.run(['git', '-C', dest_dir, 'remote', 'add', 'origin', repo_url])
    subprocess.run(['git', '-C', dest_dir, 'fetch', '--depth=1', 'origin', commit_hash])
    subprocess.run(['git', '-C', dest_dir, 'checkout', commit_hash])

# Create virtual environment
def create_virtualenv(venv_dir, versions):
    for version in versions:  
        #magorina, nejde, verze pythonu uz musi existovat
        #subprocess.run(['sudo', 'dnf', 'install', f'{version}'])
        subprocess.run([f'{version}', '-m', 'venv', f'{venv_dir}{version}'])

# Get dependencies
def install_requirements(venv_dir, dest_dir, versions, test_dir):
    result = {}
    for version in versions:  
        subprocess.run([os.path.join(f'{venv_dir}{version}', 'bin', f'{version}'), '-m', 'pip', 'install', '--upgrade', 'pip'])
        #subprocess.run([os.path.join(venv_dir, 'bin', 'python3'), '-m', 'pip', 'install', 'pytest', 'requests', 'pytest-reportlog'])
        output = subprocess.run([os.path.join(f'{venv_dir}{version}', 'bin', 'pip'), 'install', '-r', os.path.join(dest_dir, test_dir, 'requirements.txt')], capture_output=True, text=True)
        if output and output.stdout:
            result[version] = (output.returncode, output.stdout + '\n' + output.stderr)
        else:
            result[version] = (output.returncode, 'No output captured')

    return result
            

# Parse json parameters
def parse_params(parameters):
    param_str = ''
    try:
        for param, value in parameters.items():
            param_str += f'--{param} {value} '
    except:
        return ''

    return param_str

# Run tests, get full output
def run_tests(venv_dir, dest_dir, repo, param, parsed_params):
    activate_script = os.path.join(f'{venv_dir}{param.version}', 'bin', 'activate')
    #subprocess.run(f'bash -c "source {activate_script} && pytest {dest_dir}/tests.py -v --report-log={log_file}"', shell=True)
    output = subprocess.run(f'bash -c "source {activate_script} && cd {os.path.join(dest_dir, repo.test_dir)} && {param.version} {repo.test_command} {parsed_params}"',
                            shell=True, capture_output=True, text=True)
    if output and output.stdout:
        return (output.stdout + '\n' + output.stderr, output.returncode)
    else:
        return None

# Persist result data
def parse_results(log, commit, param, results_path):
    test = Test()
    test.commit = commit
    test.repository = commit.repository
    test.params = param
    test.timestamp = timezone.now()

    # Check for errors
    err = '' if log[1] == 0 else 'Non-zero exit code'
    test.summary = json.dumps(f'["{err}{param.version}"]')

    if err == '':
        try:
            with open(results_path, 'r') as file:
                data = json.load(file)

            test.summary = json.dumps(data)
        except:
            test.summary = json.dumps(f'["Problem loading test result file"]')

    # Parse stdout
    log_lines = {str(i+1): line for i, line in enumerate(log[0].split('\n'))}
    test.detailed = json.dumps(log_lines)

    test.save()

# Clean up after everything is done
def clean_up(dir):
    try:
        shutil.rmtree(dir) 
    except:
        pass

# Save test result with error message + log
def save_with_err(commit, param, err, case):
    test = Test()
    test.commit = commit
    test.repository = commit.repository
    test.params = param
    test.timestamp = timezone.now()

    test.summary = json.dumps(f'["Encountered an error during {case}"]')

    log_lines = {str(i+1): line for i, line in enumerate(err.split('\n'))}
    test.detailed = json.dumps(log_lines)

    test.save()


# Function called from GitHub webhook or manually
def run_test(commit=None):
    if not commit:
        commit = Commit.objects.latest('timestamp')
        if not commit:
            return

    test_path = 'tests'
    repo = commit.repository
    dest_dir = os.path.join(test_path, commit.hash)
    venv_dir = os.path.join(dest_dir, 'env')

    versions = []
    params = TestParameters.objects.filter(repository=repo)
    for param in params:
        if param.version not in versions:
            versions.append(param.version)

    try:
        checkout_repo(repo.url, dest_dir, commit.hash)
        create_virtualenv(venv_dir, versions)
        clean_versions = install_requirements(venv_dir, dest_dir, versions, repo.test_dir)

        for param in params:
            try:
                if clean_versions[param.version][0] != 0:
                    save_with_err(commit, param, clean_versions[param.version][1], 'instalation')
                    continue

                results_path = os.path.join(dest_dir, f'{repo.test_dir}', f'{param.param_name}_test_results.json')
                parsed_params = parse_params(param.parameters) + f'--test_results {param.param_name}_test_results.json'
                log = run_tests(venv_dir, dest_dir, repo, param, parsed_params)
                if log:
                    parse_results(log, commit, param, results_path)
                else:
                    raise LogNotFoundException()
            except Exception as e:
                save_with_err(commit, param, repr(e), 'execution')
    except:
        # error?
        pass
    finally:
        clean_up(dest_dir)
