from pydantic import BaseModel

class SecretRequest(BaseModel):
    key: str
    secret: str
