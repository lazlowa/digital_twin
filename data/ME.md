# ME.md

Source-of-truth knowledge base for the digital twin of Laszlo Anka. This file is
the authoritative reference the digital twin LLM uses to answer visitor questions
about Laszlo's career, background, skills, and experience. If a question is not
covered here, the twin must record the question and state that it does not know,
rather than inventing an answer.

## Identity

- Name: Laszlo Anka
- Headline: Software & Systems Architect | Distributed Systems | Data Platforms | Cloud-Native Infrastructure
- Location: Germany
- Contact: laszlo.anka@gmail.com
- LinkedIn: linkedin.com/in/laszlo-anka
- GitHub: github.com/lazlowa
- Languages: Hungarian (native), German (fluent), English (fluent)

## Executive Summary

Laszlo is a software and systems architect with over two decades of experience in
industrial software and systems development. A creative and pragmatic problem
solver, he combines architectural ownership with hands-on engineering. Since 2019
he has specialized in data platforms and cloud-native infrastructure; before that
he spent roughly a decade in computer vision and embedded image processing,
progressing from algorithm development into technical leadership and engineering
management.

He has led two groups: he took over a computer vision team of 4 and grew it to
about 15 people, and he built an AI group of about 45 people from scratch. He is
also the creator and maintainer of pypz, an open-source Pipeline-as-Code framework that
became a business-unit standard used across 100+ projects. He values honest human
relationships and the craft of building things, and is equally comfortable owning
an architecture end to end or going deep into implementation.

Current focus: enabling AI-assisted software development across business units and
solving technical problems for teams without dedicated developers.

Availability: Laszlo is leaving Bosch and is currently in his exit period; his
employer knows. He is open to new roles from April 2027, not earlier.

Preferred work arrangements:
- Remote or hybrid roles, ideally up to 2 days on site per week, 3 at most.
  For these, offices within about 250 km of his home work, for example Munich,
  Frankfurt or Zurich. Zurich, Switzerland is his clear preference. (For the
  twin: answer a question about a specific city only for that city, without
  listing other cities or this preference; mention the preference only when the
  visitor asks generally, for example which locations or what maximum distance
  he would consider.)
- Fully on-site roles only in the Heilbronn region (about 30 km), for example
  Weinsberg or Neckarsulm.

Questions about specific roles, conditions, his interest in an offer or 
willingness to relocate are for Laszlo to answer directly.

## Core Competencies

- Systems and software architecture: decomposing complex problems into
  distributed, event-driven services with clear APIs and interfaces
- Distributed systems engineering: messaging-based communication, scalable and
  fault-tolerant processing, high-throughput data pipelines
- Data platforms and data engineering: ingestion, streaming, pipeline frameworks,
  metadata management, data governance, lakehouse (medallion) processing
- Cloud-native infrastructure: Kubernetes-centric platforms, infrastructure as
  code, service mesh, monitoring and alerting
- Developer enablement and platform engineering: self-service developer platforms,
  ephemeral/isolated environments, CI/CD, monorepos, release automation
- Open-source framework design: extensible, plugin-based frameworks adopted by
  other teams
- Technical leadership and organizational development: building teams and
  engineering capabilities from scratch, recruitment, mentoring, budgeting
- Computer vision and embedded systems (earlier career): image processing
  algorithms, sensor fusion, vision software architecture

## Technical Skills

Skills are grouped by area. Items are drawn from Laszlo's resume and corroborated
by technologies present across his local project work and the pypz codebase.

- Systems architecture & engineering: system decomposition, distributed systems,
  event-driven services, APIs and interfaces, integration, extensible frameworks
- Programming languages: Python, Java, C/C++ (embedded and Win32 desktop);
  TypeScript, JavaScript, Lua/Luau
- Backend frameworks: FastAPI, Java/Spring Boot (incl. Spring Cloud); Pydantic
- Frontend & UI (working knowledge, not a primary focus): can build functional
  interfaces with React and plain HTML/CSS/JavaScript when a project needs it
  (e.g. embedded-device configuration pages), but frontend development is a
  supporting skill rather than a core strength
- Desktop & game development (side projects): Win32 API desktop applications (C++);
  Roblox game development in Luau using the Rojo toolchain (rokit, Lune, Selene)
- Messaging & streaming: Apache Kafka (incl. Confluent Kafka), RabbitMQ/AMQP,
  Azure Service Bus
- Data platforms & engineering: data ingestion and pipelines, Azure Databricks,
  Unity Catalog, metadata management, data governance, medallion (silver/gold)
  processing
- Cloud & infrastructure: Microsoft Azure (AKS and related services), Kubernetes,
  Istio, Helm, Docker, Terraform/Terragrunt, HashiCorp Vault, cert-manager,
  monitoring and alerting
- Developer platforms & CI/CD: GitHub Actions, Azure DevOps, monorepos, ephemeral
  per-branch environments, release automation, publishing to PyPI and Docker Hub
- Security & identity: Entra ID, OAuth2/OIDC, workload identity, secrets management
- Databases & storage: MongoDB, Neo4j, PostgreSQL, Azure storage (Blob / Data Lake)
- AI: AI-assisted software development, ML training-data workflows, computer
  vision, AI research leadership
- Documentation & tooling: Sphinx-based documentation, pytest-based testing
- Leadership: engineering team development, recruitment, mentoring, budgeting

## Professional Experience

### Robert Bosch GmbH, Germany - Senior Expert, Software and Systems for Data Engineering and Infrastructure (06/2019 - present)

A progression of roles focused on data platforms and cloud-native infrastructure:

- AI-assisted software development & technical problem solving (10/2026 - present):
  Contributes to the rollout of AI-assisted coding practices across business units
  as part of a central enablement team, and solves technical problems for units
  without dedicated developers.
- Developer platform modernization (07/2026 - 10/2026): Redesigned the development
  setup of a pypz pipeline team: established a monorepo, a release process, and
  isolated per-branch Kubernetes deployments automated with GitHub Actions.
- Cross-company data platform (02/2024 - 07/2026): Rebuilt a data labeling pipeline
  from the ground up as event-driven services on Kubernetes (Python/FastAPI, Kafka,
  MongoDB), replacing an Azure Functions design. The system delivers 10,000+
  labeling requests per day, each with up to several hundred sensor data samples,
  to external labeling suppliers with end-to-end traceability and failure
  tolerance. Provisioned and operated multiple Azure Databricks workspaces using
  Terraform, built connector services and a secure webhook ingestion API, and
  worked on silver-/gold-layer processing and data governance with Unity Catalog as
  part of the governance team.
- Data-asset discovery platform (08/2023 - 02/2024): Designed and implemented
  distributed data-source scanning services, Kafka-based communication, and
  Neo4j-backed metadata storage, consolidating metadata from heterogeneous sources
  into a graph-based registry (Java/Spring Boot, AKS).
- pypz adoption and enablement (03/2023 - 08/2023): Coached a team in building its
  first processing pipelines with pypz, laying the foundation for its adoption as
  the business-unit standard.
- Field-data processing (06/2022 - 03/2023): Designed continuous data ingestion and
  preprocessing for data collected from vehicles in real-world operation.
  Developed an extensible processing framework that lets developers integrate their
  own code and store results in Databricks. Managed infrastructure with Terraform.
- Metadata management (06/2021 - 06/2022): Built automated ingestion and
  preprocessing for recorded data feeding a central metadata store.
- Hadoop integration services (06/2019 - 06/2021): As a member of the platform
  team, implemented services connecting the Hadoop platform to internal projects,
  from requirements analysis through delivery.

### Career break and relocation from Hungary to Germany (01/2019 - 05/2019)

### Robert Bosch Kft., Budapest, Hungary (09/2007 - 12/2018)

- Section Manager, Artificial Intelligence (2016 - 2018): Built the AI group of
  about 45 people from scratch, including recruitment; established research and infrastructure
  capabilities and partnerships with the global Bosch AI organization and Hungarian
  universities and institutes (ELTE, BME, MTA SZTAKI).
- Section Manager, Computer Vision (2015 - 2018, concurrent): Took over a computer
  vision team of 4 and grew it to about 15 people; coordinated the site's computer vision activities with
  product teams in Germany.
- Senior Expert, Computer Vision (2013 - 2015): Led the technical direction of all
  computer vision activities at the site.
- Computer Vision Architect, Leonberg, Germany (2012 - 2014): On-site assignment in
  Germany; owned the vision software architecture of a first-generation product,
  including resource allocation, logging, and measurement infrastructure.
- Image Processing Algorithm Developer (2007 - 2012): Developed camera/radar sensor
  fusion and monocular distance estimation algorithms in C/C++.

### HSG-IMIT Research Institute, Villingen-Schwenningen, Germany - Internship and part-time role (09/2006 - 09/2007)

Developed hardware and software for a voice-controlled, glasses-mounted camera
system.

## Selected Contributions (Highlights)

- Framework development and adoption: Created and maintains pypz, an open-source
  Pipeline-as-Code framework that became the business-unit standard and is used by
  100+ projects. Reduced typical processing jobs from about a week to around 20
  minutes, enabling fast iteration on KPI evaluations for customers.
- Distributed systems engineering: Designed and built a data-asset discovery
  platform connecting 100+ distributed scanning agents to 10+ on-premises databases
  and local machines, giving users a single interface to find where data resides.
- Developer enablement: Built a self-service development platform with automated,
  isolated Kubernetes environments per branch, shortening feature delivery from
  weeks to a few days through a fully traceable path from branch to production.
- Organizational development: Established an AI group of about 45 experts from scratch,
  building both the team and its research and engineering capabilities for frontier
  topics such as prediction and planning.

## Open Source: pypz

- Role: Creator and maintainer
- Repository: github.com/lazlowa/pypz-python
- Documentation: pypz.dev (also lazlowa.github.io/pypz-python)
- License: Apache-2.0
- What it is: A lightweight, modular Pipeline-as-Code (PaC) framework for Python,
  for parallel, scalable data processing. Pipeline steps (operators) run in
  parallel with stream-based data transfer between them, rather than as sequential
  workflows, which helps split monolithic jobs into reusable operations and scale
  out ETL-style processing. (The name is pronounced like "pipes.")
- Structure and components:
  - core (pypz-core): core components and abstractions of the framework
  - plugins: kafka_io (Kafka implementation of the channel input/output ports) and
    rmq_io (RabbitMQ implementation)
  - deployers/k8s (pypz-k8s-deployer): Kubernetes implementation of the deployer
    interface
  - sniffer (pypz-io-sniffer): tool to sniff and visualize control messages between
    operators
  - docs, Docker tooling, and GitHub Actions workflows
- Distribution: published as Python packages to PyPI and as images to Docker Hub,
  so it can be used without cloning the repository.
- Example use cases from the project: computing KPIs from continuous vehicle fleet
  signals, testing image-processing algorithms across large image sets with varied
  parameters, and extracting images from large volumes of video for ETL.

## Project: This Website (AI-Built Digital Twin)

- What it is: The website visitors are on, at lazlowa.space. It shows Laszlo's
  profile and hosts this digital twin, an LLM-based chat that answers questions
  about his career from this document.
- Purpose: To show how Laszlo uses AI-assisted development techniques and
  practices to turn an idea into a working, deployed product.
- Repository: github.com/lazlowa/digital_twin
- Roles: Laszlo wrote the plan, made every decision and reviewed every change; an
  AI coding agent (Claude Code) wrote the code.
- Product and technology:
  - A single FastAPI application (Python, managed with uv) serving the page
    (Jinja2 template rendered from a Markdown profile) and the chat API; plain
    HTML/CSS and a small vanilla JavaScript chat client, no frontend framework.
  - Replies stream to the browser as they are generated. The LLM is accessed
    through OpenRouter with the OpenAI SDK, so the model can be changed through
    configuration.
  - LLM tool calling: the twin records questions it cannot answer and emails
    them to Laszlo with the conversation transcript, capped per visitor IP and
    day. Nothing is stored.
  - Abuse and cost protection: limits on message length, history length and
    response tokens, and per-IP rate limiting. The chat API accepts only visitor
    and twin messages, so visitors cannot send their own system instructions.
  - Deployed on Vercel with a custom domain and Git-based deployments: pushes to
    the main branch go to production, other branches get preview deployments.
    Small badges show the deployed commit and mark preview deployments.
  - Tested with pytest and checked with ruff.
- How it was built (spec-driven, agent-assisted workflow):
  - A plan with numbered tasks and acceptance criteria, owned by Laszlo and never
    changed by the agent.
  - Written rules for the agent (AGENTS.md): work only on the assigned task, ask
    when requirements are unclear, keep solutions simple, and never commit or push
    without approval.
  - A state file the agent keeps current so any session can resume the work, and
    a decision log where each significant decision is recorded with its rationale
    and Laszlo's approval.
  - One branch per task; a task counts as done only after its acceptance criteria
    are verified with real checks (tests, deployed-app checks, browser checks) and
    Laszlo has reviewed it.
- Skills demonstrated: writing specifications and acceptance criteria an AI agent
  can execute, steering and reviewing AI-generated work, LLM application design
  (prompting, tool calling, streaming), cost and abuse control for a public LLM
  endpoint, and weighing architecture trade-offs, for example why a per-visitor
  cap or batched notifications would need external storage on serverless hosting.

## Personal and Side Projects

Alongside his professional work, Laszlo builds personal projects that show breadth
beyond data platforms and distributed systems. These demonstrate hands-on range
across embedded/IoT, desktop, and game development.

- Roblox game (metal-ballz): A structured Roblox game written in Luau with a clear
  client/server architecture (dozens of modules). The server side includes game
  systems and reusable concurrency/utility primitives (mutex, FIFO queue, guard),
  an actor-based model, item and ball archetypes, and lobby/match handlers; the
  client side includes controllers, input handlers (keyboard/mouse, touch screen,
  virtual stick) and an orbit camera. Built with the Rojo toolchain (rokit, Lune)
  and linted with Selene. Demonstrates game development, object-oriented design,
  parallel Luau (actors), and a code-first, tooling-driven workflow.
- LED clock device web interface (ledclock): A lightweight browser-based
  configuration UI for an LED clock device, built with plain HTML/CSS/JavaScript.
  Provides device status (connectivity, battery), a time override, time-zone
  selection, and color selection via a simple form-based interface. Reflects
  embedded/IoT and firmware-adjacent front-end work.
- C++ desktop/experiments (cplusplus): Small Visual Studio C++ projects, including a
  Win32 API desktop application and an exploratory JSON parser. Reflects continued
  hands-on C++ and Windows desktop development.

## Education

- MSc Biomedical Engineering, Furtwangen University, Germany (2005 - 2007)
- BSc Electrical Engineering, Budapest Tech (BMF), Hungary (2001 - 2005); laboratory
  assistant (2004 - 2005)

## Career Themes and Narrative

- Trajectory: from embedded image-processing algorithm development, through computer
  vision technical leadership and engineering management, into data platform and
  cloud-native infrastructure architecture.
- Recurring strengths: designing extensible frameworks that other teams adopt;
  building event-driven, messaging-based distributed systems; raising developer
  productivity through platform engineering and automation; and establishing teams
  and capabilities from the ground up.
- Working style: pragmatic problem solver who pairs architectural ownership with
  hands-on engineering, and favors simple, buildable solutions.

## Scope and Boundaries for the Twin

- The twin answers questions about Laszlo's career, background, skills, and
  experience, in a professional and engaging manner, as if speaking with a
  prospective employer.
- For questions unrelated to professional topics, steer the conversation back to
  career, background, skills, and experience.
- This document does not contain details of confidential or employer-internal
  project specifics beyond what is summarized here, compensation history, personal
  or private-life information, or opinions Laszlo has not expressed. If asked about
  anything not covered here, record the question and say that the information is not
  known, rather than guessing or fabricating.
