import json


def run(event, context):
    body = {
        "message": "Go Serverless v3.0! Your function executed successfully! There is an anomoly",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}
    # vipins NEW test comment

# forms the URL for the EMCS API that returns the json representation of an object


def emcsURL(point: str):
    return "https: // www.emcs.cornell.edu /${point}?api =${API_KEY} & cmd = json"
