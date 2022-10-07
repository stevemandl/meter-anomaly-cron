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

This project is for developing and deploying simple cron-like service running on AWS Lambda using the traditional Serverless Framework.

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

### Deployment

This project made to deploy work with the Github CI/CD framework. 

### Local invocation

In order to test out your functions locally, you can invoke them with the following command:

```
serverless invoke local --function rateHandler
```

After invocation, you should see output similar to:

```bash
Your cron function "aws-node-scheduled-cron-dev-rateHandler" ran at Fri Mar 05 2021 15:14:39 GMT+0100 (Central European Standard Time)
```

### Offline emulation

If you want to invoke your functions through a lambda-like endpoint from a client that would be making webservice requests to the API gateway, use:

```bash
$ serverless offline
```

After starting, you should see output like:

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
Remember to use 'x-api-key' on the request headers.
Key with token: 'd41d8cd98f00b204e9800998ecf8427e'

   ┌───────────────────────────────────────────────────────────────────────────────────────┐
   │                                                                                       │
   │   POST | http://localhost:3000/dev/testTemplate                                       │
   │   POST | http://localhost:3000/2015-03-31/functions/testTemplateHandler/invocations   │
   │                                                                                       │
   └───────────────────────────────────────────────────────────────────────────────────────┘

Server ready: http://localhost:3000 🚀
```

Then you should be able to send a request to the offline service like this:
```bash
$ curl -X POST http://localhost:3000/dev/testTemplate -H 'x-api-key: dev-yqiOpWb6095s097Roybo2793yHXGNWFx6oWCVvvv'  \
-d '{"pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System"}'
```