from sqlmodel import SQLModel as Model
from sqlmodel import Field
from datetime import datetime

class Token(Model):
    access_token: str
    token_type: str
    user_id: int

class LoginSession(Model, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int
    access_token: str
    token_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    