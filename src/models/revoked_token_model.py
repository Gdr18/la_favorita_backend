from pydantic import BaseModel, Field, field_validator
import pendulum


# Campo único: "jti", configurado en MongoDB Atlas.
# Campo TTL: "exp", configurado en MongoDB Atlas. El documento se eliminará automáticamente cuando expire la fecha.
class RevokedTokenModel(BaseModel, extra="forbid", arbitrary_types_allowed=True):
    jti: str = Field(..., pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$")
    exp: pendulum.DateTime = Field(...)

    @field_validator('exp', mode='before')
    @classmethod
    def check_exp(cls, v):
        if isinstance(v, pendulum.DateTime) and v > pendulum.now("UTC"):
            return v
        raise ValueError("La fecha de expiración debe ser tipo datetime y mayor que la fecha actual.")

    def to_dict(self):
        return self.model_dump()
