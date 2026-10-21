# LessonForge

## Self-Evaluating Lesson Content Generator

LessonForge is a GenAI content-generation system that creates beginner-friendly lessons, evaluates them against a hard quality rubric, identifies failures, and regenerates the lesson using targeted feedback.

The system is designed around a simple principle:

> Generate → Evaluate → Learn from failure → Regenerate → Evaluate again

The project was built as a practical GenAI engineering system using Python, LangGraph, Gemini, RAG, structured outputs, and persistent memory.

---

## Problem

Generating educational content with an LLM does not guarantee that the result is:

- accurate
- beginner-friendly
- complete
- clear
- supported by relevant knowledge
- useful for learning

A single generation step can produce missing examples, unexplained jargon, incomplete explanations, or inaccurate information.

LessonForge addresses this by separating **generation** from **evaluation**.

Instead of accepting the first generated lesson, the system evaluates it against explicit criteria and retries when necessary.

---

## System Architecture

```text
                    User Request
                         │
                         ▼
                  Load Memory
                         │
                         ▼
                  RAG Retrieval
                         │
                         ▼
                Lesson Generation
                         │
                         ▼
              Independent Evaluator
                         │
                  ┌──────┴──────┐
                  │             │
                PASS           FAIL
                  │             │
                  │       Failure Analysis
                  │             │
                  │       Save Failure Memory
                  │             │
                  │       Targeted Regeneration
                  │             │
                  │        Evaluate Again
                  │             │
                  └──────┬──────┘
                         ▼
                  Final Lesson
                         │
                         ▼
                  Rejection Log
```

The workflow is implemented using LangGraph.

---

## Core Workflow

### 1. Load persistent memory

LessonForge stores previous lesson runs and recurring failure patterns in SQLite.

Historical failure patterns can be provided to future generations as preventive guidance.

---

### 2. Retrieve relevant knowledge

The system retrieves relevant information from a local knowledge base before generating the lesson.

Current retrieval pipeline:

```text
Markdown knowledge
       ↓
Document chunking
       ↓
Sentence Transformer embeddings
       ↓
FAISS vector index
       ↓
Top-k relevant chunks
```

The retrieved information is passed to the generator as grounding context.

The same retrieved context is also provided to the evaluator so that factual evaluation can consider the available knowledge.

---

### 3. Generate a structured lesson

The generator uses Gemini with structured Pydantic output.

A lesson contains:

- title
- learning objectives
- sections
- examples
- key takeaways
- glossary

The generator is instructed to create beginner-friendly content and define technical terminology when it is first introduced.

---

### 4. Evaluate independently

The evaluator is intentionally separated from the generator.

Every lesson is evaluated against five hard criteria:

| Criterion | Requirement |
|---|---|
| Accuracy | Factually correct and not misleading |
| Beginner friendliness | Understandable without advanced prior knowledge |
| Examples | Contains relevant concrete examples |
| Coverage | Explains what, why, and how |
| Clarity | Avoids unexplained jargon and unnecessary complexity |

Each criterion receives:

```text
PASS / FAIL
Reason
Evidence
```

The final evaluation status is calculated deterministically by application code.

A lesson passes only when all required criteria pass.

---

## 5. Failure analysis

If evaluation fails, LessonForge does not immediately regenerate the entire lesson blindly.

A separate failure-analysis step converts evaluator feedback into targeted fixes.

For example:

```text
Criterion:
examples

Problem:
The lesson explains the concept but does not provide
a concrete example.

Required improvement:
Add a simple real-world example that demonstrates
the concept.
```

This creates actionable instructions for the regeneration step.

---

## 6. Targeted regeneration

The regeneration agent receives:

- the original learner request
- the existing lesson
- targeted failure analysis

It is instructed to preserve content that already works and modify only what is necessary to address the failed criteria.

The system allows a maximum of two retries.

This prevents an uncontrolled generation loop.

---

## 7. Rejection log

Every failed generation is recorded in the rejection log.

The log captures:

- attempt number
- failed criteria
- reasons for failure
- changes requested for the next attempt

This makes the improvement process inspectable instead of hiding failed generations.

The final output therefore contains both:

1. the final lesson
2. the rejection history

---

## Persistent Memory

LessonForge uses SQLite for persistent memory.

Two main types of information are stored:

### Lesson runs

```text
topic
learner level
learning goal
final status
number of attempts
timestamp
```

### Failure patterns

```text
criterion
failure pattern
recommended action
occurrence count
last seen timestamp
```

Recurring failure patterns can therefore influence future generations.

This allows the system to gradually build reusable quality guidance rather than treating every lesson generation as an isolated event.

---

## Technology Stack

- **Python** — application implementation
- **LangGraph** — stateful generation/evaluation workflow
- **LangChain** — LLM integration and structured outputs
- **Google Gemini** — lesson generation, evaluation, failure analysis, and regeneration
- **Pydantic** — structured data models and validation
- **Sentence Transformers** — local text embeddings
- **FAISS** — vector similarity search
- **SQLite** — persistent memory
- **pytest** — automated testing

---

## Project Structure

```text
lessonforge/
├── src/
│   ├── agents/
│   │   ├── evaluator.py
│   │   ├── failure_analyzer.py
│   │   ├── generator.py
│   │   ├── regenerator.py
│   │   └── rubric.py
│   │
│   ├── graph/
│   │   ├── memory_nodes.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── workflow.py
│   │
│   ├── memory/
│   │   └── store.py
│   │
│   ├── retrieval/
│   │   ├── loader.py
│   │   └── retriever.py
│   │
│   ├── models.py
│   └── output.py
│
├── knowledge/
│   └── rag_basics.md
│
├── tests/
│   ├── test_graph.py
│   ├── test_memory.py
│   ├── test_memory_graph.py
│   ├── test_failure_memory.py
│   └── test_retry_flow.py
│
├── data/
├── outputs/
├── test_refactor.py
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

---

## Running the Project

### 1. Create the environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -e ".[dev]"
```

### 3. Configure Gemini

Create a `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run tests

```bash
python -m pytest -q
```

The current automated test suite covers the graph routing, persistent memory, failure memory, and retry/rejection flow.

### 5. Run the end-to-end workflow

```bash
python test_refactor.py
```

The integration workflow generates and evaluates a beginner-level lesson on Introduction to RAG.

---

## Example Evaluation Flow

A typical self-evaluation cycle looks like:

```text
Attempt 1
─────────
FAIL

Failed criterion:
Examples

Reason:
The lesson explains retrieval conceptually but lacks
a concrete example.

Targeted fix:
Add a simple real-world example.

        ↓

Regeneration

        ↓

Attempt 2
─────────
PASS
```

The system then returns the passing lesson together with the rejection log.

---

## Design Decisions

### Why separate generation and evaluation?

A generator should not be the only authority on whether its own output is good.

The evaluator has a separate role and a strict rubric, creating a clear quality gate between generation attempts.

### Why structured outputs?

Pydantic models make the lesson and evaluation machine-readable and prevent the application from depending on fragile free-form text parsing.

### Why RAG?

The generator should have access to relevant external knowledge instead of relying entirely on model parameters.

### Why persistent memory?

Repeated failures contain useful information. Storing recurring failure patterns allows future generations to receive preventive guidance.

### Why limit retries?

Unlimited self-correction can increase latency and cost without guaranteeing improvement. LessonForge therefore caps retries at two.

---

## Testing

The project includes deterministic tests for the workflow and memory components.

The retry-flow test specifically verifies:

```text
FAIL
  ↓
Failure analysis
  ↓
Regeneration
  ↓
PASS
```

It also verifies that the rejection history survives the successful retry.

Current test status:

```text
9 passed
```

---

## Scope

LessonForge is intentionally focused on the assignment problem rather than attempting to build a complete production content platform.

The architecture can be extended later with additional knowledge sources, richer evaluation rubrics, more sophisticated memory retrieval, observability, APIs, or a user interface.