import json


def run(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully! There is an anomoly",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
    #vipins NEW test comment