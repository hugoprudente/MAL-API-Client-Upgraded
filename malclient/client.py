import re
import secrets
import os
import datetime
import logging
from typing import Optional
import platform
from urllib.parse import urlencode

from .request_handler import APICaller
from .anime import Anime
from .my_list import MyList
from .manga import Manga
from .industry import Industry
from .exceptions import AuthorizationError
from .boards import Boards
from .urls import MalApiVersion, MAL_OAUTH_BASE, oauth_authorize_url, rest_base_url

__all__ = ['Client', 'setup_logging', 'generate_authorization_url', 'fetch_token_schema_2']


def generate_authorization_url(client_id: str, *,
                               code_verifier: Optional[str] = None,
                               redirect_uri: Optional[str] = None) -> tuple[str, str]:
    if code_verifier is None:
        token = secrets.token_urlsafe(100)
        code_verifier = code_challenge = token[:128]

    assert 48 <= len(code_verifier) <= 128

    params = urlencode({
        "response_type": "code",
        "client_id": client_id,
        "state": "RequestID42",
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
        "redirect_uri": redirect_uri or "",
    })
    authorization_url = f"{oauth_authorize_url()}?{params}"
    return authorization_url, code_verifier


def fetch_token_schema_2(client_id: str,
                        client_secret: str,
                        code_verifier: str,
                        code: str,
                        redirect_uri: Optional[str] = None) -> dict[str, str]:
    """

    Helper function to generate access token **do not use this to refresh token**
    Function follows MAL auth schema 2

    :ivar str client_id: your client id (available on myanimelist developer page)
    :ivar str client_secret: your client secret (available on myanimelist developer page)
    :return: Freshly generated Access Token for your client
    :rtype: dict[str, str]
    """

    base_url = f"{MAL_OAUTH_BASE}/"
    uri = "oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    api_handler = APICaller(base_url=base_url, headers=headers)
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "code_verifier": code_verifier,
        "grant_type": "authorization_code",
        'redirect_uri': redirect_uri,
    }
    return api_handler.call(uri=uri, method="post", data=data)


def setup_logging(*, format: str = None, filename: str = None, log_level: int = logging.INFO):
    """
    This is helper function for setting up request logging, all parameters are optional and function may be executed as is
    :param str format: Python Logging library format in which each event will be logged
    :param str filename: filename under which log will be saved, default if malclient_log_{date}.log
    :param log_level: Messages which are less severe than log-level will be ignored, most request have level INFO
    """
    if format is None:
        format = "%(levelname)s | %(asctime)s | %(message)s"
    now = datetime.datetime.now()
    if filename is None:
        filename = f"malclient_log_{now.strftime('%Y-%m-%d_%H-%M')}.log"
    logging.basicConfig(filename=filename, level=log_level, format=format)


class Client(Anime, Manga, MyList, Boards, Industry):
    """

    Base class for interacting with MyAnimeList REST API

    :ivar client_id: string containing client_id obtained from [client configuration on MAL](https://myanimelist.net/apiconfig)
    :ivar access_token: string containing access token obtained through OAuth2
    :ivar refresh_token: string containing refresh token obtained through OAuth2
  """
    def __init__(
        self,
        *,
        client_id: str = None,
        access_token: str = None,
        refresh_token: str = None,
        nsfw: bool = False,
        api_version: MalApiVersion = "v2",
    ):
        self.nsfw = nsfw
        self._api_version = api_version
        self._base_url = rest_base_url(api_version)
        self._bearer_token = access_token
        self._client_id = client_id
        self.refresh_token = refresh_token
        self.authorized = False
        self._api_handler = None
        self.headers = {}
        self._connect_to_api()

    @property
    def api_version(self) -> MalApiVersion:
        return self._api_version

    @property
    def rest_base_url(self) -> str:
        return self._base_url

    @classmethod
    def generate_new_token(cls, client_id: str, client_secret: str, *, code_verifier: str = None, redirect_uri: Optional[str] = None, api_version: MalApiVersion = "v2"):
        auth_url, code_verifier = generate_authorization_url(client_id, code_verifier=code_verifier, redirect_uri=redirect_uri)
        if 'windows' in platform.system().lower():
            os.system(f"explorer \"{auth_url}\"")
        elif 'darwin' in platform.system().lower():
            os.system(f"open \"{auth_url}\"")
        elif 'linux' in platform.system().lower():
            os.system(f"xdg-open \"{auth_url}\"")
        print(f"If opening url failed enter it manually into your browser:\n{auth_url}")
        code_url = input("Paste url you were redirected to\n")
        code = re.search(r"(?<=code=)(\w+)", code_url).group()

        data = fetch_token_schema_2(client_id, client_secret, code_verifier, code, redirect_uri)
        return cls(access_token=data['access_token'], refresh_token=data['refresh_token'], api_version=api_version)

    def _connect_to_api(self):
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        if self._bearer_token is not None:
            self.headers['Authorization'] = f'Bearer {self._bearer_token}'
            self.authorized = True
        elif self._client_id is not None:
            self.headers['X-MAL-CLIENT-ID'] = self._client_id
        else:
            raise AuthorizationError()

        self._api_handler = APICaller(base_url=self._base_url, headers=self.headers)

    def refresh_bearer_token(self,
                             client_id: str,
                             client_secret: str,
                             refresh_token: str,
                             print_response: bool = True) -> None:
        """

        Function to automatically refresh your clients bearer token (as for now there is no such thing as lifetime token)

        :param str client_id: Your client id number
        :param str client_secret: Your client secret
        :param str refresh_token: Your refresh token
        :param bool print_response: Should the response json be printed or not
        """
        base_url = f"{MAL_OAUTH_BASE}/"
        uri = "oauth2/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        api_handler = APICaller(base_url=base_url, headers=headers)
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        }

        response = api_handler.call(uri=uri, method="post", data=data)
        if print_response:
            print("Refreshing token with client id and secret:")
            print(response)
        self._bearer_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Bearer {response["access_token"]}',
        }
        if self._client_id is not None:
            self.headers['X-MAL-CLIENT-ID'] = self._client_id
        self._api_handler = APICaller(base_url=self._base_url, headers=self.headers)