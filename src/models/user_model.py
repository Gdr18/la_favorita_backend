import re

from ..utils.db import type_checking


class UserModel:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        role: int = 3,
        phone: str = None,
        addresses: list = None,
        basket: list = None,
        orders: list = None,
    ):
        if type_checking(name, str):
            self.name = name

        if self._validate_email and type_checking(email, str):
            self.email = email

        # TODO: Implementar validación de contraseña según los criterios deseados
        if type_checking(password, str):
            self.password = password

        if type_checking(role, int) and role in [1, 2, 3]:
            self.role = role
        else:
            raise ValueError("'role' debe tener el valor 1, 2 o 3")

        if phone and type_checking(phone, str):
            self.phone = phone

        if addresses and type_checking(addresses, list):
            self.addresses = addresses

        if basket and type_checking(basket, list):
            self.basket = basket

        if orders and type_checking(orders, list):
            self.orders = orders

    def _validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if re.match(pattern, email):
            return True
        else:
            raise ValueError("El email no es válido")


# TODO: Eliminar lo siguiente cuando se implemente la validación de contraseña

# from typing import List, Optional
# import re

# class User:
#     def __init__(
#         self,
#         name: str,
#         email: str,
#         password: str,
#         role: int = 3,
#         phone: Optional[str] = None,
#         addresses: List[str] = [],
#         basket: List[dict] = [],
#         orders: List[dict] = [],
#     ):
#         self.name = name
#         self.email = email if self._validate_email(email) else None
#         self.password = password if self._validate_password(password) else None
#         self.role = role if role in [1, 2, 3] else 3
#         self.phone = phone
#         self.addresses = addresses
#         self.basket = basket
#         self.orders = orders

#     @property
#     def email(self) -> str:
#         return self._email

#     @email.setter
#     def email(self, value: str):
#         if self._validate_email(value):
#             self._email = value
#         else:
#             raise ValueError("Email no válido")

#     def _validate_email(self, email: str) -> bool:
#         pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
#         return re.match(pattern, email)

#     def _validate_password(self, password: str) -> bool:
#         # Implementar validación de contraseña según los criterios deseados
#         return True
