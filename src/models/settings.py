from sqlmodel import SQLModel as Model, Field


class SettingsBase(Model):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    groq_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str | None = None


class SettingsRead(SettingsBase):
    pass

class Settings(SettingsBase, table=True):  # type: ignore
    pass


