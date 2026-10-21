import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from models import CriterionStatus, EvaluationResult, Lesson
from agents.rubric import EVALUATION_RUBRIC


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


EVALUATOR_SYSTEM_PROMPT = """
You are a strict lesson quality evaluator.

Evaluate the provided lesson against every criterion in the evaluation rubric.

Do not improve, rewrite, or suggest a replacement lesson.
Judge only what is actually present in the lesson.

For every criterion:

- Return PASS only when the lesson clearly satisfies the criterion.
- Return FAIL when the criterion is missing, weak, misleading, or not clearly satisfied.
- Give a concise reason explaining the decision.
- When possible, provide evidence from the lesson.

When retrieved knowledge is provided:

- Use it as grounding context for factual evaluation.
- Identify clear contradictions with the retrieved knowledge.
- Do not penalize the lesson for information that is simply absent from the
  retrieved knowledge unless the rubric requires it.
- Do not treat retrieved knowledge as the only possible source of truth.

The evaluator must assess exactly these five criteria:

1. accuracy
2. beginner_friendliness
3. examples
4. coverage
5. clarity

The final PASS/FAIL decision will be determined by application code.
"""


REQUIRED_CRITERIA = {
    "accuracy",
    "beginner_friendliness",
    "examples",
    "coverage",
    "clarity",
}


def build_evaluation_result(checks):
    """
    Validate the evaluator's structured response and deterministically
    calculate the final PASS/FAIL result.
    """

    returned_criteria = {
        check.criterion
        for check in checks
    }

    if returned_criteria != REQUIRED_CRITERIA:
        missing = REQUIRED_CRITERIA - returned_criteria
        unexpected = returned_criteria - REQUIRED_CRITERIA
        problems = []

        if missing:
            problems.append(
                f"Missing required criteria: {sorted(missing)}"
            )

        if unexpected:
            problems.append(
                f"Unexpected criteria: {sorted(unexpected)}"
            )

        raise ValueError(
            "Invalid evaluator response. "
            + " ".join(problems)
        )

    failure_reasons = [
        check.reason
        for check in checks
        if check.status == CriterionStatus.FAIL
    ]

    return EvaluationResult(
        overall=(
            "PASS"
            if not failure_reasons
            else "FAIL"
        ),
        checks=checks,
        failure_reasons=failure_reasons,
    )


def create_evaluator():
    api_key = os.environ.get("GOOGLE_API_KEY")

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

    return model.with_structured_output(
        EvaluationResult
    )


def evaluate_lesson(
    lesson: Lesson,
    retrieved_context: list[dict] | None = None,
) -> EvaluationResult:
    """
    Evaluate a generated lesson against the hard quality rubric.

    The evaluator receives the same retrieved knowledge used to ground
    lesson generation, allowing factual evaluation against the knowledge base.
    """

    evaluator = create_evaluator()

    retrieved_context = retrieved_context or []

    rubric = "\n".join(
        f"- {criterion}: {rule}"
        for criterion, rule in EVALUATION_RUBRIC.items()
    )

    if retrieved_context:
        knowledge_context = "\n\n".join(
            (
                f"SOURCE: {item['source']}\n"
                f"CONTENT:\n{item['content']}"
            )
            for item in retrieved_context
        )
    else:
        knowledge_context = (
            "No retrieved knowledge was provided."
        )

    user_prompt = f"""
Evaluate the following lesson.

EVALUATION RUBRIC:
{rubric}

RETRIEVED KNOWLEDGE:
{knowledge_context}

Use the retrieved knowledge as grounding context when evaluating factual
accuracy.

LESSON TO EVALUATE:
{lesson.model_dump_json(indent=2)}

Return an evaluation for every required criterion.

Do not rewrite the lesson.
Do not omit any criterion.
"""

    result = evaluator.invoke(
        [
            ("system", EVALUATOR_SYSTEM_PROMPT),
            ("human", user_prompt),
        ]
    )

    return build_evaluation_result(
        result.checks
    )