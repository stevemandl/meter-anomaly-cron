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

# AWS Serverless Application Model Framework Node Scheduled Cron on AWS

This project is for developing meter anomaly detection algorithms and scheduling them to run in AWS Lambda using the Serverless Application Model (SAM) framework.
The cronHandler function is invoked automatically according to the event schedule. The cronHandler calls anomaly detection functions with a single parameter: meter name. Which algorithms get called with which point names is determined by the configuration lists maintained at https://www.emcs.cornell.edu/MeterAnomalyConfig. 
The functions apply a specific anomaly detection algorithm, and return a description of the anomaly detected only if detection occurs. If no anomaly is detected, the algorithm should return falsy(false/False, null/None, or an empty string).


In below example, we use `cron` syntax to define `Schedule` event that will trigger our `cronHandler` function every hour

```yml
Resources:
  CronHandler:
    Type: AWS::Serverless::Function
    Properties:
      Handler: cron/handler.run
      Events:
        CloudWatchEvent:
          Type: Schedule
          Properties:
            Schedule: cron(0 * ? * * *)      
```

Detailed information about cron expressions in available in official [AWS docs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions).


## Usage

Use [git](https://github.com/git-guides/install-git) to clone a local copy of this repository. Development work should be done on dev branches associated with a repository issue. Please do not make changes to the dev or main branches. Ask Steve if you have questions about how to create, check out, commit changes, and push to dev branches.

Node and npm are required for testing javascript and typescript. See https://docs.npmjs.com/downloading-and-installing-node-js-and-npm for installation instructions.
### Install Dependencies

If developing in javascript or typescript, install node dependencies into the project directory from the base directory prior to use:
```
npm install
```

If developing in python, python 3.9 and pipenv are required
See https://github.com/pypa/pipenv#installation

Be sure to run 
```
pipenv install
```
from the py_src directory to set up your local environment.

### Tools
A code editor such as Visual Studio Code is recommended. See https://code.visualstudio.com/docs for information about vscode.

When working with AWS resources such as lambda functions, the AWS and AWS SAM CLI are useful. See https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html and https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

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
sam local invoke --event events/KlarmanSolar.json MeterAnomalyPY/PythonTemplate
```

After invocation, you should see output similar to:

```bash
Invoking python_template/handler.run (python3.9)                                                                                                                                                                                           
Local image is up-to-date                                                                                                                                                                                                                  
Using local image: public.ecr.aws/lambda/python:3.9-rapid-x86_64.                                                                                                                                                                          
                                                                                                                                                                                                                                           
Mounting /home/ec2-user/environment/meter-anomaly-cron/.aws-sam/build/MeterAnomalyPY/PythonTemplate as /var/task:ro,delegated, inside runtime container                                                                                    
END RequestId: 9c8e272c-4ba1-402a-bd05-4acb9546b0b0
REPORT RequestId: 9c8e272c-4ba1-402a-bd05-4acb9546b0b0  Init Duration: 0.03 ms  Duration: 447.82 ms     Billed Duration: 448 ms Memory Size: 128 MB     Max Memory Used: 128 MB
{"statusCode": 200, "body": ""}
```
The body of the response should contain the anomaly description, if detected, or an empty string if no anomaly is detected.

### Project directory structure
The project is organized by programming language: py_src/ contains python source code and ts_src/ contains typescript.

Each lambda function is in its own subdirectory of the source root. Test files are alongside the modules they are testing, named *.spec.ts or *spec.py.

```
.
├── ts_src                      # source root for typescript
|   ├── package.json            # npm package config
|   ├── package-lock.json       # npm config lockfile
|   ├── template.yaml           # SAM template for ts functions
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
|   ├── template.yaml           # SAM template for python functions
|   ├── pytest.ini              # pytest settings
|   ├── Pipfile                 # pipenv requirements
|   ├── Pipfile.lock            # generated by `pipenv lock`
│   ├── python_lib              # Shared code library for python
│   │   ├── utils.py            # Generic python helpers
│   │   └── utils_spec.py       # Tests for utilities
│   └── python_template         # Python template algorithm
│       ├── handler.py          # Entry point for python template lambda
│       └── handler_spec.py     # Tests for python template lambda
├── events                      # sample event json files used for local invocation
│   └── KlarmanSolar.json       # Event to test using Klarman hall solar electric meter
│
├── .gitignore                  # specifies untracked files that git should ignore
├── CODE_OF_CONDUCT.md          # Generic code of conduct for shared github repositories
├── CONTRIBUTING.md             # Contribution guidelines
├── template.yaml               # references to nested SAM Applications
└── README.md                   # If you're reading this, ...
```

