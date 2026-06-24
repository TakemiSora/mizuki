from mizuki.http import  Path 

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

def test_route_key():
    path = Path(
        "GET",
        "channels/{channel_id}",
        channel_id=123
    )

    assert path._route_key == "GET:channels/{channel_id}"
