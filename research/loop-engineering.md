# Loop Engineering — research + a portable framework for any repo

> **What this is.** A grounded reference on *loop engineering* (the emerging practice Anthropic's Claude
> Code team + Addy Osmani/Boris Cherny/Peter Steinberger set out in mid-2026) **plus a reusable framework
> you can drop onto any project/repo** to make it "code like a loop." Written to be portable: the
> principles are fixed; each repo swaps in its own config. Applied to this repo at the end (§7) and in the
> A/B spec ([`ab-testing-engine-spec.md`](ab-testing-engine-spec.md)).
>
> **Sources:** Addy Osmani, *Loop Engineering* (addyosmani.com/blog/loop-engineering); Anthropic,
> *Getting Started With Loops* (claude.com/blog/getting-started-with-loops); Boris Cherny (Anthropic,
> head of Claude Code); Peter Steinberger.

---

## 1. The one-line shift
**Stop prompting the agent turn-by-turn. Design the *loop* that prompts the agent for you.**

- Old (prompt engineering): *you* hold the tool — write prompt, read reply, write next prompt.
- New (loop engineering): you build a **system** that finds work, distributes it, checks results, records
  what's done, and decides what's next — and *that system* prompts the agents.
- Boris Cherny (Anthropic): *"I don't prompt Claude anymore. I have loops running that prompt Claude and
  figure out what to do. My job is to write loops."*
- Osmani's definition of a loop: *"a recursive goal where you define a purpose and the AI iterates until
  complete."* And the mindset: *"Build the loop like someone who intends to stay the engineer, not just
  the person who presses go."*

**Loop design is *harder* than prompt engineering, not easier** — the leverage moved, the work didn't vanish.

---

## 2. The delegation ladder — Anthropic's four rungs (climb one at a time)
Each rung hands off more judgment and adds more risk. **Only climb when the current rung has earned trust.**
Not every task needs a high rung — start with the simplest thing that works.

| Rung | What triggers it | Who decides "done" | Use it for | Claude Code |
|---|---|---|---|---|
| **1. Turn-based** | your prompt | you verify each reply | one-off tasks with a clear exit | normal chat |
| **2. Goal-based** | your prompt + a *verifiable success condition* | a **separate evaluator** model checks the condition and sends it back to work until true | "keep going until the tests pass / N found" | `/goal` |
| **3. Time-based** | an external schedule/event | each run exits when its goal is met; the routine runs until you stop it | recurring work: triage, migrations, audits, **growth optimization** | `/schedule`, cron, GitHub Actions, Routines |
| **4. Proactive** | the loop finds & prioritizes its *own* work | fully autonomous; orchestrates agents/processes on events | mature, high-trust systems | scheduled + discovery skills + connectors |

**The rule:** each rung up removes a human checkpoint, so earn it. A rung-4 loop making mistakes unattended
is a rung-4 loop you can't walk away from.

---

## 3. The 5 + 1 primitives (the parts every loop is built from)
| Primitive | Its job in the loop | Claude Code mechanism |
|---|---|---|
| **Automations** (the heartbeat) | discovery + triage on a schedule, with no human prompting | `/loop` (re-run on cadence), `/goal` (run until true), cron, hooks, GitHub Actions |
| **Worktrees** (parallel without collision) | isolate parallel agents so two don't fight over the same file | `git worktree`, `--worktree`, `isolation: worktree` on subagents |
| **Skills** (intent written down) | codify project knowledge so the agent doesn't re-derive it cold every run | `SKILL.md` folders (instructions + scripts + refs), invoked by `$name` or implicitly by description |
| **Plugins / Connectors** (real tools) | let the loop *act* in your world — open the PR, update the ticket, ping the channel — not just report | MCP servers + integrations (GitHub, Linear, Slack, DBs, APIs) |
| **Sub-agents** (maker ≠ checker) | split ideation from verification so the writer doesn't grade its own homework | agents in `.claude/agents/` with distinct instructions (and often a stronger model for the verifier) |
| **State / Memory** (the spine) | track what's done + what's next **on disk**, outside any conversation | markdown / JSONL / a board — *"the agent forgets, the repo doesn't."* |

**The compounding insight:** *"Without skills the loop re-derives your whole project from zero every cycle;
with skills it compounds."* Same for state — it's what lets a loop *resume* instead of restart.

---

## 4. Anatomy of a complete loop (Osmani's worked example)
1. **Automation** fires every morning on the repo.
2. **Discovery skill** reads yesterday's CI failures / open issues / recent commits.
3. **Documents** findings to a state file (markdown / board).
4. For each actionable finding, opens an **isolated worktree**.
5. A **drafting sub-agent** writes the fix.
6. A **verifier sub-agent** reviews the draft against the project's skills + tests.
7. **Connectors** open the PR + update the ticket.
8. **Fallback**: anything it can't handle lands in a human triage inbox.
9. **State update**: what was tried, what passed, what's still open.
10. **Next run** resumes from that state. — *"You designed it once. You prompted none of those steps."*

---

## 5. Guardrails — the do's and don'ts (this is where loops live or die)
**Do**
- **Separate the verifier from the implementer.** Different instructions, ideally a different/stronger model.
  *"Since the loop runs while you are not watching, a verifier you actually trust is the only reason you can
  walk away."*
- **Keep state on disk**, never only in context.
- **Write tight, boring skill descriptions** so implicit invocation actually triggers.
- **Close the loop with connectors** — a loop that only edits the filesystem is a memo; one with connectors ships.
- **Design loops to deepen understanding**, not avoid it. Read what the loop makes.

**Don't**
- **Don't ship unattended without verification.** *"A loop running unattended is also a loop making mistakes
  unattended."* Your job is to *ship code you confirmed works.*
- **Don't accrue comprehension debt.** *"The faster the loop ships code you didn't write, the bigger the gap
  between what exists and what you actually get."*
- **Don't surrender cognition** — the temptation to stop having an opinion and take whatever it returns.
- **Don't ignore token cost.** Sub-agents burn more; spend a second opinion only where it's worth paying for.
- **Don't treat `/goal` as proof** — it's a *claim* of done-ness; the evaluator is more trustworthy than the
  implementer, but human confirmation still matters for anything that ships to users.

> The determining factor is never the loop — it's the engineer. *"Two people can build the exact same loop
> and get completely opposite results."* Loops amplify whatever intent you bring.

---

## 6. THE PORTABLE FRAMEWORK — set up a loop on any repo (the reusable recipe)
Drop this onto any project. Fill the 6 blanks; climb the ladder one rung at a time.

**Step 0 — Name the job & its exit.** One sentence: *"Every <cadence>, this loop should <goal>, and it's
done when <verifiable condition>."* No verifiable condition → you're not ready for rung 2+.

**Step 1 — State (the spine).** Create a `state/` (JSONL or markdown) that records: what ran, what it found,
what it did, what's open. Everything else reads/writes here. Rule: *nothing important lives only in context.*

**Step 2 — Skills (intent).** Write `SKILL.md`(s) for the recurring judgment: the conventions, the "how we
do X here," the past incidents, the definition of a good change. This is what stops the loop guessing.

**Step 3 — Sensors + a deterministic core.** What does the loop MEASURE each run (metrics, logs, tests,
tickets)? Keep measurement + any correctness math deterministic; the model *speaks* results, it doesn't
*derive* them.

**Step 4 — Maker/checker sub-agents.** One proposes, one verifies against the skills + a validation gate
(does it build / parse / pass tests / stay in scope?). Reject on any failure. Never let the maker self-grade.

**Step 5 — Connectors + a gate.** Wire the loop to act (git commit/PR, ticket, email/Slack). Put a **human or
evaluator gate** in front of anything irreversible or user-facing. Reversible-by-design (one `git revert`).

**Step 6 — Automation (the heartbeat).** Schedule it (GitHub Actions cron / `/schedule` / Routine) so it runs
in the cloud, not on your machine. Add a **failure alert** so silence means success. Start at rung 3.

**Step 7 — Earn the next rung.** Once it's trustworthy at rung 3 (time-based, human-gated), let it discover
and prioritize its own work (rung 4). Add a **completeness critic** ("what did I miss?") and A/B verification
of its own changes (see the A/B spec).

**The portable checklist**

- [ ] One-sentence goal **with a verifiable done-condition**
- [ ] State on disk (resume, not restart)
- [ ] Skills capturing the recurring judgment
- [ ] Deterministic measurement / correctness core
- [ ] Maker ≠ checker (separate verifier + validation gate)
- [ ] Connectors to act + a gate on irreversible/user-facing steps
- [ ] Cloud schedule + failure alert
- [ ] Reversible changes (one revert away) + audit log
- [ ] Token-cost cap + kill switch
- [ ] A human who still reads what it ships (no comprehension debt)

---

## 7. Applied to this repo (AZ Restaurant Partners)
**The growth engine is already a loop — at rungs 3→4.** Mapping it to the framework:

| Primitive | In `growth_engine/` today |
|---|---|
| Automation | GitHub Actions cron — `az-growth-propose` (daily) + `az-growth-inbox` (every 15m) |
| State | `growth_engine/state/*.jsonl` (signals, findings, batches, decisions, **executed** fingerprints) |
| Skills (intent) | the deterministic `sensors/` rules + `checks/site.py` invariants + `executors.py` edit templates |
| Sensors + deterministic core | `sensors/ga4_traffic.py` (GA4 → findings; math is deterministic) |
| Maker / checker | maker = deterministic executors + the **Claude** reply-actioner; checker = `validate_edit` (HTML/JSON-LD/`node --check`) + scope fence |
| Connectors + gate | git-commit-to-`main` → Pages deploy; **gate = the owner's email approval**; failure alert wired |
| Reversible + audit | one commit per change (revert-able); full JSONL audit; kill switch `ENGINE_DISABLED=1` |

**What's missing to make it "extremely smart" (the next rung):** it currently proposes → ships → *hopes*.
It doesn't yet **prove** a change worked. The upgrade is to close the measurement loop with **A/B testing**:
ship each change as an experiment, measure the lead-rate lift per variant, and **keep winners / revert
losers automatically** — a self-improving optimization loop. That is the `/goal`-style verifiable
done-condition applied to marketing, and it's spec'd in
[`ab-testing-engine-spec.md`](ab-testing-engine-spec.md).

**Portability note:** everything above is repo-agnostic. To run this loop on another client's site, swap the
GA4 property, the site paths, the owner allowlist, and the skills — the machinery is the framework.
