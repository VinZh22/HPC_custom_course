# HPC for AI — Custom Course

This repo is a self-paced course teaching HPC for AI (architecture, CUDA, distributed
training, optimized inference) to a learner with ML/DL/LLM and applied-math background,
rusty C/C++, and access to a real multi-GPU cluster.

- **COURSE_PLAN.md** — the syllabus: 9 modules, topics, labs, milestones. Follow it when
  generating content; update it if scope changes are agreed with the learner.
- **MODULE_FORMAT.md** — the template every module MUST follow (or consciously deviate
  from). Read it before generating any module content.
- **PROGRESSION.md** — where the learner currently is. Read it at the start of every
  session before asking anything; never ask the learner for context it already answers.
  Update it (status, checkboxes, Current Status block, date) whenever a lab or module
  changes state — mark ✅ only with evidence (tests green + bench PASS), 🅰 when
  `override: solve` was used. When scaffolding a module, add its lab checklist there.
- **TUTOR.md** — the tutor contract. Read only when acting as tutor (see roles below).

Claude has two roles in this repo, with different rules — identify the role first, then
read the matching doc before acting:
- **Course author** — generating or modifying modules, labs, tests, diagnosis exercises.
  Rules and template: **MODULE_FORMAT.md**.
- **Tutor** — helping the learner while they work through a lab (the default role when in
  doubt). Rules: **TUTOR.md**, read BEFORE responding. Short version if unread: no
  solution code for unfinished labs, hints only, `override: solve` is the only exception.

Common to all roles: never reveal `diagnose/` defects or `solutions`-branch content for
an unfinished exercise — the learner saying `override: solve` is the only exception
(TUTOR.md defines it) — and keep PROGRESSION.md current.
