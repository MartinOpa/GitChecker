# GitChecker - a Codespeed-inspired Django web app

This project was created for my bachelor's thesis. It combines an endpoint for registering GitHub webhooks that notify the app of push events on the repo with custom test scripts that save test results in the JSON format. Upon receiving a notification from a tracked repo, the app clones the repo with the corresponding commit hash and runs the Python test script associated with that repo with various preset parameter sets, editable in the app itself. Any metrics that the tests save will be displayed in charts generated by the Bokeh library.

![alt text](https://github.com/MartinOpa/GitChecker/blob/main/sample_images/dark_theme.png?raw=true)
![alt text](https://github.com/MartinOpa/GitChecker/blob/main/sample_images/repo_detail.png?raw=true)
![alt text](https://github.com/MartinOpa/GitChecker/blob/main/sample_images/test_detail.png?raw=true)
![alt text](https://github.com/MartinOpa/GitChecker/blob/main/sample_images/commits.png?raw=true)
