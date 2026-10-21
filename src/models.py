from enum import Enum

from pydantic import BaseModel, Field


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class CriterionStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"


class LessonRequest(BaseModel):
    topic: str = Field(min_length=1)
    learner_level: str = "beginner"
    learning_goal: str | None = None


class LessonSection(BaseModel):
    heading: str
    content: str
    example: str | None = None


class Lesson(BaseModel):
    title: str
    learning_objectives: list[str]
    sections: list[LessonSection]
    key_takeaways: list[str]
    glossary: dict[str, str]


class EvaluationCriterion(BaseModel):
    criterion: str
    status: CriterionStatus
    reason: str
    evidence: str | None = None


class EvaluationResult(BaseModel):
    overall: EvaluationStatus
    checks: list[EvaluationCriterion]
    failure_reasons: list[str] = Field(default_factory=list)


class GenerationAttempt(BaseModel):
    attempt_number: int
    lesson: Lesson
    evaluation: EvaluationResult | None = None


class LessonRun(BaseModel):
    request: LessonRequest
    attempts: list[GenerationAttempt] = Field(default_factory=list)
    final_status: EvaluationStatus | None = None