# Retrieval-Augmented Generation (RAG)

## What is RAG?

Retrieval-Augmented Generation, commonly called RAG, is a technique that
combines information retrieval with language generation.

Instead of asking a language model to answer a question using only the
information it learned during training, a RAG system first retrieves
relevant information from an external knowledge source. That information
is then provided to the language model as context for generating the answer.

## Why is RAG useful?

Language models may not have access to an organization's private or
recent information. They can also produce incorrect information when
they do not have sufficient context.

RAG helps address these problems by retrieving relevant information from
a controlled knowledge source before generating a response.

Common use cases include:

- Question answering over company documentation
- Searching technical documentation
- Customer support knowledge bases
- Internal knowledge assistants
- Document-based research

## How does a basic RAG system work?

A simple RAG pipeline generally contains these steps:

1. A user asks a question.
2. The question is converted into a representation suitable for searching.
3. The system searches a knowledge base for relevant content.
4. The most relevant pieces of content are retrieved.
5. The retrieved content is provided to the language model as context.
6. The language model generates an answer using that context.

## Example

Suppose a company has documentation describing its employee leave policy.

An employee asks:

"What is the maximum number of paid leave days I can carry forward?"

A normal language model may not know the company's specific policy.

A RAG system can search the company's documentation, retrieve the section
describing carry-forward rules, and provide that information to the language
model. The model can then generate an answer based on the retrieved policy.

## Important terminology

### Retrieval

The process of finding information from a knowledge source that is relevant
to a user's question.

### Embedding

A numerical representation of text that captures aspects of its meaning.
Embeddings allow text to be compared based on semantic similarity.

### Vector store

A system used to store and search vector representations of information.

### Context

The information retrieved from the knowledge source and provided to the
language model when generating a response.

### Grounding

Constraining a model's response using relevant external information rather
than relying only on the model's internal knowledge.