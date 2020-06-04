from datetime import datetime, timedelta
from typing import List, Optional

import graphene
import jwt

from saleor.account.models import User

JWT_EXPIRATION_DELTA = timedelta(seconds=100)
JWT_REFRESH_EXPIRATION_DELTA = timedelta(hours=100)
JWT_SECRET = "ABC"
JWT_ALGORITHM = "HS256"
JWT_AUTH_HEADER = "HTTP_AUTHORIZATION"
JWT_AUTH_HEADER_PREFIX = "JWT"
JWT_ACCESS_TYPE = "access"
JWT_REFRESH_TYPE = "refresh"
JWT_REFRESH_TOKEN_COOKIE_NAME = "refreshToken"


def jwt_base_payload(exp_delta):
    payload = {
        "exp": datetime.utcnow() + exp_delta,
        "iat": datetime.utcnow(),
    }
    return payload


def jwt_user_payload(
    user, token_type, exp_delta, permissions: Optional[List[str]] = None
):
    payload = jwt_base_payload(exp_delta)
    payload.update(
        {
            "email": user.email,
            "type": token_type,
            "user_id": graphene.Node.to_global_id("User", user.id),
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        }
    )
    if permissions:
        payload["permissions"] = permissions
    return payload


def jwt_encode(payload):
    return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM,).decode("utf-8")


def jwt_decode(token):
    return jwt.decode(token, JWT_SECRET, algorithms=JWT_ALGORITHM)


def create_token(payload, exp_delta):
    payload.update(jwt_base_payload(exp_delta))
    return jwt_encode(payload)


def create_access_token(user, permissions=None):
    payload = jwt_user_payload(user, JWT_ACCESS_TYPE, JWT_EXPIRATION_DELTA, permissions)
    return jwt_encode(payload)


def create_refresh_token(user):
    payload = jwt_user_payload(user, JWT_REFRESH_TYPE, JWT_REFRESH_EXPIRATION_DELTA)
    return jwt_encode(payload)


def get_token_from_request(request):
    auth = request.META.get(JWT_AUTH_HEADER, "").split()
    prefix = JWT_AUTH_HEADER_PREFIX

    if len(auth) != 2 or auth[0].lower() != prefix.lower():
        return None
    return auth[1]


def get_user_from_token(token):
    payload = jwt_decode(token)
    return User.objects.filter(email=payload["email"], is_active=True).first()