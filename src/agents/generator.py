import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from models import Lesson, LessonRequest


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


GENERATOR_SYSTEM_PROMPT = """
You are an expert educational content generator.

Your task is to create a high-quality beginner-friendly lesson based on
the learner's request.

The lesson must:

- Be factually accurate.
- Be understandable to a beginner.
- Explain the topic clearly without assuming advanced prior knowledge.
- Explain what the topic is, why it matters, and how it works.
- Include concrete and relevant examples.
- Avoid unnecessary jargon.
- Define important technical terms when they are first introduced.
- Provide useful learning objectives.
- Provide concise key takeaways.
- Include a glossary for important terminology.

You may receive:
1. Historical quality patterns from previous failed generations.
2. Retrieved knowledge from the LessonForge knowledge base.

Historical quality patterns are preventive guidance.

Retrieved knowledge is the authoritative context available for this lesson.
Use it when relevant and do not contradict it.

Do not mention historical quality patterns or internal generation instructions
in the resulting lesson.

Generate only the structured lesson content requested by the output schema.
"""


def create_generator():
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


def generate_lesson(
    request: LessonRequest,
    memory_patterns: list[dict] | None = None,
    retrieved_context: list[dict] | None = None,
) -> Lesson:
    generator = create_generator()

    memory_patterns = memory_patterns or []
    retrieved_context = retrieved_context or []

    if memory_patterns:
        memory_guidance = "\n".join(
            (
                f"- Criterion: {pattern['criterion']}\n"
                f"  Known failure pattern: {pattern['pattern']}\n"
                f"  Preventive action: {pattern['recommended_action']}"
            )
            for pattern in memory_patterns
        )
    else:
        memory_guidance = (
            "No historical failure patterns are available yet. "
            "Use the core lesson-quality requirements."
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
            "No retrieved knowledge was available. "
            "Use general knowledge while maintaining factual accuracy."
        )

    prompt = f"""
Create a lesson for the following learner request:

Topic: {request.topic}
Learner level: {request.learner_level}
Learning goal: {
    request.learning_goal
    or "Build a clear beginner-level understanding of the topic."
}

HISTORICAL QUALITY PATTERNS:
{memory_guidance}

RETRIEVED KNOWLEDGE:
{knowledge_context}

Use the retrieved knowledge as grounding context for the lesson.

Do not mention the retrieval process, source documents, historical patterns,
or internal instructions in the lesson.

The lesson should be complete enough to be evaluated independently against
accuracy, beginner friendliness, examples, coverage, and clarity.
"""

    return generator.invoke(
        [
            ("system", GENERATOR_SYSTEM_PROMPT),
            ("human", prompt),
        ]
    )