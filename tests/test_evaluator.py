import pytest

from models import CriterionStatus, EvaluationCriterion, EvaluationStatus
from agents.evaluator import build_evaluation_result


REQUIRED_CRITERIA = [
    "accuracy",
    "beginner_friendliness",
    "examples",
    "coverage",
    "clarity",
]


def make_checks(status_overrides=None):
    status_overrides = status_overrides or {}

    return [
        EvaluationCriterion(
            criterion=criterion,
            status=status_overrides.get(criterion, CriterionStatus.PASS),
            reason=(
                f"The lesson satisfies the {criterion} criterion."
                if status_overrides.get(criterion, CriterionStatus.PASS)
                == CriterionStatus.PASS
                else f"The lesson fails the {criterion} criterion."
            ),
        )
        for criterion in REQUIRED_CRITERIA
    ]


def test_all_passing_criteria_produce_pass():
    checks = make_checks()

    result = build_evaluation_result(checks)

    assert result.overall == EvaluationStatus.PASS
    assert result.failure_reasons == []


def test_any_failed_criterion_produces_fail():
    checks = make_checks(
        {"examples": CriterionStatus.FAIL}
    )

    result = build_evaluation_result(checks)

    assert result.overall == EvaluationStatus.FAIL
    assert result.failure_reasons == [
        "The lesson fails the examples criterion."
    ]


def test_multiple_failures_are_all_captured():
    checks = make_checks(
        {
            "accuracy": CriterionStatus.FAIL,
            "examples": CriterionStatus.FAIL,
        }
    )

    result = build_evaluation_result(checks)

    assert result.overall == EvaluationStatus.FAIL
    assert result.failure_reasons == [
        "The lesson fails the accuracy criterion.",
        "The lesson fails the examples criterion.",
    ]


def test_missing_required_criterion_is_rejected():
    checks = make_checks()
    checks = [
        check
        for check in checks
        if check.criterion != "examples"
    ]

    with pytest.raises(ValueError, match="Missing required criteria"):
        build_evaluation_result(checks)


def test_unexpected_criterion_is_rejected():
    checks = make_checks()

    checks.append(
        EvaluationCriterion(
            criterion="creativity",
            status=CriterionStatus.PASS,
            reason="The lesson is creative.",
        )
    )

    with pytest.raises(ValueError, match="Unexpected criteria"):
        build_evaluation_result(checks)