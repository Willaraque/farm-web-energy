from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import logging
import secrets

import httpx
from bson import ObjectId
from fastapi import HTTPException

from app.core.config import settings
from app.core.database import run_collection
from app.core.mongo import db_otp, db_reset, db_token, db_user
from app.repositories.users import encrypt_password

logger = logging.getLogger(__name__)


def _digest(value: str) -> str:
    return hmac.new(
        settings.access_token_secret.encode(), value.encode(), hashlib.sha256
    ).hexdigest()


async def _send_sms(phone: str, message: str) -> None:
    if not all(
        (
            settings.twilio_account_sid,
            settings.twilio_auth_token,
            settings.twilio_from_number,
        )
    ):
        raise HTTPException(503, "El servicio SMS no está configurado")
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.twilio_account_sid}/Messages.json"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            url,
            data={"To": phone, "From": settings.twilio_from_number, "Body": message},
            auth=(settings.twilio_account_sid, settings.twilio_auth_token),
        )
    if response.status_code >= 400:
        logger.error(
            "El proveedor SMS rechazó el envío: status=%s", response.status_code
        )
        raise HTTPException(503, "No se pudo enviar el SMS")


async def request_otp(phone: str, purpose: str) -> dict:
    now = datetime.now(timezone.utc)
    previous = await run_collection(
        db_otp, "find_one", {"phone": phone, "purpose": purpose, "used": False}
    )
    if previous and previous.get("resend_after", now) > now:
        raise HTTPException(429, "Espera antes de solicitar otro código")
    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge_id = secrets.token_urlsafe(32)
    document = {
        "challenge_hash": _digest(challenge_id),
        "code_hash": _digest(f"{challenge_id}:{code}"),
        "phone": phone,
        "purpose": purpose,
        "attempts": 0,
        "used": False,
        "expires_at": now + timedelta(minutes=settings.otp_expire_minutes),
        "resend_after": now + timedelta(seconds=settings.otp_resend_seconds),
        "created_at": now,
    }
    await run_collection(
        db_otp,
        "update_many",
        {"phone": phone, "purpose": purpose, "used": False},
        {"$set": {"used": True}},
    )
    await run_collection(db_otp, "insert_one", document)
    await _send_sms(
        phone,
        f"Tu código de WAC Energy es {code}. Caduca en {settings.otp_expire_minutes} minutos.",
    )
    return {
        "challenge_id": challenge_id,
        "expires_in": settings.otp_expire_minutes * 60,
        "resend_in": settings.otp_resend_seconds,
    }


async def consume_otp(challenge_id: str, phone: str, code: str, purpose: str) -> None:
    challenge = await run_collection(
        db_otp,
        "find_one",
        {
            "challenge_hash": _digest(challenge_id),
            "phone": phone,
            "purpose": purpose,
            "used": False,
        },
    )
    now = datetime.now(timezone.utc)
    if not challenge or challenge.get("expires_at", now) <= now:
        raise HTTPException(400, "Código inválido o caducado")
    if challenge.get("attempts", 0) >= settings.otp_max_attempts:
        raise HTTPException(429, "Se agotaron los intentos del código")
    if not hmac.compare_digest(
        challenge["code_hash"], _digest(f"{challenge_id}:{code}")
    ):
        await run_collection(
            db_otp, "update_one", {"_id": challenge["_id"]}, {"$inc": {"attempts": 1}}
        )
        raise HTTPException(400, "Código inválido o caducado")
    await run_collection(
        db_otp,
        "update_one",
        {"_id": challenge["_id"]},
        {"$set": {"used": True, "used_at": now}},
    )


async def get_or_create_phone_user(phone: str) -> dict:
    user = await run_collection(db_user, "find_one", {"tel": phone})
    if user:
        return user
    document = {
        "username": f"phone:{phone}",
        "tel": phone,
        "phone_verified": True,
        "password": encrypt_password(secrets.token_urlsafe(32)),
        "active": True,
        "tipo": "Energia",
        "auth_providers": ["phone"],
        "created_at": datetime.now(timezone.utc),
    }
    result = await run_collection(db_user, "insert_one", document)
    return await run_collection(db_user, "find_one", {"_id": result.inserted_id})


async def create_reset_grant(phone: str) -> str:
    user = await run_collection(db_user, "find_one", {"tel": phone})
    if not user:
        raise HTTPException(400, "No se pudo validar la solicitud")
    token = secrets.token_urlsafe(48)
    await run_collection(
        db_reset,
        "insert_one",
        {
            "token_hash": _digest(token),
            "user_id": user["_id"],
            "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10),
        },
    )
    return token


async def reset_password(token: str, password: str) -> None:
    grant = await run_collection(
        db_reset, "find_one", {"token_hash": _digest(token), "used": False}
    )
    now = datetime.now(timezone.utc)
    if not grant or grant.get("expires_at", now) <= now:
        raise HTTPException(400, "El enlace de recuperación no es válido")
    await run_collection(
        db_user,
        "update_one",
        {"_id": grant["user_id"]},
        {"$set": {"password": encrypt_password(password), "updated_at": now}},
    )
    await run_collection(
        db_reset,
        "update_one",
        {"_id": grant["_id"]},
        {"$set": {"used": True, "used_at": now}},
    )
    await run_collection(db_token, "delete_one", {"_id": ObjectId(grant["user_id"])})
