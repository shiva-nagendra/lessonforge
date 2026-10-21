import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from models import (
    EvaluationResult,
    FailureAnalysis,
    Lesson,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


FAILURE_ANALYZER_SYSTEM_PROMPT = """
You are a lesson quality improvement planner.

Your job is to analyze a lesson that failed evaluation and produce targeted
instructions for improving it.

Do NOT rewrite the lesson.

For every failed evaluation criterion:
- Identify the specific problem.
- Explain what needs to change.
- Provide one concrete instruction that another generator can follow.

Only create fixes for criteria that actually FAILED.

Do not invent failures that are not present in the evaluation.
Do not change or reinterpret the evaluator's criteria.
"""


def create_failure_analyzer():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY was not found. "
            "Make sure the project-level .env file exists "
            "and contains GOOGLE_API_KEY."
        )

    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0,
        google_api_key=api_key,
    )

    return model.with_structured_output(FailureAnalysis)


def analyze_failures(
    lesson: Lesson,
    evaluation: EvaluationResult,
) -> FailureAnalysis:

    failed_checks = [
        check
        for check in evaluation.checks
        if check.status.value == "FAIL"
    ]

    if not failed_checks:
        return FailureAnalysis()

    analyzer = create_failure_analyzer()

    failure_details = "\n".join(
        f"- Criterion: {check.criterion}\n"
        f"  Reason: {check.reason}\n"
        f"  Evidence: {check.evidence or 'No evidence provided'}"
        for check in failed_checks
    )

    prompt = f"""
Analyze the following failed lesson evaluation.

LESSON:
{lesson.model_dump_json(indent=2)}

FAILED CRITERIA:
{failure_details}
"""

    return analyzer.invoke(
        [
            ("system", FAILURE_ANALYZER_SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )