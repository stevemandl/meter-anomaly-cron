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
The service passes anomaly detection functions meter names that have been configured to run with these functions. 
The functions apply a specific anomaly detection algorithm, and return a description of the anomaly detected only if detection occurs.


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

Use git to clone a local copy of this repository. Development work should be done on dev branches associated with a repository issue. Please do not make changes to the dev or main branches. Ask Steve if you have questions about how to create, check out, commit changes, and push to dev branches.

Node and npm are required for testing javascript and typescript code. See https://docs.npmjs.com/downloading-and-installing-node-js-and-npm for installation instructions.
### Install Dependencies
Serverless framework is required for local invocation and offline emulation. See https://www.serverless.com/console/docs

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
### Tools
A code editor such as Visual Studio Code is recommended. See https://code.visualstudio.com/docs for information about vscode.

When working with AWS resources, the AWS CLI is useful. See https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html 

### Testing
Run the npm test suite for js and ts source code:
```
npm test
```
### Developing new algorithms
 - Start by creating an issue in the repo to track the development. Assign any developers that will be working on the issue tasks. 
 - Create a dev branch from the issue and check out this branch in your development environment.
 - From a dev branch, create a new directory for the algorithm handler. The testTemplate/* and python_template/* are designed to be copied into a new directory and modified 
with the implementation of the new algorithm. The testTemplate is typescript, the python_template is python; either language can be used to create a new function.
 - The spec/test file should test the function in the same directory, and should provide at least 90% test coverage as a rule of thumb. 
 - Once ready for review, push all code to the dev branch, and label the issue as review.
 - To deploy, a new function will need to be added to the serverless.yml and an entry added to the algorithms array in the root handler. 
 - In order to apply the algorithms to points, an object list will need to be created in the EMCS with the corresponding points.
### Deployment

This project made to deploy with the Github CI/CD framework. Testing actions are automatically run against dev branches on push events. Deployment is automatically run on merges into the dev or main branches.

### Local invocation

In order to test out your functions locally, you can invoke them with the following command:

```
serverless invoke local --function cronHandler
```

After invocation, you should see output similar to:

```bash
Running "serverless" from node_modules
Compiling with Typescript...
Using local tsconfig.json - tsconfig.json
Typescript compiled.
Handler ran at Fri Oct 07 2022 09:07:22 GMT-0400 (Eastern Daylight Time)
Report:
 testTemplate: MannLibrary.STM.M22-V/AverageMassFlow has no data for the period Wed Sep 07 2022 13:07:19 GMT+0000 (Coordinated Universal Time) to Fri Oct 07 2022 13:07:19 GMT+0000 (Coordinated Universal Time)

```

### Offline emulation

If you want to invoke your functions through a lambda-like endpoint from a client that would be making webservice requests to the API gateway, use:

```bash
$ serverless offline
```

After starting serverless offline, you should see output like:

```
Running "serverless" from node_modules
Compiling with Typescript...
Using local tsconfig.json - tsconfig.json
Typescript compiled.
Watching typescript files...

Starting Offline at stage dev (us-east-1)

Offline [http for lambda] listening on http://localhost:3002
Function names exposed for local invocation by aws-sdk:
           * cronHandler: meter-anomaly-cron-dev-cronHandler
           * testTemplateHandler: meter-anomaly-cron-dev-testTemplateHandler
Scheduling [cronHandler] cron: [0 * ? * *]
```

Then you should be able to send a request from a separate terminal to the offline service like this:
```bash
$ aws lambda invoke --endpoint-url http://localhost:3002 --function-name meter-anomaly-cron-dev-testTemplateHandler --payload '{"body": { "pointName": "AppelCommons.CW.FP/TONS" }}' response.json
```

### Project directory structure
The project is organized by programming language: py_src contains python sourcecode and ts_src contains typescript.

Each lambda function is in its own subdirectory of the source root. Test files are alongside the modules they are testing, named *.spec.ts or *spec.py.
Additionally, there are common directories for shared code in tslib and python_lib:

- `tslib` - containing shared code base between typescript lambda functions
- `python_lib` - containing shared code base between python lambda functions

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

