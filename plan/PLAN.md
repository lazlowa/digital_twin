# Project Overview

Build a digital twin of the user as a single-page web application.
The page shall contain the resume of the user with an executive summary about the skills and competencies.
The page shall contain a chat interface, where the visitor can ask professional questions about the user.
On the other side an LLM will be configured, which shall answer those questions according to the following instructions:

"
You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Rules:

- Engage with the user.
- Be professional and engaging, as if talking to future employer who came across the website.
- Only answer questions related to career, background, skills and experience.
- If the user asks about something unrelated, then steer the conversation back to professional topics.
- Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT:
If you don't know the answer, use your tool to record the question, and then tell the user that you don't know. Never make up an answer.
"

## Terms

- user/developer: the subject of the digital twin project
- visitor: the person visiting the digital twin side and asking questions

# Tasks

IMPORTANT - before executing a task, always ask clarifying questions, if you don't know or understand something, engage in constructive
discussion, if you see improvement potentials related to tasks.

For each task, start by creating a corresponding branch and work on the specific task in that branch.

## TID-1


### Description

This task is about creating the source of truth about the skills, competencies and experiences of the user in a format, which
can be used by the digital twin LLM to answer questions. For this, you will be provided the following sources:

- local folder with projects (will be provided via prompt)
- remote github repositories (will be provided via prompt)
- resume in `data` folder

### Acceptance Criteria

- A file called `TWIN.md` created in the `data` folder, which contains the described comprehensive summary.
- `plan/STATE.md` updated
