"""
LessonForge — deliberate evaluation demo.

Demonstrates the self-evaluation loop required by the assignment:
generation → evaluation → failure analysis → targeted regeneration → re-evaluation.
"""

from agents.evaluator import evaluate_lesson
from agents.failure_analyzer import analyze_failures
from agents.generator import generate_lesson
from agents.regenerator import regenerate_lesson
from models import EvaluationStatus, LessonRequest
from retrieval.retriever import KnowledgeRetriever


def section(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(title)
    print("=" * 72)


def main() -> None:
    request = LessonRequest(
        topic="Introduction to RAG",
        learner_level="beginner",
        learning_goal=(
            "Understand what RAG is, why it is useful, "
            "and how the basic workflow works."
        ),
    )

    section("LESSONFORGE — EVALUATION DEMO")

    print(f"Topic: {request.topic}")
    print(f"Learner level: {request.learner_level}")
    print(f"Goal: {request.learning_goal}")

    # ---------------------------------------------------------
    # Retrieve grounding knowledge
    # ---------------------------------------------------------
    section("RETRIEVAL")

    retriever = KnowledgeRetriever()

    retrieved_context = retriever.search(
        query=(
            f"{request.topic} "
            f"{request.learning_goal} "
            f"{request.learner_level}"
        ),
        top_k=3,
    )

    print(f"Retrieved {len(retrieved_context)} relevant knowledge chunk(s).")

    # ---------------------------------------------------------
    # Generate lesson
    # ---------------------------------------------------------
    section("GENERATION")

    lesson = generate_lesson(
        request=request,
        memory_patterns=[],
        retrieved_context=retrieved_context,
    )

    print(f"Generated: {lesson.title}")

    # ---------------------------------------------------------
    # Introduce a controlled quality issue for the demo
    # ---------------------------------------------------------
    corrupted_lesson = lesson.model_copy(deep=True)

    deliberate_error = (
        "RAG does not retrieve information from documents or external "
        "knowledge. It generates answers entirely from the language "
        "model's existing knowledge."
    )

    corrupted_lesson.sections[0].content += (
        "\n\n" + deliberate_error
    )

    section("CONTROLLED QUALITY ISSUE")

    print("A factual statement has been introduced into the generated lesson:")
    print(f"\n{deliberate_error}")

    # ---------------------------------------------------------
    # Evaluate
    # ---------------------------------------------------------
    section("EVALUATION")

    failed_evaluation = evaluate_lesson(
        lesson=corrupted_lesson,
        retrieved_context=retrieved_context,
    )

    print(f"Overall: {failed_evaluation.overall.value}")

    for check in failed_evaluation.checks:
        if check.status.value == "FAIL":
            print(f"\n{check.criterion.upper()}: FAIL")
            print(f"Reason: {check.reason}")

            if check.evidence:
                print(f"Evidence: {check.evidence}")

    if failed_evaluation.overall != EvaluationStatus.FAIL:
        raise RuntimeError(
            "The controlled quality issue was not rejected by the evaluator."
        )

    # ---------------------------------------------------------
    # Analyze failure
    # ---------------------------------------------------------
    section("FAILURE ANALYSIS")

    failure_analysis = analyze_failures(
        corrupted_lesson,
        failed_evaluation,
    )

    for fix in failure_analysis.fixes:
        print(f"\nCriterion: {fix.criterion}")
        print(f"Problem: {fix.problem}")
        print(f"Instruction: {fix.instruction}")

    if not failure_analysis.fixes:
        raise RuntimeError(
            "The evaluator produced a failure, but no corrective "
            "instruction was generated."
        )

    # ---------------------------------------------------------
    # Targeted regeneration
    # ---------------------------------------------------------
    section("TARGETED REGENERATION")

    improved_lesson = regenerate_lesson(
        request=request,
        lesson=corrupted_lesson,
        failure_analysis=failure_analysis,
    )

    print(f"Updated lesson: {improved_lesson.title}")

    # ---------------------------------------------------------
    # Re-evaluate
    # ---------------------------------------------------------
    section("RE-EVALUATION")

    final_evaluation = evaluate_lesson(
        lesson=improved_lesson,
        retrieved_context=retrieved_context,
    )

    print(f"Overall: {final_evaluation.overall.value}")

    for check in final_evaluation.checks:
        status = check.status.value
        print(f"{check.criterion}: {status}")

    section("END OF DEMO")

    if final_evaluation.overall == EvaluationStatus.PASS:
        print("The revised lesson satisfies the evaluation rubric.")
    else:
        print("The revised lesson still has evaluation failures.")


if __name__ == "__main__":
    main()