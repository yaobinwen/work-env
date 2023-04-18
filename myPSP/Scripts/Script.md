# myPSP Script

## 1. Overview

This script defines my daily work process, including the activities, outputs, and measurements. The purpose is twofold:

- For me, the process helps find out what I can improve in order to do my work better.
- For employer, the process helps produce results of higher and higher quality.

This script has the following sections:

- `Version` shows the version of the current script. I'm using `yyyy-mm-dd` as the version number because I don't expect many changes within one day. I am not using [`Semantic Versioning`](https://semver.org/) because it is designed for software products but this product doesn't have the concepts like "API", "backward-compatibility", or "patch".
- `Purposes` define what specific areas I want to improve in the work I do for my current employer.
- `Definition` has the detailed definition of my personal software process.
- `Glossary` defines the terms used in this script that may not be known to everybody.

## 2. Version

2023-04-18

## 3. Purposes

| Purpose | Measurements | Notes |
|:--------|:-------------|:------|
| Find as many bugs as possible before the delivery of my task. | The number of bugs that are found after I publish my work. ||
| Increase my throughput so I can get as many tasks done as possible. | The number of my Pull Requests that are ready for review and merge in one week. I don't use the number of _merged_ Pull Requests because the review depends on others availability. If I use the merged number, that also measures the others' throughput, not just mine. ||

## 4. Definition

### 4.1 Brief

In this phase, I get briefed about the basics of the task:
- Priority
- Context: Whose work is this task related to; when is this task supposed to be finished.

However, chances are I will not get the complete information about the task and will need the subsequent phases to explore it.

### 4.2 Explore

In this phase, I explore the unknown territory of the task in order to make things clear. For example:
- What solutions are possible and which one is preferred?
- What technical issues are there and how to solve them?

The output is the **task breakdown** that lists what should be done in order to finish the task.

### 4.3 Plan

In this phase, I estimate the size and needed time for each item in the task breakdown.

The output is the task breakdown with size and time estimates.

### 4.4 Develop & Test

In this phase, I work on the task implementation and testing.

In addition to the work itself, I also need to do two things:
- Log the actual time I spend on the task.
- Take periodical breaks to review whether I am still in the scope.

### 4.5 Reflect

In this phase, I reflect upon my whole day's work in the following aspects:
- Whether I have followed the defined process.
- Any other thoughts on what I can improve.

## 5. Glossary

- Task breakdown: A list of things that to be done in order to finish the task. Developing the breakdown requires some insight into the task composition.
