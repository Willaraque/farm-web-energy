from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.repositories.tokens import (
    authenticate_user,
    create_access_token,
    drop_tokenBD,
    get_user_active_current,
    save_token,
)
from app.schemas.models import (
    OAuthExchange,
    OtpVerify,
    PhoneRequest,
    ResetPassword,
    Token,
    User,
    UserInDB,
)
from app.services.auth_flows import (
    consume_otp,
    create_reset_grant,
    request_otp,
    reset_password,
)
from app.services.oauth import (
    authorization_url,
    consume_login_grant,
    enabled_providers,
    handle_callback,
)

app_tokens = APIRouter(tags=["authentication"])


async def issue_session(user) -> dict:
    token = create_access_token(
        {"sub": user.username}, timedelta(minutes=settings.access_token_expire_minutes)
    )
    return await save_token(
        user.id, user.username, {"access_token": token, "token_type": "bearer"}
    )


@app_tokens.post("/token", response_model=Token)
async def login_for_access_token(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict:
    user = await authenticate_user(form.username, form.password)
    if not user:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await issue_session(user)


@app_tokens.get("/auth/oauth/providers")
async def oauth_providers() -> dict[str, list[str]]:
    return {"providers": enabled_providers()}


@app_tokens.get("/auth/oauth/{provider}/start")
async def oauth_start(provider: str) -> RedirectResponse:
    return RedirectResponse(await authorization_url(provider), status_code=302)


@app_tokens.get("/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str, state: str) -> RedirectResponse:
    grant = await handle_callback(provider, code, state)
    return RedirectResponse(
        f"{settings.frontend_url.rstrip('/')}/auth/callback?code={grant}",
        status_code=302,
    )


@app_tokens.post("/auth/oauth/exchange", response_model=Token)
async def oauth_exchange(payload: OAuthExchange) -> dict:
    return await issue_session(UserInDB(**await consume_login_grant(payload.code)))


@app_tokens.post("/auth/password/forgot")
async def forgot_password(payload: PhoneRequest) -> dict:
    result = await request_otp(payload.phone, "password_reset")
    return {**result, "message": "Si existe una cuenta asociada, recibirás un código."}


@app_tokens.post("/auth/password/verify-otp")
async def verify_password_otp(payload: OtpVerify) -> dict[str, str]:
    await consume_otp(
        payload.challenge_id, payload.phone, payload.code, "password_reset"
    )
    return {"reset_token": await create_reset_grant(payload.phone)}


@app_tokens.post("/auth/password/reset")
async def complete_password_reset(payload: ResetPassword) -> dict[str, str]:
    await reset_password(payload.reset_token, payload.password)
    return {"message": "Contraseña actualizada correctamente"}


@app_tokens.get("/users/me", response_model=User)
async def read_users_me(
    user: Annotated[UserInDB, Depends(get_user_active_current)],
) -> User:
    return User.model_validate(user.model_dump(exclude={"password"}))


@app_tokens.post("/verify-token")
async def verify_token_endpoint(
    user: Annotated[UserInDB, Depends(get_user_active_current)],
) -> dict[str, bool]:
    return {"valid": True}


@app_tokens.delete("/delete-token")
async def delete_token(
    user: Annotated[UserInDB, Depends(get_user_active_current)],
) -> dict[str, bool]:
    result = await drop_tokenBD(str(user.id))
    if not result["valid"]:
        raise HTTPException(404, "Token no encontrado")
    return result
