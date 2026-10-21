import sys

sys.path.insert(0, "src")

from models import LessonRequest
from agents.generator import generate_lesson


request = LessonRequest(
    topic="Introduction to RAG",
    learner_level="beginner",
    learning_goal="Understand what RAG is and why it is useful.",
)

lesson = generate_lesson(request)

print(lesson.model_dump_json(indent=2))
