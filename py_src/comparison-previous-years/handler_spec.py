from python_template.handler import run
from requests.exceptions import HTTPError
from requests.models import Response


def test_nobarf(mocker):
    event = {
        "body": {
            "pointName": "KlarmanHall.Elec.Solar.PowerScout3037/kW_System",
            "timeStamp": "2022-10-05T23:58:47.390Z",
        }
    }
    """
    Note from Steve: This should match the order your algorithm calls fetch_trends, and you will want 
    to replace the datapoints with something you actually want to test your algorithm with, such as 
    actual data you collect from a known anomaly
    """
    mocker.patch(
        "python_template.handler.fetch_trends",
        side_effect=[
            {
                "data": [
                    {
                        "datapoints": [
                            [28.313975, 1685577600000],
                            [26.4299, 1685581200000],
                            [26.1045, 1685584800000]
                        ]
                    }
                ]
            },
            {
                "data": [
                    {
                        "datapoints": [
                            [48.600675, 1654041600000],
                            [45.799775, 1654045200000],
                            [46.109575, 1654048800000]
                        ]
                    }
                ]
            },
        ],
    )
    result = run(event, None)
    assert "statusCode" in result
    assert "missing" in result.get("body")


def test_handle400(mocker):
    r = Response()
    r.status_code = 400
    r._content = b'{"error":"No data"}'
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "no data" in result.get("body")


def test_barf(mocker):
    r = Response()
    r.status_code = 400
    r._content = b"qwerty"
    mocker.patch(
        "python_template.handler.fetch_trends", side_effect=HTTPError(response=r)
    )
    event = {"body": {"pointName": "foo"}}
    result = run(event, None)
    assert "statusCode" in result
    assert "qwerty" in result.get("body")