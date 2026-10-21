import sys

sys.path.insert(0, "src")

from graph.memory_nodes import load_memory_node


print("=" * 70)
print("LESSONFORGE MEMORY GRAPH TEST")
print("=" * 70)


state = {
    "request": None,
}

result = load_memory_node(state)

assert "memory_patterns" in result
assert isinstance(result["memory_patterns"], list)

print("\nMemory node executed successfully.")
print(f"Retrieved patterns: {len(result['memory_patterns'])}")

for pattern in result["memory_patterns"]:
    print(
        f"\n[{pattern['criterion']}] "
        f"{pattern['pattern']}"
    )
    print(
        f"Recommendation: "
        f"{pattern['recommended_action']}"
    )


print("\n" + "=" * 70)
print("MEMORY GRAPH TEST PASSED")
print("=" * 70)