<!--
title: 'Meter Anomaly Cron scheduler'
description: 'This is a cron scheduler for running anomaly detection functions on a schedule, and compiling the anomalies into a report.'
layout: Doc
framework: v3
platform: AWS
language: nodeJS
priority: 1
authorName: 'Steve Mandl'
authorAvatar: 'https://secure.gravatar.com/avatar/d3fe459f8114ad905d54de551e44e4f0?s=800&d=identicon'
-->

# Serverless Framework Node Scheduled Cron on AWS

This project is for developing and deploying simple cron-like service running on AWS Lambda using the traditional Serverless framework. 
The cronHandler function is invoked automatically according to the event schedule. The cronHandler calls anomaly detection functions with a single parameter: meter name. Which algorithms get called with which point names is determined by the configuration lists maintained at https://www.emcs.cornell.edu/MeterAnomalyConfig. 
The functions apply a specific anomaly detection algorithm, and return a description of the anomaly detected only if detection occurs. If no anomaly is detected, the algorithm should return falsy(false/False, null/None, or an empty string).


In below example, we use `cron` syntax to define `schedule` event that will trigger our `cronHandler` function every second minute every Monday through Friday

```yml
functions:
  cronHandler:
    handler: handler.run
    events:
      - schedule: cron(0/2 * ? * MON-FRI *)
```

Detailed information about cron expressions in available in official [AWS docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions).


## Usage

Use [git](https://github.com/git-guides/install-git) to clone a local copy of this repository. Development work should be done on dev branches associated with a repository issue. Please do not make changes to the dev or main branches. Ask Steve if you have questions about how to create, check out, commit changes, and push to dev branches.

Node and npm are required for testing javascript, typescript, and for using the serverless framework. See https://docs.npmjs.com/downloading-and-installing-node-js-and-npm for installation instructions.
### Install Dependencies
Serverless framework is only required for local invocation and offline emulation of lambda functions. See https://www.serverless.com/console/docs (Development and testing of algorithms can be done without serverless.)

Install serverless globally (these instructions depend on npm. If you wish to install serverless using another package manager, consult the serverless docs.):
```
npm i -g serverless
```
Install other dependencies into the project directory from the base directory prior to use:
```
npm install
```

If developing in python, python 3.8 and pipenv are required
See https://github.com/pypa/pipenv#installation

Be sure to run 
```
pipenv install
```
from the py_src directory to set up your local environment.

### Tools
A code editor such as Visual Studio Code is recommended. See https://code.visualstudio.com/docs for information about vscode.

When working with AWS resources such as lambda functions, the AWS CLI is useful. See https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html 

### Testing
Run the npm test suite for js and ts source code:
```
cd ts_src
npm test
```
Run pytest for python source code:
```
cd py_src
pipenv run pytest
```

### Developing new algorithms
 - Start by creating an issue in the GitHub repository to track the development. Assign any developers that will be working on the issue tasks. 
 - A development branch should be created for the issue automatically. Once you are ready to actively work on the issue, label it as https://github.com/stevemandl/meter-anomaly-cron/labels/WIP.
 - After checking out an issue branch in your local repository, create a new directory for the algorithm handler. The ts_src/testTemplate/ and py_src/python_template/ directories are designed to be copied into a new directory and modified 
with the implementation of the new algorithm. The testTemplate is typescript, the python_template is python; either language can be used to create a new function. All python source should remain in the py_src/ directory and all typescript should remain in ts_src/. For example, the following command would copy the python template into a new subdirectory of py_src:
```
:~/temp/meter-anomaly-cron/py_src$ cp -r python_template/ 16-test-algorithm/
```
 - The spec file should test the function in the same directory, and should provide at least 90% test coverage as a rule of thumb. It is a good practice to periodically commit and push your changes to github to back up your code.
 - Once ready for review, push all code to the issue branch, and label the issue as https://github.com/stevemandl/meter-anomaly-cron/labels/review.
 - To deploy, a new function will need to be added to the corresponding (py_src or ts_src) serverless.yml and an entry added to the algorithms array in the root handler. Steve can help with this.
 - In order to apply the algorithms to points, an object list will need to be created in the EMCS (named MeterAnomaly.[function].PointList) with the corresponding points.
### Deployment

This project made to deploy with the Github CI/CD framework. Testing actions are automatically run against dev branches on push events. Deployment to AWS lambda is automatically run on merges into the dev or main branches.

### Local invocation

To call a python function locally without the sls framework, an invoke.py utility has been provided. Usage is available by executing
```bash
~/meter-anomaly-cron/py_src$ pipenv run ./invoke.py -h
```
you can invoke them from the py_src directory with a command similar to the following:
```bash
~/meter-anomaly-cron/py_src$ pipenv run ./invoke.py -t 1676005200 python_template/handler.run Foundry.STM.M23/MassFlow

invoke.py arguments:
    function: python_template/handler.run, pointName: Foundry.STM.M23/MassFlow, timeStamp: 1676005200 
Calling function ...
Received response: '{'statusCode': 200, 'body': 'Foundry.STM.M23/MassFlow is missing more than 10% of values for the period 2023-01-11 00:00 to 2023-02-10 00:00'}'
Algorithm executed without an error
ANOMALY DETECTED: Foundry.STM.M23/MassFlow is missing more than 10% of values for the period 2023-01-11 00:00 to 2023-02-10 00:00
Elapsed time (seconds): '0.453'.
```

In order to invoke lambda functions locally, you can invoke them from the py_src or ts_src/ directory with a command similar to the following:

```
sls invoke local --function pythonTemplate --data '{"body": {"pointName": "AppelCommons.CW.FP/TONS", "timeStamp": "2022-11-17"}}'
```

After invocation, you should see output similar to:

```bash
Running "serverless" from node_modules
testTemplate run at 2022-11-18 13:52:38.354892 with event {'body': {'pointName': 'AppelCommons.CW.FP/TONS', 'timeStamp': '2022-11-17'}}

{
    "statusCode": 200,
    "body": ""
}

```
The body of the response should contain the anomaly description, if detected, or an empty string if no anomaly is detected.
### Offline emulation

If you want to invoke your functions through a lambda-like endpoint from a client that would be making webservice requests to the API gateway, use the following command start the python service (i.e. all functions written in python) from the project root:

```bash
$ serverless meter-anomaly-py:offline
```

After starting serverless offline, you should see output like:

```
Running "serverless" from node_modules

Starting Offline at stage dev (us-east-1)

Offline [http for lambda] listening on http://localhost:3002
Function names exposed for local invocation by aws-sdk:
           * pythonTemplate: meter-anomaly-py-dev-pythonTemplate
```

Then you should be able to send a request from a separate terminal to the offline service like this:
```bash
$ aws lambda invoke --endpoint-url http://localhost:3002 --function-name meter-anomaly-py-dev-pythonTemplate --payload '{"body": { "pointName": "AppelCommons.CW.FP/TONS" }}' response.json
```
The response will be written to the file response.json as specified.

### Project directory structure
The project is organized by programming language: py_src/ contains python source code and ts_src/ contains typescript.

Each lambda function is in its own subdirectory of the source root. Test files are alongside the modules they are testing, named *.spec.ts or *spec.py.

```
.
├── ts_src                      # source root for typescript
|   ├── package.json            # npm package config
|   ├── package-lock.json       # npm config lockfile
|   ├── serverless.yml          # Serverless service file for typescript functions
|   ├── tsconfig.json           # Typescript compiler configuration
|   ├── types.ts                # Typescript types
│   ├── tslib                   # Shared code library for typescript
│   │   └── utils.ts            # Generic typescript helpers
│   ├── testTemplate            
│   │   ├── handler.ts          # Entry point for typescript template lambda
│   │   └── handler.spec.ts     # Tests for typescript template lambda
│   └── cron
│       ├── handler.ts          # Entry point for typescript cron lambda
│       └── handler.spec.ts     # Tests for typescript cron lambda
|
├── py_src                      # source root for typescript
|   ├── serverless.yml          # Serverless service file for python functions
|   ├── pytest.ini              # pytest settings
|   ├── Pipfile                 # pipenv requirements
|   ├── Pipfile.lock            # generated by `pipenv lock`
│   ├── python_lib              # Shared code library for python
│   │   ├── utils.py            # Generic python helpers
│   │   └── utils_spec.py       # Tests for utilities
│   └── python_template         # Python template algorithm
│       ├── handler.py          # Entry point for python template lambda
│       └── handler_spec.py     # Tests for python template lambda
│
├── .gitignore                  # specifies untracked files that git should ignore
├── CODE_OF_CONDUCT.md          # Generic code of conduct for shared github repositories
├── CONTRIBUTING.md             # Contribution guidelines
└── README.md                   # If you're reading this, ...
```

