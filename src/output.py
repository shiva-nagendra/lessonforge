from graph.state import LessonGraphState
from models import LessonOutput


def build_lesson_output(
    state: LessonGraphState,
) -> LessonOutput:
    """
    Convert the internal LangGraph state into the final assignment output.
    """

    return LessonOutput(
        request=state["request"],
        final_status=state["final_status"],
        lesson=state["current_lesson"],
        rejection_log=state.get("rejection_log", []),
        attempts=len(state["attempts"]),
    )


def format_rejection_log(
    state: LessonGraphState,
) -> str:
    """
    Create a concise human-readable rejection log for the demo.
    """

    rejection_log = state.get("rejection_log", [])

    if not rejection_log:
        return "No rejection occurred. The first generation passed evaluation."

    lines = ["REJECTION LOG", "=" * 50]

    for entry in rejection_log:
        lines.append(
            f"\nAttempt {entry.attempt_number}: {entry.status.value}"
        )

        lines.append(
            "\nFailed criteria:"
        )

        for criterion in entry.failed_criteria:
            lines.append(f"- {criterion}")

        lines.append("\nWhy:")

        for reason in entry.reasons:
            lines.append(f"- {reason}")

        lines.append("\nChanges requested for retry:")

        for change in entry.changes_made_on_retry:
            lines.append(f"- {change}")

    return "\n".join(lines)