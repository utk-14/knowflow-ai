import json
import httpx
import jwt
from functools import lru_cache
from fastapi import HTTPException, Header
from typing import Optional
from app.config import settings


@lru_cache(maxsize=1)
def _get_jwks() -> list[dict]:
    """
    Fetch Supabase's public JWKS (JSON Web Key Set) and cache it.
    Called once per process lifetime.
    """
    url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Supabase JWKS: {str(e)}",
        )
    return response.json()["keys"]


def _find_signing_key(kid: Optional[str]):
    """
    Find the JWK matching the token's key ID (`kid`).
    If no `kid` is provided, use the first key available.
    """
    keys = _get_jwks()
    if not keys:
        raise HTTPException(status_code=500, detail="No signing keys found in JWKS")

    if kid:
        for k in keys:
            if k.get("kid") == kid:
                return k
        raise HTTPException(status_code=401, detail=f"No matching key for kid={kid}")

    return keys[0]


def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Verify the Supabase-issued JWT and return the authenticated user's UUID.

    Flow:
      1. Extract token from `Authorization: Bearer <token>`.
      2. Read the token header to know which algorithm and key were used.
      3. If ES256 (new Supabase) -> verify with public key from JWKS.
      4. If HS256 (legacy) and a legacy secret exists -> verify with shared secret.
      5. Return `sub` claim (the user's UUID).

    Raises 401 on any failure.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header",
        )

    token = authorization.replace("Bearer ", "").strip()

    try:
        header = jwt.get_unverified_header(token)
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Malformed token: {str(e)}")

    alg = header.get("alg", "ES256")
    kid = header.get("kid")

    try:
        if alg == "HS256" and settings.SUPABASE_JWT_SECRET:
            # Legacy path — only used if you still have HS256 tokens
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False},
            )
        elif alg == "ES256":
            # Modern Supabase path (asymmetric ECC)
            key_data = _find_signing_key(kid)
            public_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key_data))
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["ES256"],
                options={"verify_aud": False},
            )
        else:
            raise HTTPException(
                status_code=401,
                detail=f"Unsupported token algorithm: {alg}",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing 'sub' claim")

    return user_id