import asyncio
from http.client import HTTPException
from unittest.mock import AsyncMock, MagicMock
from mizuki.file import File
import pytest
from mizuki.http import  Path , RateLimitBucket , HTTPClient
from mizuki.errors import HTTPException, Unauthorized, Forbidden, NotFound
from mizuki.http import  Path , RateLimitBucket , HTTPClient

def test_path_with_no_parameters():
    path = Path("GET", "gateway")
    assert path.url == "gateway"
 
def test_path_form():
    path = Path(
        "GET",
        "channels/{channel_id}",
        channel_id=123
    )

    assert path.url == "channels/123"


def test_path_url_encoding():
    path = Path(
        "GET",
        "users/{name}",
        name="hello world"
    )

    assert path.url == "users/hello%20world"

def test_bucket_key():
    path = Path(
        "GET",
        "channels/{channel_id}",
        channel_id=123
    )
    assert path._bucket_key == "GET:channels/{channel_id}+123"

#-----------------------------------------

def test_bucket_stores_initial_values():
    bucket = RateLimitBucket(5, 1.5)
    assert bucket.remaining == 5
    assert bucket.reset_after == 1.5

def test_bucket_has_a_lock():
    bucket = RateLimitBucket(5, 1.5)
    assert isinstance(bucket.lock, asyncio.Lock)

def test_update_bucket_reads_headers():
    bucket = RateLimitBucket(1, 0)
    resp = MagicMock()
    resp.headers = {
        "X-RateLimit-Remaining": "3",
        "X-RateLimit-Reset-After": "2.5",
    }
    bucket.update_bucket(resp)
    assert bucket.remaining == 3
    assert bucket.reset_after == 2.5

def test_update_bucket_when_headers_missing():
    bucket = RateLimitBucket(0, 0)
    resp = MagicMock()
    resp.headers = {}
    bucket.update_bucket(resp)
    assert bucket.remaining == 1
    assert bucket.reset_after == 0.1

def test_update_bucket_casts_types():
    bucket = RateLimitBucket(0, 0)
    resp = MagicMock()
    resp.headers = {
        "X-RateLimit-Remaining": "7",
        "X-RateLimit-Reset-After": "0.75",
    }
    bucket.update_bucket(resp)
    assert isinstance(bucket.remaining, int)
    assert isinstance(bucket.reset_after, float)

#-----------------------------------------
#Helper Functions
#Builds a fake aiohttp response usable as an async context manager.

def make_response(status=200, headers=None, json_data=None, content_type="application/json"):
    resp = MagicMock()
    resp.status = status
    base_headers = {"Content-Type": content_type}
    if headers:
        base_headers.update(headers)
    resp.headers = base_headers
    resp.json = AsyncMock(return_value=json_data if json_data is not None else {})
 
    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=False)
    return cm
 
 
def make_client_with_session(request_return_value):
    client = HTTPClient()
    session = MagicMock()
    session.request = MagicMock(return_value=request_return_value)
    client._session = session
    return client, session


#cm = context manager 

@pytest.mark.asyncio
async def test_request_raises_without_session():
    client = HTTPClient()
    path = Path("GET", "users/{user_id}", user_id=1)
    with pytest.raises(AssertionError):
        await client._request(path)

@pytest.mark.asyncio
async def test_successful_json_request_returns_data():
    resp_cm = make_response(status=200, json_data={"ok": True})
    client, session = make_client_with_session(resp_cm)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    result = await client._request(path)
 
    assert result == {"ok": True}
    session.request.assert_called_once_with("GET", "users/1")
 
 
@pytest.mark.asyncio
async def test_non_json_response_returns_none():
    resp_cm = make_response(status=200, content_type="text/plain", json_data={"ok": True})
    client, _ = make_client_with_session(resp_cm)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    result = await client._request(path)
 
    assert result is None
 
@pytest.mark.asyncio
async def test_request_records_new_bucket():
    resp_cm = make_response(
        status=200,
        headers={"X-RateLimit-Bucket": "bucket-abc", "X-RateLimit-Remaining": "4", "X-RateLimit-Reset-After": "1.0"},
        json_data={},
    )
    client, _ = make_client_with_session(resp_cm)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    await client._request(path)
 
    assert "bucket-abc" in client._buckets
    assert client._buckets["bucket-abc"].remaining == 4
    assert client._buckets_keys[path._bucket_key] == "bucket-abc"

@pytest.mark.asyncio
async def test_request_pre_sleeps_when_bucket_exhausted(monkeypatch):
    resp_cm = make_response(
        status=200,
        headers={"X-RateLimit-Bucket": "bucket-empty", "X-RateLimit-Remaining": "0", "X-RateLimit-Reset-After": "3.3"},
        json_data={},
    )
    client, _ = make_client_with_session(resp_cm)
 
    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    await client._request(path)
 
    sleep_mock.assert_awaited_once_with(3.3)
 
@pytest.mark.asyncio
async def test_401_raises_unauthorized():
    resp_cm = make_response(status=401, json_data={"message": "bad token"})
    client, _ = make_client_with_session(resp_cm)
    path = Path("GET", "users/{user_id}", user_id=1)
 
    with pytest.raises(Unauthorized):
        await client._request(path)
 
 
@pytest.mark.asyncio
async def test_403_raises_forbidden():
    resp_cm = make_response(status=403, json_data={"message": "no access"})
    client, _ = make_client_with_session(resp_cm)
    path = Path("GET", "users/{user_id}", user_id=1)
 
    with pytest.raises(Forbidden):
        await client._request(path)

@pytest.mark.asyncio
async def test_404_raises_not_found():
    resp_cm = make_response(status=404, json_data={"message": "missing"})
    client, _ = make_client_with_session(resp_cm)
    path = Path("GET", "users/{user_id}", user_id=1)
 
    with pytest.raises(NotFound):
        await client._request(path)
 
 
@pytest.mark.asyncio
async def test_other_4xx_raises_http_exception():
    resp_cm = make_response(status=418, json_data={"message": "teapot"})
    client, _ = make_client_with_session(resp_cm)
    path = Path("GET", "users/{user_id}", user_id=1)
 
    with pytest.raises(HTTPException):
        await client._request(path)
 
@pytest.mark.asyncio
async def test_429_retries_and_eventually_succeeds(monkeypatch):
    rate_limited_cm = make_response(
        status=429,
        json_data={"retry_after": 0.5},
        headers={"X-RateLimit-Scope": "user"},
    )
    success_cm = make_response(status=200, json_data={"ok": True})
 
    client, session = make_client_with_session(None)
    session.request.side_effect = [rate_limited_cm, success_cm]
 
    sleep_mock = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep_mock)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    result = await client._request(path)
 
    assert result == {"ok": True}
    sleep_mock.assert_awaited_once_with(0.5)
    assert session.request.call_count == 2
 
 
@pytest.mark.asyncio
async def test_global_429_clears_then_resets_event(monkeypatch):
    rate_limited_cm = make_response(
        status=429,
        json_data={"retry_after": 0.2},
        headers={"X-RateLimit-Scope": "global"},
    )
    success_cm = make_response(status=200, json_data={"ok": True})
 
    client, session = make_client_with_session(None)
    session.request.side_effect = [rate_limited_cm, success_cm]
 
    observed_state_during_sleep = {}
 
    async def fake_sleep(seconds):
        observed_state_during_sleep["was_cleared"] = not client._global_ratelimit.is_set()
 
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)
 
    path = Path("GET", "users/{user_id}", user_id=1)
    await client._request(path)
 
    assert observed_state_during_sleep["was_cleared"] is True
    assert client._global_ratelimit.is_set()  
 

 
@pytest.mark.asyncio
async def test_request_with_json_passes_through(monkeypatch):
    client = HTTPClient()
    captured = {}
 
    async def fake_request(self, path, **kwargs):
        captured.update(kwargs)
        return {"ok": True}
 
    
    monkeypatch.setattr(HTTPClient, "_request", fake_request)
 
    path = Path("POST", "channels/{channel_id}/messages", channel_id=1)

    await client.request(path, files=None, json={"content": "hi"})
 
    assert captured["json"] == {"content": "hi"}
    assert "data" not in captured
 
 
@pytest.mark.asyncio
async def test_request_with_files_builds_form_data(monkeypatch, tmp_path):
    file_path = tmp_path / "image.png"
    file_path.write_bytes(b"fake-bytes")
 
    client = HTTPClient()
    captured = {}
 
    async def fake_request(self, path, **kwargs):
        captured.update(kwargs)
        return {"ok": True}
 
    monkeypatch.setattr(HTTPClient, "_request", fake_request)
 
    path = Path("POST", "channels/{channel_id}/messages", channel_id=1)
    file = File(str(file_path), filename="image.png")
    await client.request(path, files=[file], json={"content": "hi"})
 
    assert "data" in captured
    assert "json" not in captured
 


