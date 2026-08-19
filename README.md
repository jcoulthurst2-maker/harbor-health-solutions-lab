# Harbor Health Command System

> **A fictional healthcare system with real-world problems.**

Harbor Health is a 32-week healthcare solutions build. Instead of doing disconnected coding exercises, I am rebuilding the same fictional hospital over time.

Each mission starts with a realistic healthcare problem. I investigate what is wrong, decide what needs to change, use the right technology, test the result, and explain what should happen next.

## Explore the build

If you are scanning this as a hiring manager, consultant, operator, or technologist, start here:

- **[Current mission](docs/CURRENT-MISSION.md)** — see the problem I am actively working through and what evidence the mission is expected to produce.
- **[Why these problems](docs/WHY-THESE-PROBLEMS.md)** — see why the project focuses on access, data trust, prior authorization, interoperability, AI, security, and adoption.
- **[How the build works](docs/HOW-THE-BUILD-WORKS.md)** — see the method I use to move from an operational problem to a tested solution.
- **[AI approach](docs/AI-APPROACH.md)** — see how I decide when AI belongs in a healthcare workflow and when it does not.
- **[32-week roadmap](docs/ROADMAP.md)** — see how SQL, Python, APIs, FHIR/HL7, AWS, and architecture build on one another.
- **[Future mission bank](docs/MISSION-BACKLOG.md)** — see the healthcare problems the system is designed to encounter next.
- **[Synthetic appointment sample](data/appointments_sample.csv)** — inspect a small sample of the fictional data behind Mission 001.

### What this project is meant to demonstrate

Not just coding. The build is designed to show how I approach **problem framing, operational diagnosis, data quality, workflow design, technical implementation, system integration, AI judgment, architecture, adoption, and executive communication** as parts of one healthcare solution.

## Why these problems

The problems are not random. They were chosen because they sit where healthcare operations and technology often fail together.

| Problem | Why it matters |
|---|---|
| **Patients cannot get appointments quickly** | Access problems can come from scheduling, staffing, capacity, referrals, or bad data. The first challenge is proving which problem is actually happening. |
| **People do not trust the data** | If the data is wrong, dashboards, automation, and AI can all produce confident but incorrect answers. |
| **Prior authorization slows care** | It combines payer rules, documentation, manual work, technology, and human judgment in one difficult workflow. |
| **Systems do not talk to each other** | Healthcare work often moves across EHRs, vendor tools, spreadsheets, portals, and internal systems. Important information can get lost between them. |
| **Healthcare data needs a common language** | APIs connect software. FHIR and HL7 help healthcare systems understand what the information means when it moves. |
| **AI is entering healthcare workflows** | The hard part is not calling a model. The hard part is deciding when AI is useful, testing it, keeping humans in control, and knowing what happens when it is wrong. |
| **Systems must stay secure and available** | Hospitals still have to protect sensitive information and keep care moving during outages, failures, or security incidents. |
| **A solution has to work for real people** | A technically correct tool still fails if staff hate it, it adds work, or it only works at one location. |

**The goal is to understand how these problems connect, not just learn isolated coding tricks.**

## How I work through a mission

1. **Understand the problem.** What is actually going wrong?
2. **Check the evidence.** What does the data show, and can I trust it?
3. **Decide what should change.** Is this a data, workflow, integration, software, or architecture problem?
4. **Build or connect what is needed.** Use the simplest technology that solves the problem well.
5. **Test it.** Make sure it works and look for ways it could fail.
6. **Fit it into the real workflow.** Think about staff, security, ownership, training, and adoption.
7. **Measure what happens next.** Did the change actually improve the hospital?

## Where the technology fits

- **SQL** helps me ask questions of hospital data.
- **Python** helps me automate work and build repeatable logic.
- **APIs** help different systems exchange information.
- **FHIR / HL7** help those systems exchange healthcare information correctly.
- **AWS + solution architecture** help me decide where the system runs, how it stays secure, how it handles failure, and how it scales.
- **AI** is used only when it is genuinely better than normal rules, SQL, or automation.

## How AI fits

AI has two roles here.

**AI as a build copilot:** I make the first attempt. AI can explain an error, give a hint, challenge my thinking, or review what I built. I still have to run the work, understand it, fix it, and explain why it works.

**AI inside Harbor Health:** Before adding AI to a hospital workflow, I first ask whether normal software or clear rules could solve the problem more safely and reliably. If AI adds real value, I have to define what it can see, what it can do, what humans still approve, what happens when it is wrong or unavailable, what gets logged, and how success is monitored.

**Sometimes the right answer is not to use AI at all.**

## 32-week build

| Time | Main focus | What Harbor Health is trying to fix |
|---|---|---|
| **Weeks 1–4** | SQL | Understand what is happening in the data and rebuild trust in the numbers. |
| **Weeks 5–10** | Python | Reduce repetitive manual work and turn analysis into repeatable tools. |
| **Weeks 11–14** | APIs | Connect systems that currently work in isolation. |
| **Weeks 15–20** | FHIR / HL7 | Make those connections work correctly with healthcare data. |
| **Weeks 21–32** | AWS + architecture | Make the whole system secure, reliable, scalable, and ready for a real organization. |

Architecture and AI judgment are part of the work from the beginning. The later weeks simply go deeper.

## Current mission

**Mission 001 — Appointment Access**

Harbor Health believes patients are waiting too long for appointments, but leadership does not trust the current dashboard enough to know why.

I inherit a synthetic appointment dataset. My first job is to figure out what can actually be proven from it.

We start here for a reason: **before the hospital automates anything, connects more systems, or adds AI, it needs a trustworthy understanding of the problem.**

[Open the current mission](docs/CURRENT-MISSION.md)

## Project status

This is an **active build**, not a finished case study. Completed missions will be added only as the work is actually completed.

## End goal

By the end, Harbor Health should read like one complete healthcare transformation case: the original problems, the evidence, the systems built, the integrations, the healthcare data standards, justified AI components, cloud design, security decisions, rollout plan, and the outcomes that should be measured.