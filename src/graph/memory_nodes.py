from graph.state import LessonGraphState
from memory.store import MemoryStore


def load_memory_node(state: LessonGraphState) -> LessonGraphState:
    memory = MemoryStore()

    patterns = memory.get_failure_patterns(limit=5)

    return {
        "memory_patterns": patterns,
    }


def save_failure_memory_node(
    state: LessonGraphState,
) -> LessonGraphState:
    failure_analysis = state["failure_analysis"]

    memory = MemoryStore()

    for fix in failure_analysis.fixes:
        memory.save_failure_pattern(
            criterion=fix.criterion,
            pattern=fix.problem,
            recommended_action=fix.instruction,
        )

    return {}


def save_lesson_run_node(
    state: LessonGraphState,
) -> LessonGraphState:
    request = state["request"]
    attempts = state["attempts"]
    final_status = state["final_status"]

    memory = MemoryStore()

    memory.save_lesson_run(
        topic=request.topic,
        learner_level=request.learner_level,
        learning_goal=request.learning_goal,
        final_status=final_status.value,
        attempts=len(attempts),
    )

    return {}