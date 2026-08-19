# Harbor Health Command System

> **A fictional healthcare system with real-world problems.**

Harbor Health is a 32-week healthcare solutions build. I am rebuilding the same fictional hospital over time so the work shows how I diagnose problems, design solutions, use technology, and move from evidence to implementation.

## 60-second scan

**What this is:** a healthcare transformation case in progress, not a collection of disconnected coding exercises.

**What it covers:** appointment access, data quality, referral flow, prior authorization, system integration, FHIR/HL7, AI, security, adoption, outages, and scale.

**What I am demonstrating:** problem framing, operational diagnosis, workflow design, technical implementation, integration, AI judgment, architecture, change management, and executive communication.

**Current mission:** Harbor Health believes patients are waiting too long for appointments, but leadership does not trust the current dashboard enough to know why. I am starting by establishing what the data can actually prove.

**Why that comes first:** if the hospital cannot trust its basic operational data, then adding automation, integrations, or AI simply makes the wrong answer move faster.

## Explore the build

- **[Current mission](docs/CURRENT-MISSION.md)** — the problem I am actively working through and the evidence the mission should produce.
- **[Why these problems](docs/WHY-THESE-PROBLEMS.md)** — why the project focuses on access, data trust, prior authorization, interoperability, AI, security, and adoption.
- **[How the build works](docs/HOW-THE-BUILD-WORKS.md)** — the method for moving from a healthcare problem to a tested solution.
- **[AI approach](docs/AI-APPROACH.md)** — how I decide when AI belongs in a workflow and when it does not.
- **[32-week roadmap](docs/ROADMAP.md)** — how SQL, Python, APIs, FHIR/HL7, AWS, and architecture build on one another.
- **[Future mission bank](docs/MISSION-BACKLOG.md)** — the healthcare problems Harbor Health is designed to encounter next.
- **[Synthetic appointment sample](data/appointments_sample.csv)** — a small sample of the fictional data behind Mission 001.

## Why these problems

The problem set is deliberate. Each issue sits where healthcare operations and technology often break down together.

| Problem | Why it matters |
|---|---|
| **Patients cannot get appointments quickly** | Access problems can come from scheduling, staffing, capacity, referrals, or bad data. The challenge is proving which problem is actually happening. |
| **People do not trust the data** | If the data is wrong, dashboards, automation, and AI can all produce confident but incorrect answers. |
| **Prior authorization slows care** | It combines payer rules, documentation, manual work, technology, and human judgment in one difficult workflow. |
| **Systems do not talk to each other** | Healthcare work often moves across EHRs, vendor tools, spreadsheets, portals, and internal systems. Important information can get lost between them. |
| **Healthcare data needs a common language** | APIs connect software. FHIR and HL7 help healthcare systems understand what the information means when it moves. |
| **AI is entering healthcare workflows** | The hard part is deciding when AI is useful, validating it, keeping humans in control, and planning for failure. |
| **Systems must stay secure and available** | Hospitals still have to protect sensitive information and keep care moving during outages or security incidents. |
| **A solution has to work for real people** | A technically correct tool still fails if staff hate it, it adds work, or it cannot scale beyond one site. |

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

**AI inside Harbor Health:** Before adding AI to a hospital workflow, I first ask whether normal software or clear rules could solve the problem more safely and reliably. If AI adds real value, I define what it can see, what it can do, what humans still approve, what happens when it is wrong or unavailable, what gets logged, and how success is monitored.

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

## Project status

This is an **active build**, not a finished case study. Completed missions will be added only as the work is actually completed.

## End goal

By the end, Harbor Health should read like one complete healthcare transformation case: the original problems, the evidence, the systems built, the integrations, the healthcare data standards, justified AI components, cloud design, security decisions, rollout plan, and the outcomes that should be measured.