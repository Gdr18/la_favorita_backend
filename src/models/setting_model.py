from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

from src.services.db_services import db


# Campos únicos: name. Está configurado en MongoDB Atlas.
class SettingModel(BaseModel, extra="forbid"):
    name: str = Field(..., min_length=1, max_length=50)
    values: List[str] = Field(..., min_length=1)

    @field_validator("values", mode="before")
    @classmethod
    def __validate_values(cls, v):
        if isinstance(v, list) and all(isinstance(item, str) and len(item) > 1 for item in v):
            return v
        else:
            raise ValueError("El campo 'values' debe ser una lista de strings con al menos un caracter en cada string.")

    # Solicitudes a la colección settings

    def insert_setting(self):
        new_setting = db.settings.insert_one(self.model_dump())
        return new_setting

    @staticmethod
    def get_settings():
        settings = db.settings.find()
        return list(settings)

    @staticmethod
    def get_setting(setting_id):
        setting = db.settings.find_one({"_id": ObjectId(setting_id)})
        return setting

    def update_setting(self, setting_id):
        updated_setting = db.settings.find_one_and_update(
            {"_id": ObjectId(setting_id)}, {"$set": self.model_dump()}, return_document=True
        )
        return updated_setting

    @staticmethod
    def delete_setting(setting_id):
        deleted_setting = db.settings.delete_one({"_id": ObjectId(setting_id)})
        return deleted_setting
