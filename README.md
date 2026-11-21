# MAL-API-Client-Upgraded

![PyPI](https://img.shields.io/pypi/v/malclient-upgraded?logo=myanimelist&style=for-the-badge)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/malclient-upgraded?logo=python&logoColor=%23ffd43b&style=for-the-badge)
![PyPI - License](https://img.shields.io/pypi/l/malclient-upgraded?style=for-the-badge&color=3EB049) </br>
![Read the Docs](https://img.shields.io/readthedocs/mal-api-client-upgraded?style=for-the-badge&color=3EB049)
![PyPI - Downloads](https://img.shields.io/pypi/dm/malclient-upgraded?style=for-the-badge&color=3EB049) </br>
A third party object-oriented python3 client library for MyAnimeList's official REST API.
Originally created by [@JFryy](https://github.com/JFryy/MAL-API-Client), dropped around 2 years ago, picked up and rewritten by ModerNews to fit more modern standards and new REST API functions.

## Documentation
Unsure what to do? [Check out our documentation](https://mal-api-client-upgraded.readthedocs.io) </br>

## Installation
**Python 3.14+ required.**

From PyPI:

```bash
pip install malclient-upgraded
```

Development (recommended: [uv](https://docs.astral.sh/uv/) and a local `.venv` on Python 3.14):

```bash
uv sync --extra dev
uv run pytest
```

Or from GitHub:

```bash
pip install git+https://github.com/hugoprudente/MAL-API-Client-Upgraded
```

## API versions

- **REST** (default): `Client(api_version="v2")` → `https://api.myanimelist.net/v2/` ([official API](https://myanimelist.net/apiconfig/references/api/v2))
- **REST legacy**: `api_version="v1"` → `https://api.myanimelist.net/v1/` (deprecated by MAL; for explicit compatibility only)
- **OAuth** always uses `https://myanimelist.net/v1/oauth2/` regardless of `api_version`


## Authentication
Client library uses OAuth2 authorization, all you need to do is register your app [here](https://myanimelist.net/apiconfig).
Main auth requires access token:

```python
import malclient

malclient.Client(access_token=token)
```

Alternatively can authenticate using your client ID

```python
import malclient

malclient.Client(client_id=id)
```

You can generate token old-fashioned way using [this tutorial](https://myanimelist.net/blog.php?eid=835707)  
Or you can use function implemented in API

```python
import malclient

# Interactive OAuth (opens browser on supported platforms):
client = malclient.Client.generate_new_token("<CLIENT_ID>", "<CLIENT_SECRET>")
```

Although remember to call it only once and, then use the token generated this way, optionally with `Client.refresh_bearer_token` method  

As mentioned previously, if you're scared that your token will time out you can also utilize `Client.refresh_bearer_token` function

```python
client.refresh_bearer_token(
          client_id="<your-client-id>",
          client_secret="<your-client-secret>",
          refresh_token="<your-refresh-token>")
```

For any other issues regarding authentication, [please refer to the following guide](https://myanimelist.net/blog.php?eid=835707).

## Quick Start Examples
Responses are Pydantic v2 models (`model_dump()`, `model_validate()`).

```python
import malclient

client = malclient.Client(
    access_token="<your-access-token>",
    nsfw=True,
    api_version="v2",
)

# search anime, returns list
anime = client.search_anime("cowboy", limit=20)
for item in anime:
    # prints only titles
    print(item)
    # prints all attributes of object
    print(repr(item))
    
# search anime, returns list
manga = client.search_manga("Monogatari", limit=20)
for item in manga:
    # prints only titles
    print(manga)
    # prints all attributes of object
    print(repr(manga))

# Get individual anime by ID
anime = client.get_anime_details(1)
print(anime)
print(repr(anime))

# Update anime List based off of search results
anime = client.search_anime("Monogatari", limit=1)
```

### Most Imoprtant To-Do's
- [ ] Implement people endpoint
- [ ] Implement episodes endpoint
- [ ] Implement additional search endpoint

### Useful resources
- [MAL auth guide](https://myanimelist.net/blog.php?eid=835707)
- [Unofficial API Discord](https://discord.gg/XqzqDkzuFx)
- [Official MAL API Club](https://myanimelist.net/clubs.php?cid=13727)

## P.S. 
If anything bugs you, you can always reach me out at discord Gruzin#0911 as well
