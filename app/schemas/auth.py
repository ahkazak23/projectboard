from pydantic import BaseModel, ConfigDict, model_validator


# Requests
class LoginIn(BaseModel):
    login: str
    password: str


class RegisterIn(BaseModel):
    login: str
    password: str
    repeat_password: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.repeat_password:
            raise ValueError("Passwords do not match")
        return self


# Response
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    login: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
