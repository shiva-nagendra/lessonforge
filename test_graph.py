import sys

sys.path.insert(0, "src")

from graph.nodes import route_after_evaluation
from models import (
    CriterionStatus,
    EvaluationResult,
    EvaluationStatus,
)


REQUIRED_CRITERIA = [
    "accuracy",
    "beginner_friendliness",
    "examples",
    "coverage",
    "clarity",
]


def make_evaluation(status: EvaluationStatus) -> EvaluationResult:
    checks = [
        {
            "criterion": criterion,
            "status": (
                CriterionStatus.PASS
                if status == EvaluationStatus.PASS
                else CriterionStatus.FAIL
            ),
            "reason": (
                "Criterion satisfied."
                if status == EvaluationStatus.PASS
                else "Criterion deliberately failed for routing test."
            ),
            "evidence": None,
        }
        for criterion in REQUIRED_CRITERIA
    ]

    return EvaluationResult(
        overall=status,
        checks=checks,
        failure_reasons=(
            []
            if status == EvaluationStatus.PASS
            else ["Deliberate test failure."]
        ),
    )


print("=" * 70)
print("LESSONFORGE RETRY ROUTING TEST")
print("=" * 70)


# -------------------------------------------------------------------
# TEST 1: PASS should go directly to success
# -------------------------------------------------------------------

state = {
    "current_evaluation": make_evaluation(EvaluationStatus.PASS),
    "retry_count": 0,
    "max_retries": 2,
}

route = route_after_evaluation(state)

print("\nTest 1 — PASS with 0 retries")
print(f"Expected: success")
print(f"Actual:   {route}")

assert route == "success"


# -------------------------------------------------------------------
# TEST 2: FAIL with retries remaining should retry
# -------------------------------------------------------------------

state = {
    "current_evaluation": make_evaluation(EvaluationStatus.FAIL),
    "retry_count": 0,
    "max_retries": 2,
}

route = route_after_evaluation(state)

print("\nTest 2 — FAIL with retries remaining")
print(f"Expected: retry")
print(f"Actual:   {route}")

assert route == "retry"


# -------------------------------------------------------------------
# TEST 3: FAIL after first retry should retry again
# -------------------------------------------------------------------

state = {
    "current_evaluation": make_evaluation(EvaluationStatus.FAIL),
    "retry_count": 1,
    "max_retries": 2,
}

route = route_after_evaluation(state)

print("\nTest 3 — FAIL after 1 retry")
print(f"Expected: retry")
print(f"Actual:   {route}")

assert route == "retry"


# -------------------------------------------------------------------
# TEST 4: FAIL after maximum retries should stop
# -------------------------------------------------------------------

state = {
    "current_evaluation": make_evaluation(EvaluationStatus.FAIL),
    "retry_count": 2,
    "max_retries": 2,
}

route = route_after_evaluation(state)

print("\nTest 4 — FAIL after maximum retries")
print(f"Expected: max_retries")
print(f"Actual:   {route}")

assert route == "max_retries"


print("\n" + "=" * 70)
print("ALL RETRY ROUTING TESTS PASSED")
print("=" * 70)