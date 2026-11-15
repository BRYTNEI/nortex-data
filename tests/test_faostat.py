from unittest.mock import Mock

import requests

from nortex_data.sources import faostat


def test_faostat_reauthenticates_and_retries(monkeypatch):
    monkeypatch.setattr(faostat, "load_dotenv", lambda: None)
    monkeypatch.setenv("FAOSTAT_TOKEN", "old")
    monkeypatch.setenv("FAOSTAT_USERNAME", "demo")
    monkeypatch.setenv("FAOSTAT_PASSWORD", "example")
    denied = requests.Response()
    denied.status_code = 401
    request = Mock(side_effect=[
        requests.HTTPError(response=denied),
        Mock(**{"json.return_value": {"AccessToken": "new"}}),
        Mock(**{"json.return_value": {"data": [{"code": "1"}]}}),
    ])
    monkeypatch.setattr(faostat, "request", request)
    client = faostat._Client({"login": "https://example.test/auth/login", "endpoint": "https://example.test/en"})
    assert client.get("dimensions/QCL/") == [{"code": "1"}]
    assert request.call_args_list[0].kwargs["headers"]["Authorization"] == "Bearer old"
    assert request.call_args_list[2].kwargs["headers"]["Authorization"] == "Bearer new"
