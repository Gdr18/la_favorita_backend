import re
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError

from ..utils.db_utils import bcrypt


# TODO: Verificar que todo funciona correctamente
# Campos únicos: email. Está configurado en MongoDB Atlas.
class UserModel(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=8, max_length=50)
    role: int = Field(default=3, ge=1, le=3)
    phone: Optional[str] = None
    addresses: Optional[List] = None
    basket: Optional[Dict] = None

    class ConfigDict:
        extra = 'forbid'

    @field_validator('password')
    def __validate_password(cls, v):
        bcrypt_pattern = re.compile(r'^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$')
        if bcrypt_pattern.match(v):
            return v
        if (
            len(v) >= 8
            and re.search(r"[A-Z]", v)
            and re.search(r"[a-z]", v)
            and re.search(r"[0-9]", v)
            and re.search(r"[!@#$%^&*_-]", v)
        ):
            hashing_v = cls.hashing_password(v)
            return hashing_v
        else:
            raise ValueError('password')

    @staticmethod
    def hashing_password(password):
        return bcrypt.generate_password_hash(password).decode("utf-8")

    @field_validator('phone')
    def __validate_phone(cls, v):
        if v is None:
            return v
        phone_pattern = re.compile(r"^\+?34?\d{9}$")
        if phone_pattern.match(v):
            return v
        else:
            raise ValueError("phone")

    def to_dict(self):
        return self.dict()
