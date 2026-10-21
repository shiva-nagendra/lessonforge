from typing import TypedDict

from models import (
    EvaluationResult,
    EvaluationStatus,
    FailureAnalysis,
    GenerationAttempt,
    Lesson,
    LessonRequest,
    RejectionLogEntry,
)


class LessonGraphState(TypedDict, total=False):
    request: LessonRequest

    current_lesson: Lesson
    current_evaluation: EvaluationResult

    failure_analysis: FailureAnalysis

    memory_patterns: list[dict]

    retrieved_context: list[dict]

    attempts: list[GenerationAttempt]

    rejection_log: list[RejectionLogEntry]

    retry_count: int
    max_retries: int

    final_status: EvaluationStatus