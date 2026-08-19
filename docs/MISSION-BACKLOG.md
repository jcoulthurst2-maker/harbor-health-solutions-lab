# Future Work

## What this page is for

This page shows **how Harbor Health becomes harder after the current work**.

The problem-context page explains why the healthcare issues matter. The roadmap explains when capabilities are introduced. This page is only about the next level of complexity the lab will have to handle.

## How the difficulty increases

**From one answer to conflicting evidence** — later problems introduce bad data, competing metrics, referral leakage, and capacity tradeoffs so the first explanation is not always the right one.

**From one workflow to connected workflows** — solutions begin crossing teams, vendor tools, downstream systems, and write-back paths, creating ownership and failure questions that do not exist in a single-system exercise.

**From a working integration to healthcare-grade exchange** — the lab adds FHIR, HL7, SMART context, and mixed-system environments where data has to keep the correct meaning across boundaries.

**From automation to judgment under uncertainty** — later work introduces AI use cases, unsupported outputs, clinician distrust, outages, human overrides, and cases where the correct decision is to use simpler rules instead.

**From normal operation to failure** — security, credential exposure, ransomware, downtime, excessive access, recovery, and continuity force the system to keep working safely when conditions are bad.

**From a pilot to enterprise scale** — multi-clinic rollout, reliability, cost, training breakdowns, feedback gaps, pilot rejection, phased launch, and support burden test whether a solution can survive organizational complexity.

## Final integrated case

The final Harbor Health case should bring the work together for a mixed executive and technical audience: what the organization was facing, what evidence supported the decisions, what was built, how the architecture evolved, what was validated, what would be required for go-live, what risks remain, and what leadership should do next.

## What good looks like

By the end, Harbor Health should be difficult because the decisions are interconnected—not because the code is artificially complicated.