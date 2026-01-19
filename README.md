# Learning LangGraph Basics

This repository demonstrates two execution models for code explanation workflows, both achieving the same business intent: providing clear explanations of code to users.

## Business Intent

Both `plan_then_execute` and `adaptive_execution` generate code explanations, but they use fundamentally different orchestration strategies.

## Execution Models

### `plan_then_execute`: Plan-First Pattern

**LangGraph** orchestrates the entire planning phase upfront:
- Creates a structured plan (explanation depth, focus area)
- Generates explanation based on plan
- Self-critiques and revises iteratively
- Produces final explanation before execution

**Temporal** handles execution:
- Waits for human approval
- Generates example usage
- Manages workflow state

This follows a traditional "plan thoroughly, then execute" pattern where LangGraph completes planning before Temporal takes over.

### `adaptive_execution`: Adaptive Step-by-Step Pattern

**LangGraph** is embedded as a Temporal activity, deciding each step dynamically:
- Plans the next single step (explain, improve, or done)
- Considers execution history to make decisions
- Runs repeatedly within Temporal's workflow loop

**Temporal** orchestrates the adaptive execution:
- Loops: plan next step → execute step → update state
- Handles human approval mid-flow
- Manages workflow lifecycle

This follows a "plan adaptively, one step at a time" pattern where LangGraph and Temporal collaborate continuously throughout execution.
