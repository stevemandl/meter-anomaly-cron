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
    mocker.patch(
        "python_template.handler.fetch_trends",
        return_value={"data": [{"datapoints": []}]},
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