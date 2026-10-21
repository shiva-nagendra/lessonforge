from agents.evaluator import evaluate_lesson
from agents.failure_analyzer import analyze_failures
from agents.generator import generate_lesson
from agents.regenerator import regenerate_lesson
from graph.state import LessonGraphState
from models import (
    EvaluationStatus,
    GenerationAttempt,
    RejectionLogEntry,
)
from retrieval.retriever import KnowledgeRetriever


MAX_RETRIES = 2


def retrieve_node(state: LessonGraphState) -> LessonGraphState:
    request = state["request"]

    retriever = KnowledgeRetriever()

    query_parts = [
        request.topic,
        request.learning_goal or "",
        request.learner_level,
    ]

    query = " ".join(
        part.strip()
        for part in query_parts
        if part.strip()
    )

    retrieved_context = retriever.search(
        query=query,
        top_k=3,
    )

    return {
        "retrieved_context": retrieved_context,
    }


def generate_node(state: LessonGraphState) -> LessonGraphState:
    lesson = generate_lesson(
        request=state["request"],
        memory_patterns=state.get("memory_patterns", []),
        retrieved_context=state.get("retrieved_context", []),
    )

    attempt = GenerationAttempt(
        attempt_number=1,
        lesson=lesson,
    )

    return {
        "current_lesson": lesson,
        "attempts": [attempt],
        "rejection_log": [],
        "retry_count": 0,
        "max_retries": MAX_RETRIES,
    }


def evaluate_node(state: LessonGraphState) -> LessonGraphState:
    lesson = state["current_lesson"]

    evaluation = evaluate_lesson(
        lesson=lesson,
        retrieved_context=state.get("retrieved_context", []),
    )

    attempts = state["attempts"]
    current_attempt_number = attempts[-1].attempt_number

    updated_attempts = [
        GenerationAttempt(
            attempt_number=attempt.attempt_number,
            lesson=attempt.lesson,
            evaluation=(
                evaluation
                if attempt.attempt_number == current_attempt_number
                else attempt.evaluation
            ),
        )
        for attempt in attempts
    ]

    return {
        "current_evaluation": evaluation,
        "attempts": updated_attempts,
        "final_status": evaluation.overall,
    }


def analyze_failure_node(state: LessonGraphState) -> LessonGraphState:
    lesson = state["current_lesson"]
    evaluation = state["current_evaluation"]

    failure_analysis = analyze_failures(
        lesson,
        evaluation,
    )

    failed_checks = [
        check
        for check in evaluation.checks
        if check.status.value == "FAIL"
    ]

    rejection_entry = RejectionLogEntry(
        attempt_number=state["attempts"][-1].attempt_number,
        status=EvaluationStatus.FAIL,
        failed_criteria=[
            check.criterion
            for check in failed_checks
        ],
        reasons=[
            check.reason
            for check in failed_checks
        ],
        changes_made_on_retry=[
            fix.instruction
            for fix in failure_analysis.fixes
        ],
    )

    rejection_log = [
        *state.get("rejection_log", []),
        rejection_entry,
    ]

    return {
        "failure_analysis": failure_analysis,
        "rejection_log": rejection_log,
    }


def regenerate_node(state: LessonGraphState) -> LessonGraphState:
    lesson = state["current_lesson"]
    request = state["request"]
    failure_analysis = state["failure_analysis"]

    improved_lesson = regenerate_lesson(
        request=request,
        lesson=lesson,
        failure_analysis=failure_analysis,
    )

    retry_count = state["retry_count"] + 1
    attempt_number = retry_count + 1

    attempt = GenerationAttempt(
        attempt_number=attempt_number,
        lesson=improved_lesson,
    )

    return {
        "current_lesson": improved_lesson,
        "attempts": [
            *state["attempts"],
            attempt,
        ],
        "retry_count": retry_count,
    }


def route_after_evaluation(state: LessonGraphState) -> str:
    evaluation = state["current_evaluation"]

    if evaluation.overall == EvaluationStatus.PASS:
        return "success"

    if state["retry_count"] >= state["max_retries"]:
        return "max_retries"

    return "retry"