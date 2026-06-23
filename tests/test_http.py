import pytest
from mizuki.http import HTTPClient, Path, RateLimitBucket

def test_pathwithnoparameters():
    path = Path("GET", "gateway")
    assert path.url == "gateway"
 
 #This checks the no parameter tesr case 



def test_pathform():
    path = Path(
        "GET",
        "channels/{channel_id}",
        channel_id=123
    )

    assert path.url == "channels/123"


#Checks the formate of the path  
def test_pathstring():
    path = Path(
        "GET",
        "users/{name}",
        name="hello world"
    )

    assert path.url == "users/hello%20world"
#If the path is a string it should be formated correctly with the url encoding

def test_route():
    path = Path(
        "GET",
        "channels/{channel_id}",
        channel_id=123
    )

    assert path._route_key.startswith("GET:")
#Checks the route key starts with the method and a colon