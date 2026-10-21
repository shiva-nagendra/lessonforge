from models import Lesson, LessonSection
from agents.evaluator import evaluate_lesson


# Intentionally weak lesson.
# This is used to verify that the evaluator correctly detects failures.
lesson = Lesson(
    title="RAG",
    learning_objectives=[],
    sections=[
        LessonSection(
            heading="RAG",
            content="RAG is a technology used with AI.",
            example=None,
        )
    ],
    key_takeaways=[],
    glossary={},
)


result = evaluate_lesson(lesson)

print(result.model_dump_json(indent=2))