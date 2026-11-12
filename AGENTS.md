# AGENTS.md

## Execution Strategy

Tasks are defined in `plan/PLAN.md#Tasks`, each with a stable ID (TID-X, where X denotes the id), and assigned sequentially by the developer.

**Execute only the explicitly assigned task. Never proceed to the next task without an explicit instruction.**

### Clarification

- Ask the developer before proceeding when uncertainty affects requirements, scope, architecture, or other consequential decisions.
- Resolve routine implementation details independently, following existing conventions and the simplicity principle.

### PLAN.md

- Project goals, requirements, source material location and tasks are defined in `plan/PLAN.md`.
- Owned exclusively by the developer. NEVER modify, rewrite, reorder, or delete its contents.
- Treat it as the authoritative source for requirements and acceptance criteria.
- If a task is ambiguous, contradictory, or problematic, report the issue, its implications, and a proposed resolution. The developer decides and applies any change.

### STATE.md

`plan/STATE.md` is maintained by the agent and is a snapshot of the current execution state, not a log.

- Contains only what another agent needs to resume work: current task ID, completed and remaining work, relevant files, verification results, blockers, next action.
- Update it after completing a task, on a blocker, or when ending a session.
- Replace obsolete information instead of accumulating it.
- The repository and executed checks are authoritative. Never claim work is complete or verified without evidence.

### DECISIONS.md

Record significant decisions in `plan/DECISIONS.md`. Do not record trivial implementation choices.

- One entry per decision: date (YYYY-MM-DD), task ID, decision, brief rationale, and whether it was approved by the developer.
- Append only. A changed decision gets a new entry that references the one it supersedes.
- Ask the developer before recording a decision here.

### Session Protocol

At the start of a session:

1. Read all markdown files in the `plan/` folder.
2. Inspect the repository and Git status; reconcile them with STATE.md.
3. Work only on the assigned task or prompt the developer for further action.

Before ending a session or completing a task:

1. Verify the task's acceptance criteria are met, including any checks they specify.
2. Confirm PLAN.md is unchanged (`git diff --quiet -- plan/PLAN.md`).
3. Update STATE.md and record any undocumented decisions in STATE.md, marked as needing developer clarification.
4. Summarize what changed, what was verified, and what remains.

### Development lifecycle

1. For each task create a corresponding branch, you are allowed to work on that task only in that branch
2. For task completion, validate against the tasks acceptance criteria
   IMPORTANT - You must not commit and push anything unless instructed by the developer
4. The developer will review and etl. instruct you with further actions

## Coding Standards

1. Use current stable library versions and idiomatic approaches.
2. Prefer the simplest solution that satisfies the requirements. NEVER over-engineer: no speculative abstractions, unnecessary dependencies, or unrelated features.
3. Avoid unnecessary defensive programming, but keep essential error handling.
4. Follow established conventions, reuse existing code, and keep changes focused.
5. Never commit secrets.
6. Keep documentation, including README, concise.
7. Never use emojis in code, UI, documentation, or commit messages.
8. For any finding, include file name and line number.

## IMPORTANT

- If I ask a question, then ALWAYS answer it before you take any action, DO NOT edit, commit or push anything as part of your answer.
- If you don't know something, admit it and ALWAYS ask for clarification, DO NOT make up anything as a fact.
