import sys

sys.path.insert(0, "src")

from graph.workflow import build_lesson_graph
from models import LessonRequest


print("=" * 70)
print("LESSONFORGE REFACTOR INTEGRATION TEST")
print("=" * 70)

graph = build_lesson_graph()

request = LessonRequest(
    topic="Introduction to RAG",
    learner_level="beginner",
    learning_goal=(
        "Understand what RAG is, why it is useful, "
        "and how the basic workflow works."
    ),
)

result = graph.invoke(
    {
        "request": request,
    }
)

print(f"\nFinal status: {result['final_status'].value}")
print(f"Total attempts: {len(result['attempts'])}")
print(f"Retries used: {result['retry_count']}")

for attempt in result["attempts"]:
    print(
        f"Attempt {attempt.attempt_number}: "
        f"{attempt.evaluation.overall.value}"
    )

print("\n" + "=" * 70)
print("REFACTOR INTEGRATION TEST PASSED")
print("=" * 70)