from unittest.mock import patch

from graph.nodes import (
    analyze_failure_node,
    evaluate_node,
    regenerate_node,
)
from models import (
    CriterionStatus,
    EvaluationCriterion,
    EvaluationResult,
    EvaluationStatus,
    FailureAnalysis,
    FailureFix,
    GenerationAttempt,
    Lesson,
    LessonRequest,
    LessonSection,
)


def make_lesson(title: str) -> Lesson:
    return Lesson(
        title=title,
        learning_objectives=[
            "Understand the basic concept."
        ],
        sections=[
            LessonSection(
                heading="Introduction",
                content="This explains the topic simply.",
                example="For example, imagine a simple system.",
            )
        ],
        key_takeaways=[
            "The topic has a clear purpose."
        ],
        glossary={},
    )


def make_evaluation(status: EvaluationStatus) -> EvaluationResult:
    criterion_status = (
        CriterionStatus.PASS
        if status == EvaluationStatus.PASS
        else CriterionStatus.FAIL
    )

    checks = [
        EvaluationCriterion(
            criterion=criterion,
            status=criterion_status,
            reason=(
                "Criterion satisfied."
                if criterion_status == CriterionStatus.PASS
                else "Criterion failed."
            ),
            evidence="Test evidence.",
        )
        for criterion in [
            "accuracy",
            "beginner_friendliness",
            "examples",
            "coverage",
            "clarity",
        ]
    ]

    return EvaluationResult(
        overall=status,
        checks=checks,
        failure_reasons=(
            []
            if status == EvaluationStatus.PASS
            else ["The lesson failed the evaluation."]
        ),
    )


def test_retry_flow_creates_rejection_log():
    request = LessonRequest(
        topic="RAG",
        learner_level="beginner",
    )

    first_lesson = make_lesson("Initial RAG Lesson")
    improved_lesson = make_lesson("Improved RAG Lesson")

    failed_evaluation = make_evaluation(EvaluationStatus.FAIL)
    passed_evaluation = make_evaluation(EvaluationStatus.PASS)

    state = {
        "request": request,
        "current_lesson": first_lesson,
        "current_evaluation": failed_evaluation,
        "attempts": [
            GenerationAttempt(
                attempt_number=1,
                lesson=first_lesson,
                evaluation=failed_evaluation,
            )
        ],
        "rejection_log": [],
        "retry_count": 0,
        "max_retries": 2,
    }

    failure_analysis = FailureAnalysis(
        fixes=[
            FailureFix(
                criterion="examples",
                problem="The lesson lacks a concrete example.",
                instruction="Add one simple real-world example.",
            )
        ]
    )

    # Simulate failure analysis.
    with patch(
        "graph.nodes.analyze_failures",
        return_value=failure_analysis,
    ):
        analyzed_state = {
            **state,
            **analyze_failure_node(state),
        }

    # Verify rejection log was created.
    assert len(analyzed_state["rejection_log"]) == 1

    rejection = analyzed_state["rejection_log"][0]

    assert rejection.attempt_number == 1
    assert rejection.status == EvaluationStatus.FAIL
    assert "accuracy" in rejection.failed_criteria
    assert "examples" in rejection.failed_criteria
    assert (
        "Add one simple real-world example."
        in rejection.changes_made_on_retry
    )

    # Simulate targeted regeneration.
    with patch(
        "graph.nodes.regenerate_lesson",
        return_value=improved_lesson,
    ):
        regenerated_state = {
            **analyzed_state,
            **regenerate_node(analyzed_state),
        }

    # Verify second attempt was created.
    assert regenerated_state["retry_count"] == 1
    assert len(regenerated_state["attempts"]) == 2
    assert regenerated_state["attempts"][-1].attempt_number == 2
    assert regenerated_state["current_lesson"] == improved_lesson

    # Simulate second evaluation passing.
    with patch(
        "graph.nodes.evaluate_lesson",
        return_value=passed_evaluation,
    ):
        evaluated_state = {
            **regenerated_state,
            **evaluate_node(regenerated_state),
        }

    # Verify successful recovery.
    assert evaluated_state["final_status"] == EvaluationStatus.PASS
    assert len(evaluated_state["attempts"]) == 2
    assert (
        evaluated_state["attempts"][-1].evaluation.overall
        == EvaluationStatus.PASS
    )

    # Rejection history must survive the successful retry.
    assert len(evaluated_state["rejection_log"]) == 1