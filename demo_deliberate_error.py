"""
LessonForge — complete evaluation demo.

Demonstrates:
generation → deliberate failure → evaluation → failure analysis
→ targeted regeneration → re-evaluation → final passing lesson.

The output is intentionally formatted so the final lesson and
rejection log can be copied directly into the assessment document.
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


def print_lesson(lesson) -> None:
    """Print the complete lesson in a copy-friendly format."""

    section("FINAL PASSING LESSON")

    print(f"\n# {lesson.title}\n")

    print("## Learning Objectives")
    for objective in lesson.learning_objectives:
        print(f"- {objective}")

    print("\n## Lesson")

    for index, lesson_section in enumerate(lesson.sections, start=1):
        print(f"\n### {index}. {lesson_section.heading}")
        print(lesson_section.content)

        if lesson_section.example:
            print("\n**Example:**")
            print(lesson_section.example)

    print("\n## Key Takeaways")
    for takeaway in lesson.key_takeaways:
        print(f"- {takeaway}")

    print("\n## Glossary")
    for term, definition in lesson.glossary.items():
        print(f"- **{term}:** {definition}")


def print_evaluation(evaluation) -> None:
    """Print every evaluation criterion."""

    print(f"\nOverall: {evaluation.overall.value}")

    for check in evaluation.checks:
        print(f"\n{check.criterion.upper()}: {check.status.value}")
        print(f"Reason: {check.reason}")

        if check.evidence:
            print(f"Evidence: {check.evidence}")


def main() -> None:
    request = LessonRequest(
        topic="Introduction to RAG",
        learner_level="beginner",
        learning_goal=(
            "Understand what RAG is, why it is useful, "
            "and how the basic workflow works."
        ),
    )

    section("LESSONFORGE — COMPLETE EVALUATION DEMO")

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
    # Introduce a controlled quality issue
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

    print("A deliberate factual error has been introduced:")
    print(f"\n{deliberate_error}")

    # ---------------------------------------------------------
    # Evaluate corrupted lesson
    # ---------------------------------------------------------
    section("INITIAL EVALUATION — EXPECTED FAIL")

    failed_evaluation = evaluate_lesson(
        lesson=corrupted_lesson,
        retrieved_context=retrieved_context,
    )

    print_evaluation(failed_evaluation)

    if failed_evaluation.overall != EvaluationStatus.FAIL:
        raise RuntimeError(
            "The controlled quality issue was not rejected by the evaluator."
        )

    # ---------------------------------------------------------
    # Analyze failure
    # ---------------------------------------------------------
    section("REJECTION / FAILURE ANALYSIS")

    failure_analysis = analyze_failures(
        corrupted_lesson,
        failed_evaluation,
    )

    if not failure_analysis.fixes:
        raise RuntimeError(
            "The evaluator produced a failure, but no corrective "
            "instruction was generated."
        )

    for fix in failure_analysis.fixes:
        print(f"\nCriterion: {fix.criterion}")
        print(f"Problem: {fix.problem}")
        print(f"Correction instruction: {fix.instruction}")

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
    print("The failed lesson was regenerated using the evaluator's feedback.")

    # ---------------------------------------------------------
    # Re-evaluate improved lesson
    # ---------------------------------------------------------
    section("FINAL RE-EVALUATION")

    final_evaluation = evaluate_lesson(
        lesson=improved_lesson,
        retrieved_context=retrieved_context,
    )

    print_evaluation(final_evaluation)

    # ---------------------------------------------------------
    # Complete final lesson
    # ---------------------------------------------------------
    print_lesson(improved_lesson)

    # ---------------------------------------------------------
    # Submission-ready rejection log
    # ---------------------------------------------------------
    section("REJECTION LOG — SUBMISSION SUMMARY")

    print("\n### Initial Attempt")
    print("Status: FAIL")

    print("\n### What failed")
    for check in failed_evaluation.checks:
        if check.status.value == "FAIL":
            print(f"- {check.criterion}: {check.reason}")
            if check.evidence:
                print(f"  Evidence: {check.evidence}")

    print("\n### What changed on retry")
    for fix in failure_analysis.fixes:
        print(f"- {fix.criterion}: {fix.instruction}")

    print("\n### Final Attempt")
    print(f"Status: {final_evaluation.overall.value}")

    for check in final_evaluation.checks:
        print(f"- {check.criterion}: {check.status.value}")

    section("END OF DEMO")

    if final_evaluation.overall == EvaluationStatus.PASS:
        print("The revised lesson satisfies the complete evaluation rubric.")
    else:
        print("The revised lesson still has evaluation failures.")


if __name__ == "__main__":
    main()