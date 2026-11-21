from malclient.Datamodels import Statistics


def test_statistics_flatten_status():
    payload = {
        "num_list_users": 100,
        "status": {
            "watching": 10,
            "completed": 20,
            "on_hold": 5,
            "dropped": 2,
            "plan_to_watch": 63,
        },
    }
    stats = Statistics.model_validate(payload)
    assert stats.num_list_users == 100
    assert stats.watching == 10
    assert stats.completed == 20