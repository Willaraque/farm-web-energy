from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import base64
import secrets
from urllib.parse import urlencode

import httpx
import jwt
from fastapi import HTTPException

from app.core.config import settings
from app.core.database import run_collection
from app.core.mongo import db_login_grant, db_oauth_state, db_user
from app.repositories.users import encrypt_password

PROVIDERS = {
    "google": {
        "authorize": "https://accounts.google.com/o/oauth2/v2/auth",
        "token": "https://oauth2.googleapis.com/token",
        "scope": "openid email profile",
    },
    "facebook": {
        "authorize": "https://www.facebook.com/dialog/oauth",
        "token": "https://graph.facebook.com/oauth/access_token",
        "scope": "email,public_profile",
    },
    "instagram": {
        "authorize": "https://www.instagram.com/oauth/authorize",
        "token": "https://api.instagram.com/oauth/access_token",
        "scope": "instagram_business_basic",
    },
}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _credentials(provider: str) -> tuple[str, str]:
    if provider not in PROVIDERS:
        raise HTTPException(404, "Proveedor no soportado")
    return getattr(settings, f"{provider}_client_id"), getattr(
        settings, f"{provider}_client_secret"
    )


def enabled_providers() -> list[str]:
    return [name for name in PROVIDERS if all(_credentials(name))]


async def authorization_url(provider: str) -> str:
    client_id, client_secret = _credentials(provider)
    if not client_id or not client_secret:
        raise HTTPException(503, "Proveedor no configurado")
    state = secrets.token_urlsafe(40)
    verifier = secrets.token_urlsafe(64) if provider == "google" else None
    await run_collection(
        db_oauth_state,
        "insert_one",
        {
            "state_hash": _hash(state),
            "provider": provider,
            "pkce_verifier": verifier,
            "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
    )
    params = {
        "client_id": client_id,
        "redirect_uri": callback_url(provider),
        "response_type": "code",
        "scope": PROVIDERS[provider]["scope"],
        "state": state,
    }
    if provider == "google":
        params.update({"access_type": "online", "prompt": "select_account"})
    if verifier:
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest())
            .rstrip(b"=")
            .decode()
        )
        params.update({"code_challenge": challenge, "code_challenge_method": "S256"})
    return f"{PROVIDERS[provider]['authorize']}?{urlencode(params)}"


async def handle_callback(provider: str, code: str, state: str) -> str:
    record = await run_collection(
        db_oauth_state,
        "find_one",
        {"state_hash": _hash(state), "provider": provider, "used": False},
    )
    now = datetime.now(timezone.utc)
    if not record or record.get("expires_at", now) <= now:
        raise HTTPException(400, "Estado OAuth inválido o caducado")
    await run_collection(
        db_oauth_state, "update_one", {"_id": record["_id"]}, {"$set": {"used": True}}
    )
    identity = await _exchange_identity(provider, code, record.get("pkce_verifier"))
    user = await _get_or_create_user(provider, identity)
    grant = secrets.token_urlsafe(48)
    await run_collection(
        db_login_grant,
        "insert_one",
        {
            "grant_hash": _hash(grant),
            "user_id": user["_id"],
            "used": False,
            "expires_at": now + timedelta(minutes=2),
        },
    )
    return grant


async def consume_login_grant(grant: str) -> dict:
    record = await run_collection(
        db_login_grant, "find_one", {"grant_hash": _hash(grant), "used": False}
    )
    now = datetime.now(timezone.utc)
    if not record or record.get("expires_at", now) <= now:
        raise HTTPException(400, "Código de acceso inválido o caducado")
    await run_collection(
        db_login_grant, "update_one", {"_id": record["_id"]}, {"$set": {"used": True}}
    )
    user = await run_collection(db_user, "find_one", {"_id": record["user_id"]})
    if not user or not user.get("active", True):
        raise HTTPException(403, "Usuario inactivo")
    return user


async def _exchange_identity(
    provider: str, code: str, pkce_verifier: str | None = None
) -> dict:
    client_id, client_secret = _credentials(provider)
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": callback_url(provider),
        "code": code,
    }
    if provider == "google":
        data["grant_type"] = "authorization_code"
    if pkce_verifier:
        data["code_verifier"] = pkce_verifier
    async with httpx.AsyncClient(timeout=12) as client:
        response = await client.post(PROVIDERS[provider]["token"], data=data)
        if response.status_code >= 400:
            raise HTTPException(401, "El proveedor rechazó la autenticación")
        tokens = response.json()
        access_token = tokens.get("access_token")
        if not access_token:
            raise HTTPException(401, "Respuesta OAuth inválida")
        if provider == "google":
            id_token = tokens.get("id_token")
            if not id_token:
                raise HTTPException(401, "Google no devolvió un ID token")
            try:
                signing_key = jwt.PyJWKClient(
                    "https://www.googleapis.com/oauth2/v3/certs"
                ).get_signing_key_from_jwt(id_token)
                jwt.decode(
                    id_token,
                    signing_key.key,
                    algorithms=["RS256"],
                    audience=client_id,
                    issuer="https://accounts.google.com",
                )
            except jwt.PyJWTError as error:
                raise HTTPException(401, "ID token de Google inválido") from error
            profile = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        elif provider == "facebook":
            profile = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "fields": "id,name,email,first_name,last_name",
                    "access_token": access_token,
                },
            )
        else:
            profile = await client.get(
                "https://graph.instagram.com/me",
                params={"fields": "user_id,username", "access_token": access_token},
            )
    if profile.status_code >= 400:
        raise HTTPException(401, "No se pudo validar la identidad externa")
    result = profile.json()
    subject = str(result.get("sub") or result.get("id") or result.get("user_id") or "")
    if not subject:
        raise HTTPException(401, "Identidad externa incompleta")
    if provider == "google" and not result.get("email_verified"):
        raise HTTPException(401, "El correo de Google no está verificado")
    return {
        "subject": subject,
        "email": result.get("email"),
        "name": result.get("given_name")
        or result.get("first_name")
        or result.get("name"),
        "surname": result.get("family_name") or result.get("last_name"),
        "username": result.get("username"),
    }


async def _get_or_create_user(provider: str, identity: dict) -> dict:
    provider_key = f"{provider}:{identity['subject']}"
    user = await run_collection(db_user, "find_one", {"auth_identities": provider_key})
    if user:
        return user
    email = identity.get("email")
    if email:
        user = await run_collection(
            db_user, "find_one", {"username": email.strip().lower()}
        )
        if user and provider == "google":
            await run_collection(
                db_user,
                "update_one",
                {"_id": user["_id"]},
                {
                    "$addToSet": {
                        "auth_identities": provider_key,
                        "auth_providers": provider,
                    }
                },
            )
            return await run_collection(db_user, "find_one", {"_id": user["_id"]})
        if user:
            raise HTTPException(
                409, "Inicia sesión con tu contraseña para vincular este proveedor"
            )
    username = (
        email.strip().lower()
        if email
        else f"{provider}:{identity.get('username') or identity['subject']}"
    )
    document = {
        "username": username,
        "password": encrypt_password(secrets.token_urlsafe(32)),
        "name": identity.get("name"),
        "surname": identity.get("surname"),
        "active": True,
        "tipo": "Energia",
        "auth_identities": [provider_key],
        "auth_providers": [provider],
        "email_verified": bool(email),
        "created_at": datetime.now(timezone.utc),
    }
    result = await run_collection(db_user, "insert_one", document)
    return await run_collection(db_user, "find_one", {"_id": result.inserted_id})


def callback_url(provider: str) -> str:
    return f"{settings.backend_url.rstrip('/')}/auth/oauth/{provider}/callback"
