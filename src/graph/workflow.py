from langgraph.graph import END, START, StateGraph

from graph.memory_nodes import (
    load_memory_node,
    save_failure_memory_node,
    save_lesson_run_node,
)
from graph.nodes import (
    analyze_failure_node,
    evaluate_node,
    generate_node,
    regenerate_node,
    retrieve_node,
    route_after_evaluation,
)
from graph.state import LessonGraphState


def build_lesson_graph():
    graph = StateGraph(LessonGraphState)

    graph.add_node("load_memory", load_memory_node)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate", generate_node)
    graph.add_node("evaluate", evaluate_node)
    graph.add_node("analyze_failure", analyze_failure_node)
    graph.add_node(
        "save_failure_memory",
        save_failure_memory_node,
    )
    graph.add_node(
        "save_lesson_run",
        save_lesson_run_node,
    )
    graph.add_node("regenerate", regenerate_node)

    graph.add_edge(START, "load_memory")
    graph.add_edge("load_memory", "retrieve")
    graph.add_edge("retrieve", "generate")

    graph.add_edge("generate", "evaluate")

    graph.add_conditional_edges(
        "evaluate",
        route_after_evaluation,
        {
            "success": "save_lesson_run",
            "retry": "analyze_failure",
            "max_retries": "save_lesson_run",
        },
    )

    graph.add_edge(
        "analyze_failure",
        "save_failure_memory",
    )

    graph.add_edge(
        "save_failure_memory",
        "regenerate",
    )

    graph.add_edge(
        "regenerate",
        "evaluate",
    )

    graph.add_edge(
        "save_lesson_run",
        END,
    )

    return graph.compile()