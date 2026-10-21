import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "src")

from graph.memory_nodes import save_failure_memory_node
from models import FailureAnalysis, FailureFix


print("=" * 70)
print("LESSONFORGE FAILURE MEMORY TEST")
print("=" * 70)


with tempfile.TemporaryDirectory() as temp_dir:
    db_path = Path(temp_dir) / "test_memory.db"

    # Temporarily replace the default database path used by MemoryStore.
    import graph.memory_nodes as memory_nodes

    original_memory_store = memory_nodes.MemoryStore

    class TestMemoryStore:
        def __init__(self):
            from memory.store import MemoryStore

            self.store = MemoryStore(db_path)

        def save_failure_pattern(
            self,
            criterion,
            pattern,
            recommended_action,
        ):
            self.store.save_failure_pattern(
                criterion=criterion,
                pattern=pattern,
                recommended_action=recommended_action,
            )

    memory_nodes.MemoryStore = TestMemoryStore

    try:
        failure_analysis = FailureAnalysis(
            fixes=[
                FailureFix(
                    criterion="examples",
                    problem="The lesson does not contain a concrete example.",
                    instruction=(
                        "Add at least one concrete example "
                        "showing the concept in practice."
                    ),
                ),
                FailureFix(
                    criterion="clarity",
                    problem="A technical term is used without explanation.",
                    instruction=(
                        "Define technical terms when they are "
                        "first introduced."
                    ),
                ),
            ]
        )

        state = {
            "failure_analysis": failure_analysis,
        }

        result = save_failure_memory_node(state)

        assert result == {}

        from memory.store import MemoryStore

        memory = MemoryStore(db_path)

        patterns = memory.get_failure_patterns()

        assert len(patterns) == 2

        criteria = {
            pattern["criterion"]
            for pattern in patterns
        }

        assert criteria == {
            "examples",
            "clarity",
        }

        print("\nTest — Save analyzed failures to memory")
        print("PASS")

        for pattern in patterns:
            print(
                f"\n[{pattern['criterion']}] "
                f"{pattern['pattern']}"
            )
            print(
                f"Recommendation: "
                f"{pattern['recommended_action']}"
            )

    finally:
        memory_nodes.MemoryStore = original_memory_store


print("\n" + "=" * 70)
print("FAILURE MEMORY TEST PASSED")
print("=" * 70)