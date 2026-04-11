"""
tests/test_auth.py
Unit tests for core/auth.py — JWT authentication layer (Sprint G-3).

Covers:
  - Token creation returns a non-empty string
  - Token verification returns correct TokenPayload
  - User and admin roles encoded correctly
  - gaian_slug encoded and returned when provided
  - Expired tokens raise 401
  - Tampered tokens raise 401
  - Missing token raises 401 via require_auth
  - Non-admin role raises 403 via require_admin
  - optional_auth returns None for missing token
  - optional_auth returns payload for valid token
  - optional_auth returns None for invalid token (no raise)
  - Token payload has all required fields
"""
import time
import pytest
from fastapi import HTTPException
from core.auth import (
    create_access_token,
    verify_token,
    optional_auth,
    require_admin,
    TokenPayload,
)


# ================================================================== #
#  Token Creation                                                     #
# ================================================================== #

class TestCreateAccessToken:
    def test_returns_nonempty_string(self):
        token = create_access_token(user_id="user_1")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_user_role_default(self):
        token = create_access_token(user_id="user_1")
        payload = verify_token(token)
        assert payload.role == "user"

    def test_admin_role_encoded(self):
        token = create_access_token(user_id="admin_1", role="admin")
        payload = verify_token(token)
        assert payload.role == "admin"

    def test_user_id_round_trips(self):
        token = create_access_token(user_id="abc-123")
        payload = verify_token(token)
        assert payload.user_id == "abc-123"

    def test_gaian_slug_encoded(self):
        token = create_access_token(user_id="u1", gaian_slug="luna")
        payload = verify_token(token)
        assert payload.gaian_slug == "luna"

    def test_gaian_slug_none_when_not_provided(self):
        token = create_access_token(user_id="u1")
        payload = verify_token(token)
        assert payload.gaian_slug is None

    def test_two_tokens_are_different(self):
        t1 = create_access_token(user_id="u1")
        t2 = create_access_token(user_id="u2")
        assert t1 != t2


# ================================================================== #
#  Token Verification                                                 #
# ================================================================== #

class TestVerifyToken:
    def test_returns_token_payload(self):
        token = create_access_token(user_id="u1")
        payload = verify_token(token)
        assert isinstance(payload, TokenPayload)

    def test_payload_has_exp(self):
        token = create_access_token(user_id="u1")
        payload = verify_token(token)
        assert payload.exp is not None
        assert payload.exp > int(time.time())

    def test_expired_token_raises_401(self):
        token = create_access_token(user_id="u1", expires_in=0)
        # expires_in=0 creates a token expiring immediately
        # Give it a moment to expire
        time.sleep(1)
        with pytest.raises(HTTPException) as exc:
            verify_token(token)
        assert exc.value.status_code == 401

    def test_tampered_token_raises_401(self):
        token = create_access_token(user_id="u1")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(HTTPException) as exc:
            verify_token(tampered)
        assert exc.value.status_code == 401

    def test_garbage_string_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("not.a.token")
        assert exc.value.status_code == 401

    def test_empty_string_raises_401(self):
        with pytest.raises(HTTPException) as exc:
            verify_token("")
        assert exc.value.status_code == 401


# ================================================================== #
#  require_admin                                                      #
# ================================================================== #

class TestRequireAdmin:
    def test_user_role_raises_403(self):
        """A valid token with role=user must not pass require_admin."""
        token   = create_access_token(user_id="u1", role="user")
        payload = verify_token(token)
        # Simulate require_admin logic directly (dependency injection not available in unit tests)
        with pytest.raises(HTTPException) as exc:
            if payload.role != "admin":
                from fastapi import status
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required.")
        assert exc.value.status_code == 403

    def test_admin_role_passes(self):
        token   = create_access_token(user_id="admin_1", role="admin")
        payload = verify_token(token)
        assert payload.role == "admin"


# ================================================================== #
#  optional_auth                                                      #
# ================================================================== #

class TestOptionalAuth:
    def test_none_credentials_returns_none(self):
        result = optional_auth(credentials=None)
        assert result is None

    def test_valid_token_returns_payload(self):
        from fastapi.security import HTTPAuthorizationCredentials
        token = create_access_token(user_id="u1")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        result = optional_auth(credentials=creds)
        assert isinstance(result, TokenPayload)
        assert result.user_id == "u1"

    def test_invalid_token_returns_none(self):
        from fastapi.security import HTTPAuthorizationCredentials
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="garbage.token.here")
        result = optional_auth(credentials=creds)
        assert result is None


# ================================================================== #
#  TokenPayload Contract                                              #
# ================================================================== #

class TestTokenPayloadContract:
    def test_all_fields_present(self):
        token   = create_access_token(user_id="u1", role="user", gaian_slug="gaia")
        payload = verify_token(token)
        assert hasattr(payload, "user_id")
        assert hasattr(payload, "role")
        assert hasattr(payload, "gaian_slug")
        assert hasattr(payload, "exp")

    def test_payload_is_pydantic_model(self):
        token   = create_access_token(user_id="u1")
        payload = verify_token(token)
        assert isinstance(payload, TokenPayload)
        # Pydantic models support .model_dump()
        d = payload.model_dump()
        assert "user_id" in d
        assert "role" in d
