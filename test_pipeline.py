import sys

sys.path.insert(0, "src")

from models import LessonRequest
from pipeline import generate_and_evaluate


request = LessonRequest(
    topic="Introduction to RAG",
    learner_level="beginner",
    learning_goal="Understand what RAG is and why it is useful.",
)

lesson, evaluation = generate_and_evaluate(request)

print("\n=== GENERATED LESSON ===")
print(lesson.model_dump_json(indent=2))

print("\n=== EVALUATION ===")
print(evaluation.model_dump_json(indent=2))