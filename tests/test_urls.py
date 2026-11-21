import malclient
from malclient.urls import oauth_authorize_url, oauth_token_url, rest_base_url


def test_rest_base_url_v2():
    assert rest_base_url("v2") == "https://api.myanimelist.net/v2/"


def test_rest_base_url_v1():
    assert rest_base_url("v1") == "https://api.myanimelist.net/v1/"


def test_client_default_api_version():
    client = malclient.Client(access_token="token")
    assert client.api_version == "v2"
    assert client.rest_base_url == "https://api.myanimelist.net/v2/"


def test_client_api_version_v1():
    client = malclient.Client(client_id="cid", api_version="v1")
    assert client.api_version == "v1"
    assert client.rest_base_url == "https://api.myanimelist.net/v1/"


def test_oauth_urls():
    assert oauth_authorize_url().startswith("https://myanimelist.net/v1/oauth2/")
    assert oauth_token_url() == "https://myanimelist.net/v1/oauth2/token"