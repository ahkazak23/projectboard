from pydantic import BaseModel, ConfigDict, field_validator


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class LoginIn(BaseModel):
    login: str
    password: str

class RegisterIn(BaseModel):
    login: str
    password: str
    repeat_password: str

    @field_validator("repeat_password")
    def passwords_match(cls, v, info):
        password = info.data.get("password")
        if v != password:
            raise ValueError("Passwords do not match")
        return v