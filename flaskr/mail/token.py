from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from ..config import BaseConfig

def generate_confirmation_token(email):
    print('SECRET KEY: ',BaseConfig.SECRET_KEY[0])
    serializer = URLSafeTimedSerializer(BaseConfig.SECRET_KEY[0])
    return serializer.dumps(email, salt=BaseConfig.SECURITY_PASSWORD_SALT[0])

def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(BaseConfig.SECRET_KEY)
    salt = BaseConfig.SECURITY_PASSWORD_SALT
    try:
        email = serializer.loads(
            token,
            salt=salt,
            max_age=expiration
        )
    except:
        return False
    return email