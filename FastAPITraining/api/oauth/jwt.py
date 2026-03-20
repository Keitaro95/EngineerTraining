import jwt
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash


SECRET_KEY =""
ALGORITHM = "HS256"

password_hash = PasswirdHash.recommended()

def create_access_token(data: dict, wxpires_delta: timedelta | None = None):
    to_encode = data.copy()