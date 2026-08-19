# Harbor Health Command System

> **A fictional healthcare system with real-world problems.**

Harbor Health is a 32-week healthcare solutions build. I am rebuilding the same fictional hospital over time so the work shows how I diagnose operational problems, decide what technology actually belongs, build enough of the solution to prove it, connect it to the larger system, plan for failure and adoption, and explain the decision to both executives and technical teams.

## 60-second scan

**What this is:** one evolving healthcare transformation case, not a collection of disconnected coding exercises.

**What it covers:** appointment access, data quality, referral flow, prior authorization, system integration, FHIR/HL7, AI, security, adoption, outages, and scale.

**What I am demonstrating:** operational diagnosis, workflow redesign, SQL/Python implementation, API and healthcare-data integration, AI judgment, solution architecture, change management, validation, and executive communication.

**How the system works:** each mission begins with a believable hospital failure. I investigate the evidence, decide whether the problem needs a workflow change, data fix, automation, integration, AI, or architecture change, build the smallest useful solution, test how it can fail, then think through rollout, ownership, security, adoption, and measurement.

**Current mission:** Harbor Health believes patients are waiting too long for appointments, but leadership does not trust the current dashboard enough to know why. I am starting by establishing what the data can actually prove.

**Why that comes first:** if the hospital cannot trust its basic operational data, then adding automation, integrations, or AI simply makes the wrong answer move faster.

## What I am actually working on

The technical skills are introduced because the hospital problem requires them:

- **SQL** — question hospital data, calculate operational measures, find patterns, and test whether the data itself is trustworthy.
- **Python** — turn repeated manual work into reusable logic and tools.
- **APIs** — connect systems that currently operate in isolation.
- **FHIR / HL7** — make those connections work correctly with healthcare information.
- **AWS + solution architecture** — decide how the full system should run securely, reliably, and at scale.
- **AI** — decide where AI genuinely adds value, where fixed rules are safer, and how human control, fallback behavior, logging, and monitoring should work.

The project also includes the parts that determine whether technology succeeds in a real organization: workflow ownership, staff adoption, security, failure planning, rollout strategy, and measurable outcomes.

## Explore the build

- **[Current mission](docs/CURRENT-MISSION.md)** — the problem I am actively working through and the evidence the mission should produce.
- **[How the build works](docs/HOW-THE-BUILD-WORKS.md)** — the method for moving from a healthcare problem to a tested solution.
- **[Why these problems](docs/WHY-THESE-PROBLEMS.md)** — why the project focuses on access, data trust, prior authorization, interoperability, AI, security, and adoption.
- **[AI approach](docs/AI-APPROACH.md)** — how I decide when AI belongs in a workflow and when it does not.
- **[32-week roadmap](docs/ROADMAP.md)** — how SQL, Python, APIs, FHIR/HL7, AWS, and architecture build on one another.
- **[Future mission bank](docs/MISSION-BACKLOG.md)** — the healthcare problems Harbor Health is designed to encounter next.
- **[Synthetic appointment sample](data/appointments_sample.csv)** — a small sample of the fictional data behind Mission 001.

## The problem set

The missions are built around places where healthcare operations and technology often break down together:

- patients cannot get appointments quickly;
- dashboards and source data disagree;
- referrals disappear between steps;
- prior authorization slows care;
- vendor systems do not exchange information cleanly;
- healthcare data needs consistent meaning across systems;
- AI outputs can be wrong, ignored, or unavailable;
- systems must remain secure and usable during failure;
- technically correct tools still fail when staff do not trust or adopt them;
- a solution that works in one clinic may need to scale across many.

A mission is never created just because it is “time to learn Python” or “time to learn AWS.” The hospital problem comes first. The technology appears because Harbor Health now needs it.

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

This is an **active build**, not a finished case study. Completed missions and evidence will be added as the work is actually completed.

## End goal

By the end, Harbor Health should read like one complete healthcare transformation case: the original problems, the evidence, the systems built, the integrations, the healthcare data standards, justified AI components, cloud design, security decisions, rollout plan, adoption strategy, failure modes, tradeoffs, and the outcomes that should be measured.