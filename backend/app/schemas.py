from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from .models import Category, Reporter, Status


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    @field_validator('*', mode='before')
    @classmethod
    def clean_text(cls, value):
        if isinstance(value, str):
            return ''.join(c for c in value if c in '\n\t' or ord(c) >= 32).strip()
        return value


class ReportCreate(Input):
    reporter_type: Reporter = Reporter.anonimo
    category: Category
    location_optional: str | None = Field(None, max_length=160)
    identification_optional: str | None = Field(None, max_length=120)
    description: str = Field(min_length=20, max_length=5000)
    fictitious_confirmation: Literal[True]


class Lookup(Input):
    protocol: str = Field(min_length=4, max_length=40)
    secret: str = Field(min_length=10, max_length=128)


class Login(Input):
    email: str = Field(min_length=5, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class StatusUpdate(Input):
    status: Status
    note_private_optional: str | None = Field(None, max_length=2000)


class Answer(Input):
    option_index: int = Field(ge=0, le=10)
