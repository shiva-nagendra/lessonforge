import sys

sys.path.insert(0, "src")


from models import (
    CriterionStatus,
    EvaluationCriterion,
    EvaluationResult,
    EvaluationStatus,
    Lesson,
    LessonSection,
)
from agents.failure_analyzer import analyze_failures


lesson = Lesson(
    title="Introduction to RAG",
    learning_objectives=[
        "Understand RAG."
    ],
    sections=[
        LessonSection(
            heading="RAG",
            content="RAG is a technical AI concept.",
            example=None,
        )
    ],
    key_takeaways=[
        "RAG is useful."
    ],
    glossary={},
)


evaluation = EvaluationResult(
    overall=EvaluationStatus.FAIL,
    checks=[
        EvaluationCriterion(
            criterion="accuracy",
            status=CriterionStatus.PASS,
            reason="The lesson is factually correct.",
        ),
        EvaluationCriterion(
            criterion="beginner_friendliness",
            status=CriterionStatus.FAIL,
            reason="The explanation assumes prior knowledge.",
            evidence="The lesson uses the term RAG without explaining it.",
        ),
        EvaluationCriterion(
            criterion="examples",
            status=CriterionStatus.FAIL,
            reason="The lesson does not contain a concrete example.",
            evidence="The example field is empty.",
        ),
        EvaluationCriterion(
            criterion="coverage",
            status=CriterionStatus.FAIL,
            reason="The lesson does not explain why RAG matters or how it works.",
            evidence="The content only provides a one-line definition.",
        ),
        EvaluationCriterion(
            criterion="clarity",
            status=CriterionStatus.FAIL,
            reason="The lesson contains unexplained technical terminology.",
            evidence="The term RAG is used without definition.",
        ),
    ],
    failure_reasons=[
        "The explanation assumes prior knowledge.",
        "The lesson does not contain a concrete example.",
        "The lesson does not explain why RAG matters or how it works.",
        "The lesson contains unexplained technical terminology.",
    ],
)


analysis = analyze_failures(lesson, evaluation)

print("\n=== FAILURE ANALYSIS ===")
print(analysis.model_dump_json(indent=2))
