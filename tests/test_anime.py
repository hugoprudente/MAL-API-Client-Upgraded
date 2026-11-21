from unittest import mock

import malclient
import pytest

from malclient.Datamodels import Season, Fields, SeasonalAnimeSorting, AnimeObject

ANIME_RESPONSE = {
    "id": 1,
    "title": "anime title",
    "main_picture": {"medium": "https://url/1", "large": "https://url/2"},
    "alternative_titles": {"synonyms": ["another title"], "en": "", "ja": "別の名前"},
    "start_date": "2022-07-20",
    "end_date": "2022-07-20",
    "synopsis": "synopsis",
    "mean": "3.2",
    "rank": 345,
    "popularity": 10,
    "num_list_users": 10,
    "average_episode_duration": 2400,
    "my_list_status": {
        "status": "plan_to_watch",
        "score": 0,
        "num_episodes_watched": 0,
        "is_rewatching": False,
        "updated_at": "2022-04-03T22:48:25+00:00",
    },
    "broadcast": {"day_of_the_week": "saturday", "start_time": "23:30"},
    "num_scoring_users": 3,
    "rating": "pg_13",
    "nsfw": "white",
    "created_at": "2021-08-08T15:50:11+00:00",
    "updated_at": "2022-03-31T08:40:54+00:00",
    "media_type": "ona",
    "status": "not_yet_aired",
    "genres": [{"id": 1, "name": "Action"}],
    "num_episodes": 0,
    "start_season": {"year": 2022, "season": "summer"},
    "source": "novel",
    "studios": [{"id": 1, "name": "a studio"}],
}


def mocked_api_call(*args, **kwargs):
    uri = kwargs.get("uri", "")
    if not uri and len(args) >= 2:
        uri = args[1]
    elif not uri and args:
        uri = args[0]
    if "anime/season" in uri:
        return {"data": [ANIME_RESPONSE], "paging": {"next": "https://mock-next"}}
    raise malclient.NotFound("mock 404")


@pytest.fixture
def client():
    return malclient.Client(access_token="a_random_token", nsfw=True)


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_season_fail(mock_call, client):
    with pytest.raises(ValueError):
        client.get_seasonal_anime("summmer", 2022, limit=1)


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_fields(mock_call, client):
    response = client.get_seasonal_anime("summer", 2022, limit=1)
    payload_keys = set(response[0].model_dump().keys())
    for field in Fields.anime().to_payload().split(","):
        if "{" in field or "}" in field:
            continue
        if field not in (
            "pictures",
            "background",
            "related_anime",
            "related_manga",
            "recommendations",
            "opening_theme",
            "ending_theme",
        ):
            assert field in payload_keys


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_season_str_success(mock_call, client):
    response = client.get_seasonal_anime("summer", 2022, limit=1)
    assert len(response) == 1
    assert isinstance(response[0], AnimeObject)
    assert response[0].id == 1
    assert response[0].mean == 3.2


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_season_obj_success(mock_call, client):
    response = client.get_seasonal_anime(Season.SUMMER, 2022, limit=1)
    assert response[0].title == "anime title"


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_sort_str_fail(mock_call, client):
    with pytest.raises(ValueError):
        client.get_seasonal_anime(Season.SUMMER, 2022, sort="anime", limit=1)


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_sort_str_success(mock_call, client):
    response = client.get_seasonal_anime(
        Season.SUMMER, 2022, sort="anime_score", limit=1
    )
    assert response[0].id == 1


@mock.patch("malclient.request_handler.APICaller.call", side_effect=mocked_api_call)
def test_get_seasonal_anime_sort_enum_success(mock_call, client):
    response = client.get_seasonal_anime(
        Season.SUMMER, 2022, sort=SeasonalAnimeSorting.USER_NUM, limit=1
    )
    assert response[0].id == 1