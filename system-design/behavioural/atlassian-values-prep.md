## Atlassian Values Interview Prep — STAR Stories

This guide maps your experiences (Rippling, Toku) to Atlassian’s values. Each section contains 2–3 STAR stories. Tailor Results with concrete metrics when available.

Format of each story:

- Situation: context and problem
- Task: what you owned or had to achieve
- Actions: concrete steps you took
- Results: measurable outcomes, impact, or lessons

---

## Play, as a team

1. STAR — Cross-team approvals integrations (enablement first)

- Situation: Multiple product teams (PTO, Spend, Payroll, HRIS) needed to integrate with the new Approvals Framework; timelines varied and confusion on contracts caused delays.
- Task: Help teams ship on time and reduce handoffs/friction.
- Actions: Ran integration office hours; authored playbooks and examples; produced SDK snippets and reusable UI; created a shared Slack channel for decisions; tracked integration burn-down.
- Results: Faster time-to-integrate; fewer escalations; consistent UX across products.

2. STAR — Delegation Framework collaboration with PTO and Approvals

- Situation: PTO events had to trigger delegation actions while Approvals consumed downstream updates; schema and timing differences created friction.
- Task: Align teams on event contracts and rollout.
- Actions: Authored HLD; co-created versioned event schemas; set up contract tests; staged deployments; shared runbooks.
- Results: Predictable integration, zero breaking changes; smoother collaboration through common artifacts.

3. STAR — Notification platform standardization

- Situation: Notification content/style diverged across teams, impeding maintainability.
- Task: Align on a unified approach without blocking teams.
- Actions: Built plug-and-play UI components; JSON-based configuration; migration path with lint rules; demos to showcase benefits.
- Results: Converged notification UX; faster rollout of new features like batching.

### Sample Q&A (Play, as a team)

- Describe a situation in which you had to arrive at a compromise with someone to move a project forward.

  - Answer 1 (Delegation): Staff preferred a stateless forwarder; I proposed a queryable state. We co-authored an ADR and agreed on a minimally stateful core with clear ownership and metrics. Result: consumers stayed lean; ops risk contained.
  - Answer 2 (Events): PTO needed late schema changes while consumers wanted stability. We dual-emitted v1/v2 with a deprecation window and adapters. Result: zero breakages, both teams unblocked.

- Tell me about a time you were working on a project where your co-collaborators were holding back the process.

  - Answer 1 (Integrations): Partner teams stalled on Approvals integration details. I ran office hours, shipped SDK snippets and checklists. Result: integrations shipped on time with fewer escalations.
  - Answer 2 (Handoffs): We had repeated misses at PR handoffs. I paired to create a PR template and examples. Result: faster reviews, fewer back-and-forths.

- How do you work with other people?

  - Answer 1: Create shared channels, ADRs, and decision logs; prefer demos; make assumptions explicit; confirm owners and timelines.
  - Answer 2: Raise risks early (risk register), use milestone trackers, and keep transparent status so surprises don’t accrue.

- How have you helped make a team/individual more successful if they weren’t performing well?

  - Answer 1: Introduced runbooks and actionable alerts for stuck requests. Result: reduced toil, clearer ownership, better outcomes.
  - Answer 2: Coached a teammate via checklists and sample implementations. Result: improved throughput and quality.

- Have you ever had to put the team’s goals above personal ambitions?
  - Answer 1: Prioritized integration office hours and enablement over owning new features to unblock other teams.
  - Answer 2: Invested a sprint in centralized telemetry and dashboards instead of feature work to level-up incident response.

---

## Build with heart and balance

1. STAR — Bulk Action latency vs consistency (short-term vs long-term)

- Situation: Bulk APIs were slow due to sync hooks; users felt it.
- Task: Improve UX promptly without compromising long-term integrity.
- Actions: Short-term optimistic updates to materialized views; guardrails (idempotency, reconciliation jobs, audits); long-term move to async hook execution.
- Results: Immediate UX gain; safe transition to robust async architecture.

2. STAR — Read vs write latency (materialized views)

- Situation: Dashboards were slow; moving computation to writes risked higher write latency.
- Task: Balance read SLOs and write budgets.
- Actions: Set write p95/p99 budgets; optimized view generation; staged rollout with A/B; tuned indexes; observed deltas.
- Results: 50–60% faster reads while keeping writes within budget; shared pattern reused.

3. STAR — Change capture: control vs speed

- Situation: Needed auditing; in-house added latency and maintenance risk.
- Task: Balance platform control with time-to-value.
- Actions: Built PoC; evaluated CDC vendor; presented tradeoffs and exit plan; selected vendor for minimal disruption.
- Results: Faster adoption; zero latency on hot paths; team focused on core product work.

### Sample Q&A (Build with heart and balance)

- Tell me about a time that you had to balance competing business, team, or project priorities.

  - Answer 1 (Reads vs writes): Materialized views improved reads but risked write latency. We set write budgets, optimized generation, and staged rollout. Result: 50–60% faster reads, writes within budget.
  - Answer 2 (Roadmap vs user pain): CS pushed for batched notifications; engineering favored evaluator work. We prioritized batching based on user impact. Result: reduced notification fatigue.

- Tell me about a time when you had to make a decision without all the information you needed.

  - Answer 1 (Async engine): Adopted a third-party executor with pilots and SLOs despite unknowns. Result: offloaded compute and enabled longer jobs with low risk.
  - Answer 2 (CDC): Chose a vendor with an exit plan over in-house despite limited prod exposure. Result: faster delivery, minimal latency on hot paths.
  - Answer 3 (Rippling — Approvals Preview caching): Implemented Redis-backed preview cache without prior hit-rate data; used signature-based keys, conservative TTLs, submit-time busting, and metrics/alerts to validate. Result: high hit rates, reduced CPU, faster UX, no material correctness issues.
  - Answer 4 (Rippling — Bulk Actions optimistic updates): With unknown downstream hook failure rates at peak, opted for optimistic materialized-view updates plus idempotency, reconciliation jobs, and audit trails; planned deprecation post-async hooks. Result: immediate latency relief with controlled risk; later migrated fully to async hooks.

- How do you think about prioritisation and decision making?

  - Answer 1: Use impact × confidence ÷ effort, anchored by SLOs; timebox experiments; document tradeoffs in ADRs.
  - Answer 2: Risk-first sequencing with staged rollouts and feature flags; pick options reversible at low cost.

- What are examples when you or the team have missed the mark? How did you react? How did you approach fixing things?
  - Answer 1: Vendor integration slipped due to unexpected API constraints. We communicated early, cut to MVP, added interim workaround, and hit the revised date.
  - Answer 2: Early alert rules were noisy. We tuned thresholds/tags, added error-budget burn alerts, and improved signal quality.
  - Answer 3 (Rippling — Batched notifications defaults): Our initial batching cadence delayed a few critical approver alerts. We added critical-channel exemptions, per-team configs, and guardrails for urgent events. Post-fix, critical notifications arrived on time while non-urgent noise stayed low.
  - Answer 4 (Rippling — Materialized view write spikes): First rollout caused p99 write spikes during peak loads. We introduced micro-batching, async recompute for heavy paths, and write SLO budgets with feature flags. Writes stabilized while dashboard reads kept their gains.
  - Answer 5 (Rippling — Integration docs too generic): Early Approvals docs lacked concrete examples, causing repeated partner questions. We added code snippets, checklists, versioned contracts, and office hours. Integration time dropped and escalations reduced.

---

## Open company, no bullshit

1. STAR — Transparent risk surfacing (async engine migration)

- Situation: Migrating background jobs had unknown risks (idempotency, retries, timeouts).
- Task: Surface risks early and create shared visibility.
- Actions: Created risk register; piloted low-risk jobs; shared dashboards for queue times/failures; weekly updates on progress and blockers.
- Results: No high-severity incidents; steady migration with trust across stakeholders.

2. STAR — Event versioning candid discussions

- Situation: Late schema changes from PTO risked breaking consumers.
- Task: Communicate impact clearly and reach a pragmatic solution.
- Actions: Explained blast radius; proposed versioned events and adapters; agreed on deprecation windows; documented policy.
- Results: Zero breakages; reusable policy for future.

3. STAR — Post-incident clarity and runbooks

- Situation: Stuck requests created firefighting and tribal fixes.
- Task: Replace ad-hoc scripts with clear, shared practices.
- Actions: Built recovery jobs; added actionable alerts; authored runbooks with decision trees; measured MTTR.
- Results: Reduced manual interventions; faster, repeatable recoveries; common understanding across teams.

### Sample Q&A (Open company, no bullshit)

- Tell me about a time your first impression of a person or situation was incorrect.

  - Answer 1: Initially blamed DB for latency; profiling revealed N+1 in sync hooks. We moved to async processing. Result: reliability and latency improved.
  - Answer 2: Assumed teams wouldn’t adopt standardized logging; after feedback sessions and starter kits, adoption increased. Result: better incident telemetry.

- Tell me about a time you had a different point of view about how to solve a problem with someone on your team.

  - Answer 1: Stateless vs stateful delegation. We compared failure modes, consumer complexity, and ops cost; agreed on minimally stateful core.
  - Answer 2: Sync vs async hooks. Prototyped, shared data, phased migration. Result: team alignment and better UX.

- What's your approach when having difficult conversations?

  - Answer 1: Start with shared goals and facts; quantify impact; propose options with pros/cons (e.g., event schema changes).
  - Answer 2: Focus on user outcomes and risk; agree on decision owners and timelines; follow up with written summaries.

- How have you resolved conflict in the past?

  - Answer 1: Event versioning with dual emission and deprecation windows avoided breakages and unblocked both teams.
  - Answer 2: Reads vs writes conflict resolved via SLOs, budgets, and flags to validate safety.
  - Answer 3 (Rippling — Manager vs engineers on ops vs features): Roadmap pressure deprioritized ops work while engineers flagged on-call toil. I facilitated a session to quantify toil, carved out a two-week ops timebox with clear success metrics, and aligned on a split plan (week 1: highest-impact recovery jobs; week 2: alerts cleanup). Result: reduced incidents and regained feature velocity with shared buy-in.
  - Answer 4 (Rippling — Teammate handoff gaps): A teammate repeatedly missed integration handoff details, creating friction. I addressed it 1:1 with empathy, co-created a checklist/PR template, paired on the next two deliveries, and set explicit expectations. Result: smooth handoffs and restored trust across teams.
  - Answer 5 (Rippling — Cross-team on-call boundaries): Disagreements on who owns stuck-approval incidents led to finger-pointing. I convened leads to define a RACI, authored runbooks with triage steps, and set a warm-handoff protocol. Result: faster resolution and fewer escalations.

- Have you adapted your communication style to achieve a better outcome in a potentially negative situation?
  - Answer 1: With Customer Success, removed jargon and used before/after dashboards to align on batching defaults.
  - Answer 2: With leadership, used concise metrics and tradeoff tables to drive decisions quickly.
  - Answer 3 (Rippling — teammate code reviews): Switched from dense, nitpicky PR comments to a collaborative, live review with examples and pair-refactors. Result: fewer review cycles, higher confidence, and improved code quality.
  - Answer 4 (Rippling — stakeholder upset about delays): Moved from technical justifications to empathetic, solution-focused updates (impact first, options with tradeoffs, revised dates). Result: regained trust and agreement on a scoped MVP path.
  - Answer 5 (Rippling — cross-team post-incident): Shifted from defensive posture to a blameless, facilitative tone; focused on facts, timelines, and action items. Result: quicker consensus on fixes and stronger willingness to adopt runbooks/alerts.

---

## Be the change you seek

1. STAR — Telemetry standardization initiative

- Situation: Inconsistent logging/metrics hindered detection and debugging.
- Task: Drive standardization without blocking teams.
- Actions: Delivered centralized controllers; opinionated tags; starter templates; CI linting; shared dashboards.
- Results: Faster diagnostics; broad adoption; higher operational readiness.

2. STAR — Alerts, SLOs, and runbooks

- Situation: Noisy/missing alerts and unclear ownership slowed resolution.
- Task: Establish SLOs and actionable alerting tied to ownership.
- Actions: Defined latency/error SLOs; created alert policies; automated retries and JIRA creation; wrote runbooks.
- Results: Lower MTTR; proactive ops; clearer accountability.

3. STAR — Approvals Preview caching

- Situation: Approver computation was CPU-heavy; duplicate work between preview and submit.
- Task: Reduce compute and create a better UX.
- Actions: Added Redis cache keyed by request signature; built a generic preview endpoint; documented usage.
- Results: Lower CPU; faster flows; easy adoption by multiple teams.

### Sample Q&A (Be the change you seek)

- Share an example of a time when you were able to turn around the performance of an individual or team.

  - Answer 1: Introduced PR templates and checklists; paired reviews. Result: fewer review cycles and quicker merges.
  - Answer 2: Standardized telemetry and runbooks. Result: shorter MTTR and less on-call fatigue.

- Tell me about a time that you supported your team / a teammate to manage a major change.

  - Answer 1: Async engine migration—wrote runbooks, training, and fallback plans. Result: zero high-severity incidents.
  - Answer 2: Shift to materialized views—migration guides, feature flags, and metrics. Result: safe rollout and measurable wins.

- When have you advocated to push for change? What did you learn from this process? What was the outcome?
  - Answer 1: Telemetry standardization; learned co-creation beats mandate. Result: broad adoption and better ops.
  - Answer 2: Batched notifications; learned to prioritize user signal over team preference. Result: fewer complaints and higher engagement.

---

## Don’t #@!% the customer

1. STAR — Batched notifications to reduce spam

- Situation: Approvers were overwhelmed by frequent notifications.
- Task: Protect user attention while preserving information.
- Actions: Built batching with configurable cadence; summary payloads; coordinated with CS to tune defaults.
- Results: Noticeable drop in notifications/user; improved satisfaction; fewer support tickets.

2. STAR — Approvals Dashboard performance

- Situation: Slow dashboards reduced trust and daily efficiency.
- Task: Restore responsiveness at scale.
- Actions: Materialized views; read-optimized API; instrumentation and SLOs.
- Results: 50–60% latency improvement; stable performance under growth.

3. STAR — Reliable hooks via async processing

- Situation: Sync hooks delayed users and timed out under load.
- Task: Make hook execution reliable and non-blocking.
- Actions: Event-driven workers; idempotent handlers; dead-letter queues; observability.
- Results: Higher reliability; reduced timeouts; better UX.

### Sample Q&A (Don’t #@!% the customer)

- Tell me about a time when you had to make a tradeoff that involved potentially causing pain for a user or customer.

  - Answer 1: Optimistic updates introduced eventual consistency to cut latency. We added reconciliation and audits. Result: snappy UX with mitigated risk.
  - Answer 2: Accepted modest write latency to enable fast reads via materialized views, guarded by write budgets.

- Tell me about a time when you advocated for the customer, despite opposition.

  - Answer 1: Prioritized batched notifications despite roadmap pressure. Result: reduced spam and higher satisfaction.
  - Answer 2: Pushed for dashboard performance work; instrumented SLOs to prove impact.

- How is your mentality ‘user-centred’? How have you put the customer first? What trade-off(s) did you make to do this?
  - Answer 1: Optimize for perceived latency and reliability (async hooks, read models), accepting extra infra work and monitoring.
  - Answer 2: Approvals Preview caching reduced compute and wait time, trading cache complexity for a faster user journey.

---

## Extra sample questions (STAR)

1. Biggest challenge you faced so far in your career?

- STAR: Building a reusable Approvals Framework across many products under ambiguity—drove PRDs, extensible design, strong observability; outcome: broad adoption and stable operations.

2. Did you ever put your team ahead of your personal goals?

- STAR: Ran integration office hours and wrote playbooks/SDKs, prioritizing enablement over owning new features to unblock partner teams.

3. Did you face any issues with any teammate’s performance—how did you resolve it?

- STAR: Noticed repeated handoff gaps during integrations; paired to co-create a checklist and examples; added PR templates; outcome: fewer misses and faster reviews.

4. Did you ever commit something and fail to deliver on time?

- STAR: Vendor integration slipped due to unforeseen API constraints; communicated early, cut scope to MVP, added interim workaround; delivered revised timeline and hit it.

5. Did you drive any change in the team which ultimately got rejected?

- STAR: Proposed a heavier stateful read model initially; after ADR review and benchmarks, adopted a leaner alternative; documented lessons and kept a path to evolve if needed.

---

## Notes to tailor

- Add concrete metrics where possible (latency p95/p99, % alert noise reduction, # of teams onboarded).
- Prepare 60–90 second versions focusing on Results and 1–2 key Actions.
