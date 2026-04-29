from fastapi.testclient import TestClient

import mealie.routes.recommendations as recommendation_routes
from tests.utils.fixture_schemas import TestUser


def test_dismiss_discovery_recipe_records_feedback(api_client: TestClient, unique_user: TestUser, monkeypatch):
    captured: dict[str, object] = {}

    def fake_apply_dismiss_feedback(user_id, recipe_id, recipe_tags):
        captured["user_id"] = str(user_id)
        captured["recipe_id"] = recipe_id
        captured["recipe_tags"] = recipe_tags

    monkeypatch.setattr(recommendation_routes, "apply_dismiss_feedback", fake_apply_dismiss_feedback)

    response = api_client.post(
        "/api/recommendations/dismiss",
        json={"recipeId": "foodcom-123", "tags": ["indian", "curry"]},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert captured == {
        "user_id": str(unique_user.user_id),
        "recipe_id": "foodcom-123",
        "recipe_tags": ["indian", "curry"],
    }


def test_rate_discovery_recipe_records_feedback(api_client: TestClient, unique_user: TestUser, monkeypatch):
    captured: dict[str, object] = {}

    def fake_apply_rating_feedback(user_id, recipe_id, recipe_tags, star_rating):
        captured["user_id"] = str(user_id)
        captured["recipe_id"] = recipe_id
        captured["recipe_tags"] = recipe_tags
        captured["star_rating"] = star_rating

    monkeypatch.setattr(recommendation_routes, "apply_rating_feedback", fake_apply_rating_feedback)

    response = api_client.post(
        "/api/recommendations/rate",
        json={"recipeId": "foodcom-456", "tags": ["italian", "pasta"], "rating": 5},
        headers=unique_user.token,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert captured == {
        "user_id": str(unique_user.user_id),
        "recipe_id": "foodcom-456",
        "recipe_tags": ["italian", "pasta"],
        "star_rating": 5,
    }
