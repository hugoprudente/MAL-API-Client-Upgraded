from malclient.request_handler import APICaller


def _parser():
    return APICaller("https://example.test/", {})


def test_parse_json_merges_node():
    raw = {"node": {"id": 1, "title": "x"}, "role": "main"}
    parsed = _parser()._parse_json(raw)
    assert parsed["id"] == 1
    assert parsed["role"] == "main"


def test_parse_json_pagination():
    raw = {"data": [{"node": {"id": 2, "title": "y"}}], "paging": {"next": "n"}}
    parsed = _parser()._parse_json(raw)
    assert parsed["data"][0]["id"] == 2
    assert parsed["paging"]["next"] == "n"