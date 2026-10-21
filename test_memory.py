import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "src")

from memory.store import MemoryStore


print("=" * 70)
print("LESSONFORGE MEMORY TEST")
print("=" * 70)


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "test_memory.db"

    memory = MemoryStore(db_path)

    # ---------------------------------------------------------------
    # Test 1: Save a lesson run
    # ---------------------------------------------------------------

    memory.save_lesson_run(
        topic="Introduction to RAG",
        learner_level="beginner",
        learning_goal="Understand the basic RAG workflow.",
        final_status="PASS",
        attempts=2,
    )

    runs = memory.get_recent_runs()

    assert len(runs) == 1
    assert runs[0]["topic"] == "Introduction to RAG"
    assert runs[0]["final_status"] == "PASS"
    assert runs[0]["attempts"] == 2

    print("\nTest 1 — Save lesson run")
    print("PASS")


    # ---------------------------------------------------------------
    # Test 2: Save a failure pattern
    # ---------------------------------------------------------------

    memory.save_failure_pattern(
        criterion="examples",
        pattern="Lesson lacks concrete examples.",
        recommended_action="Add at least one concrete example for each major concept.",
    )

    patterns = memory.get_failure_patterns(
        criterion="examples"
    )

    assert len(patterns) == 1
    assert patterns[0]["criterion"] == "examples"
    assert patterns[0]["occurrences"] == 1

    print("\nTest 2 — Save failure pattern")
    print("PASS")


    # ---------------------------------------------------------------
    # Test 3: Repeated pattern increments occurrence count
    # ---------------------------------------------------------------

    memory.save_failure_pattern(
        criterion="examples",
        pattern="Lesson lacks concrete examples.",
        recommended_action="Add at least one concrete example for each major concept.",
    )

    patterns = memory.get_failure_patterns(
        criterion="examples"
    )

    assert patterns[0]["occurrences"] == 2

    print("\nTest 3 — Increment repeated pattern")
    print("PASS")


    # ---------------------------------------------------------------
    # Test 4: Persistent data survives a new MemoryStore instance
    # ---------------------------------------------------------------

    new_memory_instance = MemoryStore(db_path)

    persisted_runs = new_memory_instance.get_recent_runs()
    persisted_patterns = new_memory_instance.get_failure_patterns(
        criterion="examples"
    )

    assert len(persisted_runs) == 1
    assert len(persisted_patterns) == 1
    assert persisted_patterns[0]["occurrences"] == 2

    print("\nTest 4 — Persistence across instances")
    print("PASS")


print("\n" + "=" * 70)
print("ALL MEMORY TESTS PASSED")
print("=" * 70)