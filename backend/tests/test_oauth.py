import asyncio
from types import SimpleNamespace

import pytest
from bson import ObjectId
from fastapi import HTTPException

import app.services.oauth as oauth


def test_unknown_oauth_provider_is_rejected() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(oauth.authorization_url("unknown"))
    assert error.value.status_code == 404


def test_oauth_callback_issues_single_use_grant(monkeypatch) -> None:
    records = {"states": [], "grants": []}

    async def fake_run(collection, operation, *args, **kwargs):
        target = records["states"] if collection is oauth.db_oauth_state else records["grants"]
        if operation == "insert_one":
            document = {"_id": ObjectId(), **args[0]}; target.append(document); return SimpleNamespace(inserted_id=document["_id"])
        if operation == "find_one":
            query = args[0]
            return next((item for item in target if all(item.get(key) == value for key, value in query.items())), None)
        if operation == "update_one":
            query, update = args
            item = next(item for item in target if all(item.get(key) == value for key, value in query.items()))
            item.update(update["$set"]); return SimpleNamespace(matched_count=1)
        raise AssertionError(operation)

    monkeypatch.setattr(oauth, "run_collection", fake_run)
    monkeypatch.setattr(oauth, "_exchange_identity", lambda provider, code, verifier: async_value({"subject": "123", "email": "user@example.com"}))
    monkeypatch.setattr(oauth, "_get_or_create_user", lambda provider, identity: async_value({"_id": ObjectId(), "username": identity["email"]}))
    state = "secure-state"
    from datetime import datetime, timedelta, timezone
    records["states"].append({"_id": ObjectId(), "state_hash": oauth._hash(state), "provider": "google", "used": False, "expires_at": datetime.now(timezone.utc) + timedelta(minutes=1)})
    grant = asyncio.run(oauth.handle_callback("google", "provider-code", state))
    assert len(grant) >= 20
    assert records["states"][0]["used"] is True
    assert records["grants"][0]["used"] is False


async def async_value(value):
    return value
