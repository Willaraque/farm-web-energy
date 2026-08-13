import pytest
from pydantic import ValidationError

from app.schemas.models import OtpVerify, PhoneRequest, ResetPassword


def test_phone_requires_e164_format() -> None:
    assert PhoneRequest(phone="+34600123456").phone == "+34600123456"
    with pytest.raises(ValidationError):
        PhoneRequest(phone="600 123 456")


def test_otp_requires_exactly_six_digits() -> None:
    valid = OtpVerify(phone="+34600123456", challenge_id="a" * 24, code="123456")
    assert valid.code == "123456"
    with pytest.raises(ValidationError):
        OtpVerify(phone="+34600123456", challenge_id="a" * 24, code="12345")
    with pytest.raises(ValidationError):
        OtpVerify(phone="+34600123456", challenge_id="a" * 24, code="12345x")


def test_reset_password_has_secure_minimum() -> None:
    with pytest.raises(ValidationError):
        ResetPassword(reset_token="a" * 24, password="short")
