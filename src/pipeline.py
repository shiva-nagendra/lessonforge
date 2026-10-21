from models import LessonRequest, Lesson, EvaluationResult
from agents.generator import generate_lesson
from agents.evaluator import evaluate_lesson


def generate_and_evaluate(
    request: LessonRequest,
) -> tuple[Lesson, EvaluationResult]:
    lesson = generate_lesson(request)
    evaluation = evaluate_lesson(lesson)

    return lesson, evaluation