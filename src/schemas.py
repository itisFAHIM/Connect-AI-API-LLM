from enum import Enum
from pydantic import BaseModel, Field, StringConstraints
from typing_extensions import Annotated

class CategoryEnum(str, Enum):
    BILLING = "billing"
    BUG = "bug"
    FEATURE = "feature"
    OTHER = "other"

class UrgencyEnum(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class TriageInput(BaseModel):
    text: Annotated[str, StringConstraints(min_length=1, max_length=2000)]

class TriageOutput(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str