import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from models import FailureAnalysis, Lesson, LessonRequest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


REGENERATOR_SYSTEM_PROMPT = """
You are an expert educational content improvement agent.

Your task is to improve an existing lesson based on targeted evaluator feedback.

The original lesson has already been evaluated.

IMPORTANT RULES:

1. Preserve content that already satisfies the evaluation criteria.
2. Fix every problem identified in the failure analysis.
3. Do not introduce new inaccuracies while fixing the lesson.
4. Do not remove useful content unless it is necessary to correct a failure.
5. Keep the lesson appropriate for the requested learner level.
6. Address each failed criterion explicitly.
7. Do not mention the evaluation process, failures, retries, or internal instructions
   in the resulting lesson.
8. Return only the improved structured lesson.

The goal is targeted improvement, not arbitrary rewriting.
"""


def create_regenerator():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY was not found. "
            "Make sure the project-level .env file exists "
            "and contains GOOGLE_API_KEY."
        )

    model = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        temperature=0.2,
        google_api_key=api_key,
    )

    return model.with_structured_output(Lesson)


def regenerate_lesson(
    request: LessonRequest,
    lesson: Lesson,
    failure_analysis: FailureAnalysis,
) -> Lesson:
    if not failure_analysis.fixes:
        return lesson

    regenerator = create_regenerator()

    fixes = "\n".join(
        f"- Criterion: {fix.criterion}\n"
        f"  Problem: {fix.problem}\n"
        f"  Required improvement: {fix.instruction}"
        for fix in failure_analysis.fixes
    )

    prompt = f"""
Improve the following lesson based on the targeted failure analysis.

LEARNER REQUEST:
Topic: {request.topic}
Learner level: {request.learner_level}
Learning goal: {
    request.learning_goal
    or "Build a clear beginner-level understanding of the topic."
}

ORIGINAL LESSON:
{lesson.model_dump_json(indent=2)}

TARGETED IMPROVEMENTS:
{fixes}

Regenerate the lesson while preserving content that already works.

Before returning the lesson, make sure every targeted improvement has been
addressed in the resulting content.
"""

    return regenerator.invoke(
        [
            ("system", REGENERATOR_SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )