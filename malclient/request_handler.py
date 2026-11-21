import datetime
import json
import logging

import requests

from .exceptions import (
    APIException,
    BadRequest,
    Forbidden,
    NotFound,
    Unauthorized,
)

__all__ = ['APICaller']

DEFAULT_TIMEOUT = 30


class APICaller(object):
    def __init__(self, base_url, headers, *, timeout: float = DEFAULT_TIMEOUT):
        self._base_url = base_url
        self._headers = headers
        self._timeout = timeout

    def call(self, uri, method="get", params=None, *args, **kwargs):
        requester = getattr(requests, method.lower())
        url = self._base_url + uri
        kwargs.setdefault("timeout", self._timeout)
        logging.info(f"{method.upper()} {url} Query Parameters: {params}")
        response = requester(
            url=url,
            headers=self._headers,
            params=params,
            *args,
            **kwargs,
        )
        if response.status_code < 400:
            response = self._parse_response(response, method)
        elif 400 <= response.status_code:
            self._parse_error(response, method, url)
        return response

    def _parse_response(self, response, method):
        if method in ["get", "post", "patch", "put"]:
            response_json = response.json()
            response_json = self._parse_json(response_json)
            return response_json

        elif method == "delete":
            return response.status_code

    def _parse_json(self, json_obj):
        """
        This is main function that handles whole logic of parsing json response from MAL API.
        It is a little bit messy, so it is heavily commented for better understanding.

        :param json_obj: json object to parse
        """
        if isinstance(json_obj, list):
            list_response = []
            for item in json_obj:
                new_dict = self._parse_json(item)
                list_response.append(new_dict if new_dict != {} else item)
            return list_response

        elif isinstance(json_obj, dict):
            new_dict = json_obj.copy()

            if "node" in json_obj:
                new_dict = new_dict | json_obj['node']
                for k, v in new_dict.items():
                    if isinstance(v, dict) and "node" in v and len(v) == 1:
                        new_dict[k] = new_dict[k]['node']

            if "list_status" in json_obj:
                new_dict = new_dict | {'list_status': json_obj['list_status']}

            if "ranking" in json_obj:
                new_dict = new_dict | {'ranking': json_obj['ranking']}

            if "role" in json_obj:
                new_dict = new_dict | {'role': json_obj['role']}

            if json_obj and "data" in json_obj:
                list_response = self._parse_json(json_obj["data"])
                if "paging" in json_obj:
                    json_obj = {"data": list_response, "paging": json_obj["paging"]}
                return json_obj

            if "animeography" in json_obj:
                response_json = json_obj | {'animeography': self._parse_json(json_obj['animeography'])}
                return response_json
            return new_dict

    @staticmethod
    def _error_body(response) -> dict:
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return {}

    @staticmethod
    def _parse_error(response, method, url):
        body = APICaller._error_body(response)
        error = body.get("error", "")
        message = body.get("message", response.text or "")
        logging.error(f"{method.upper()} {url} {response.status_code} {error}: {message}")
        if response.status_code == 400:
            raise BadRequest(response)
        elif response.status_code == 401:
            raise Unauthorized(response)
        elif response.status_code == 403:
            raise Forbidden(response)
        elif response.status_code == 404:
            raise NotFound(response)
        else:
            raise APIException(response.status_code, message, response)