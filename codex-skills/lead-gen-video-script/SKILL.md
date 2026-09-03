---
name: lead-gen-video-script
description: Diagnose, structure, write, and evaluate Chinese lead-generation short-video scripts for consultants, educators, professional-service providers, and other high-ticket businesses. Use when the user asks for 获客型短视频、精准客户内容、高客单成交内容、客户痛点诊断、说服逻辑设计、获客脚本审核，或希望通过短视频筛选客户、建立专业信任并承接咨询转化。Do not use for general AI tutorials, entertainment scripts, pure traffic-oriented viral content, or ordinary product explainers.
---

# Lead-generation Video Script

Build the persuasion logic before writing copy. Optimize for qualified prospects, trust, and a natural next step rather than maximum views.

## Choose a mode

- **Create**: Build a script from business information or an idea.
- **Diagnose**: Find conversion breaks in an existing script before rewriting it.
- **Evaluate**: Score a finished script and propose targeted repairs.
- **Hooks**: Generate openings only after the audience, situation, and core claim are clear.

Use deep mode by default. Use fast mode only when the input already supplies a clear audience, concrete situation, diagnosis, solution, proof, and desired action.

## Run the workflow

### 1. Establish the business context

Determine:

- offer and approximate price or decision complexity;
- target customer, current task, and business stage;
- concrete situation in which the problem occurs;
- visible pain, consequence, and cost of inaction;
- customer's current explanation or attempted solution;
- creator's diagnosis of the root cause;
- solution and why it addresses that cause;
- real experience, process details, cases, or data;
- desired next action.

Do not ask for everything at once. Ask 1-3 questions per round, prioritizing the missing information that would most change the argument. Stop asking when remaining gaps can safely be labeled as assumptions rather than invented as facts.

Read [references/logic-framework.md](references/logic-framework.md) when judging information quality or constructing the argument.

### 2. Gate on information quality

Do not draft the final script when any critical item is too vague:

- audience is only a broad identity label;
- pain lacks an observable situation;
- diagnosis merely repeats the symptom;
- solution does not correspond to the diagnosis;
- proof is a slogan or unsupported claim;
- CTA is unknown and materially changes the script.

State the biggest gap and ask a concrete question. Never fabricate revenue, clients, outcomes, quotes, credentials, or personal experience.

### 3. Build the strategy card

Before drafting, present:

```markdown
目标客户：
触发场景：
表层问题与代价：
用户原有判断：
真正根因：
核心主张：
解决机制：
可信证据：
适用边界：
下一步行动：
```

Mark consequential inferences as `待确认假设`. If the user requested direct output and information is sufficient, continue without pausing; otherwise ask them to confirm disputed logic before drafting.

### 4. Construct the persuasion chain

Use these as logic checks, not mandatory paragraph headings:

1. audience trigger;
2. concrete pain situation;
3. meaningful consequence;
4. root-cause diagnosis;
5. one core claim;
6. solution mechanism;
7. credible evidence;
8. boundary or key objection;
9. action that continues the activated need.

Merge, reorder, or omit an explicitly implied item when natural. Keep every included section in service of the single core claim.

### 5. Draft in the creator's voice

Preserve the user's facts, terminology, stance, and speaking style. Prefer spoken Chinese, short sentences, concrete verbs, and causal transitions. Do not add generic hype, empty urgency, fake contrarianism, or traffic bait that attracts the wrong audience.

When length is unspecified, produce one concise strategy card followed by one polished continuous口播稿. Do not add shot lists, titles, or multiple variants unless asked.

### 6. Audit before delivering

Read [references/evaluation-rubric.md](references/evaluation-rubric.md). Repair material weaknesses silently before delivery. In Diagnose or Evaluate mode, show the score, biggest conversion break, and prioritized repairs before any rewritten version.

## Output rules by mode

### Create

Return the strategy card and final script. If blocked by critical information, ask only the highest-value questions instead.

### Diagnose

Return:

1. current persuasion chain;
2. biggest conversion break;
3. missing or unsupported information;
4. prioritized repair plan;
5. rewritten version only if requested.

Do not mistake grammar polishing for acquisition improvement.

### Evaluate

Return the weighted score, concise evidence for each weak dimension, and the smallest changes that improve conversion without replacing the creator's point of view.

### Hooks

Vary the trigger—situation, costly consequence, diagnostic contradiction, or result—while keeping the same qualified audience and core claim. Do not use unrelated curiosity gaps.

## Guardrails

- Treat high views as neither the default goal nor proof of acquisition quality.
- Separate identity labels from active buying situations.
- Explain the cause before prescribing the solution.
- Pair steps with mechanisms: say why each action works.
- Use evidence that proves the claim, not decorative achievements.
- State genuine limitations when they improve fit and trust.
- Make the CTA the next step of the same problem, not a generic request to follow.
- Let AI organize and test logic; never let it invent the creator's distinctive experience.

Read [references/examples.md](references/examples.md) only when examples are needed to resolve ambiguity or demonstrate a diagnosis.
