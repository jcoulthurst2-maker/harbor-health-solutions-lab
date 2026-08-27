# SQL + Data

> Build the ability to interrogate data, test explanations, and defend a conclusion with evidence.

[← Back to Solutions Lab](../../README.md)

## What I am building

SQL is the first technical layer of the Lab because it forces a simple discipline: **understand what the data actually says before deciding what the system should do.**

The goal is not memorizing syntax. I am building the ability to move from an unfamiliar dataset to a defensible explanation of what is happening, what is unusual, and what remains uncertain.

## Core capabilities

- `SELECT`, filtering, sorting, grouping, and aggregation
- joins across multiple sources
- subqueries and common table expressions
- window functions and comparative analysis
- metric definitions and denominator checks
- data-quality investigation
- anomaly and pattern detection
- timeline reconstruction
- separating correlation from a supported operational explanation
- communicating findings clearly enough for someone to act on them

## How the Lab trains it

SQL work is embedded inside missions rather than presented as isolated exercises.

A mission can provide several plausible explanations, conflicting records, incomplete data, or new evidence after the first query. I have to decide what to inspect, write the query, interpret the result, update the hypothesis, and explain what the evidence does **and does not** prove.

**Current example:** Operation Glasshouse uses identity, device, access, file, vendor, and physical-presence records to investigate a suspected information leak. The technical work includes joins, timeline analysis, repeated-pattern detection, and attribution discipline.

## Progression

### Foundation
Inspect unfamiliar tables, understand row grain, filter records, calculate useful summaries, and identify obvious outliers.

### Working depth
Join sources, decompose anomalies, reconcile conflicting definitions, build timelines, and test competing explanations.

### Advanced application
Use CTEs, window functions, more complex transformations, larger datasets, ambiguous metrics, and multi-step analytical investigations where the correct next query is not provided.

### Operational judgment
Translate the analysis into a recommendation while keeping evidence, inference, uncertainty, and action separate.

## What counts as proof

Completed work will be added here only after it has actually been done. Evidence can include:

- SQL files and query notebooks
- documented data assumptions
- investigation write-ups
- validated metrics
- before/after query approaches
- mission results and lessons learned
- short decision briefs based on the analysis

## Current status

**Active.** SQL + Data is the first live training track in the interactive Lab.
