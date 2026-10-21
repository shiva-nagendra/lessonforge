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

    @property
    def is_complete(self) -> bool:
        required_criteria = {
            "accuracy",
            "beginner_friendliness",
            "examples",
            "coverage",
            "clarity",
        }

        returned_criteria = {
            check.criterion
            for check in self.checks
        }

        return (
            len(self.checks) == len(required_criteria)
            and returned_criteria == required_criteria
        )


class FailureFix(BaseModel):
    criterion: str
    problem: str
    instruction: str


class FailureAnalysis(BaseModel):
    fixes: list[FailureFix] = Field(default_factory=list)


class GenerationAttempt(BaseModel):
    attempt_number: int
    lesson: Lesson
    evaluation: EvaluationResult | None = None


class RejectionLogEntry(BaseModel):
    """
    Human-readable record explaining why a generation attempt was rejected
    and what the regeneration step was instructed to change.
    """

    attempt_number: int
    status: EvaluationStatus
    failed_criteria: list[str]
    reasons: list[str]
    changes_made_on_retry: list[str]


class LessonRun(BaseModel):
    request: LessonRequest
    attempts: list[GenerationAttempt] = Field(default_factory=list)
    rejection_log: list[RejectionLogEntry] = Field(default_factory=list)
    final_status: EvaluationStatus | None = None


class LessonOutput(BaseModel):
    """
    Final submission-oriented output.

    Contains the passing lesson and the rejection history that explains
    how the system improved it.
    """

    request: LessonRequest
    final_status: EvaluationStatus
    lesson: Lesson
    rejection_log: list[RejectionLogEntry] = Field(default_factory=list)
    attempts: int