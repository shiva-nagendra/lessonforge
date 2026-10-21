from models import (
    CriterionStatus,
    EvaluationStatus,
    Lesson,
    LessonRequest,
    LessonSection,
)


def test_lesson_request_defaults_to_beginner():
    request = LessonRequest(topic="What is RAG?")

    assert request.topic == "What is RAG?"
    assert request.learner_level == "beginner"


def test_lesson_can_be_created():
    lesson = Lesson(
        title="Introduction to RAG",
        learning_objectives=["Understand what RAG is"],
        sections=[
            LessonSection(
                heading="What is RAG?",
                content="RAG combines retrieval with generation.",
                example="A chatbot retrieving information from company documents.",
            )
        ],
        key_takeaways=["RAG provides external context to an LLM."],
        glossary={"RAG": "Retrieval-Augmented Generation"},
    )

    assert lesson.title == "Introduction to RAG"
    assert len(lesson.sections) == 1


def test_evaluation_status_values():
    assert EvaluationStatus.PASS.value == "PASS"
    assert EvaluationStatus.FAIL.value == "FAIL"
    assert CriterionStatus.PASS.value == "PASS"
    assert CriterionStatus.FAIL.value == "FAIL"