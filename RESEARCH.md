# Research dossier: an evidence-based Berlin election navigator

**Research date:** 4 August 2026  
**Election in scope:** Election to the 20th Berlin House of Representatives (*Abgeordnetenhaus*) and the district assemblies (*BVV*) on 20 September 2026.  
**Purpose:** Decide how an application can help Berlin residents make an informed, independent, preference-consistent choice without telling them whom to vote for.

## Recommendation

Build a **source-first election navigator**, not a black-box “vote correctly” recommender.

The public-facing promise should be: *“Understand who is on your ballot, compare documented positions, and explore which options fit the issues you care about.”* In research, “correct voting” has a narrow meaning related to an informed choice consistent with a voter’s own preferences; it must not mean that the product knows the objectively right candidate or party for a person. [18]

The recommended 2026 product has three clearly separate layers:

| Layer | What it gives a resident | What it must not do |
| --- | --- | --- |
| **1. Candidate and ballot explorer** | Every officially admitted candidate relevant to the resident’s constituency; candidacy type, list position where public, source-linked profile, and a correction route. | Infer a candidate’s personal views from their party or score a non-respondent. |
| **2. Issue comparison** | A readable matrix of party and, where available, candidate positions, rationales, and primary sources. | Mix state and BVV responsibilities, or present campaign claims as verified facts. |
| **3. Alignment test** | A transparent, adjustable comparison between a resident’s issue preferences and participating actors’ stated positions. | Call its output a recommendation, hide the formula, or merge party/list and direct-candidate choices into one ranking. |

This is both more useful and more defensible than a simple political compass. It also creates a distinctive role: the Bundeszentrale für politische Bildung (bpb) says its Berlin **Wahl-O-Mat** will publish on 24 August 2026. [17] Rather than duplicate its party-oriented tool, this application should complement it with a complete, auditable candidate and constituency experience.

## Time-sensitive Berlin context

- The Berlin Senate set **20 September 2026** for the elections to the 20th *Abgeordnetenhaus* and the BVVs. The official election authority reports **78 Berlin constituencies**. [1]
- The state election committee admitted 12 state lists on 24 July 2026. Together with SPD, CDU, and Die Linke with citywide district lists, plus HEIMAT and B* in individual districts, the authority reports **17 parties** competing for second votes. [2]
- The election consists of two distinct ballot logics: 78 direct mandates are elected in constituencies with the **first vote**; remaining seats are filled from lists using the **second vote**. [13] Candidate, list, and constituency information are therefore not interchangeable. A person can be a direct candidate, a list candidate, or both.
- The simultaneous BVV election is a different decision again: it uses one vote, 55 seats per borough, and a 3% threshold. [13] Do not mix its issues, candidates, or results into the *Abgeordnetenhaus* alignment score.
- The official election authority is the primary source for the election register. It states that district committees decided constituency and district-list admissions on 22 July and the state committee decided state-list admissions on 24 July. [3] Store every imported source URL, publication date, retrieval timestamp, and a version identifier.
- Admissions do **not** yet make a complete named registry public. The authority’s official timetable sets **30 August 2026** (21 days before the election) as the deadline for publication of admitted nominations under §34 LWO. [14] As of this research date, do not present any candidate roster as final or official until that publication is available.

### Product implication

The first user decision is not simply “which candidate fits me?” It is more accurately:

1. Which **state-level issues** matter to me?
2. Which **party/list options** best align with those priorities?
3. Who is actually standing in **my constituency** and what do they personally say or have done?
4. If BVV coverage is added, which issues belong to the borough rather than the state?

Keep those answers on separate screens and label the relevant ballot context in plain language.

## What the research says

### 1. A voting-advice application can help, but its design can change the result

The strongest research finding is cautionary: statement selection and the matching rule are substantive editorial choices, not neutral plumbing.

- Walgrave, Nuytemans, and Pepermans simulated 500,000 combinations of statements and found that different selections can give users divergent information. [4]
- Louwerse and Rosema tested alternative defensible spatial/matching models using real VAA answers. A majority of users would have received different advice under another model. [5]
- Gemenis identifies the major quality risks: statement wording, response scales, reliability of coding positions, and the validity of treating items as a political dimension. [6]
- A Belgian panel study found that a popular VAA affected some final choices, but effects were modest and did not appear to strongly alter the overall outcome. [7]
- A meta-analysis across 22 studies finds positive reported associations with turnout and vote choice, but weaker effects in more rigorous experimental studies. Treat the application as politically consequential and do not infer causal impact from self-selected app users. [19]
- Statement selection can systematically change matches: an experiment found that more left–right statements increased ideological matching and benefited more extreme parties. [20] Question polarity also changed answers in a 31,112-user VAA field experiment, especially for less politically sophisticated users. [21]

**Design consequence:** never hide a single “best match” behind an unexplained percentage. Show the underlying agreements and disagreements, let people change issue importance, and label close or method-sensitive results as such.

### 2. The established German precedent is transparent and participatory

The bpb’s Wahl-O-Mat provides a useful benchmark, not a dataset to copy. Its public method uses an editorial process with young voters, asks parties to answer the final statements directly, allows weighting, and exposes explanations and party comparisons. [8] Its own research reports user-survey indications that users value learning party differences and often seek further information, while those results should not be mistaken for a representative causal estimate. [9] The bpb’s released datasets explicitly prohibit using them to create a similar party-proximity calculation; build an independent statement set and response dataset, or obtain permission. [15]

**Design consequence:** adopt the good parts—equal opportunity to answer, published rationales, adjustable weights, and a comparison view—then improve the audit trail for candidate information.

### 3. Neutrality means enabling judgement, not pretending there are no choices

The Beutelsbacher Consensus is a strong ethical design reference for civic education: no overwhelming/indoctrination, controversies must remain visible, and people should be able to analyse their own interests. [10] It is a pedagogical standard rather than a blanket legal rule for a private app, but it maps directly to good product practice.

**Design consequence:** do not suppress controversial options, frame issues symmetrically, distinguish fact from stated opinion, and make the resident—not the algorithm—the final decision-maker.

## Methods considered

| Method | Value | Main risk | Decision |
| --- | --- | --- | --- |
| Official candidate directory | High transparency; indispensable baseline. | Can overwhelm users without comparison tools. | **Required.** |
| Party alignment test | Helps people structure issue preferences; feasible if all admitted parties receive equal treatment. | Statement and formula choices can alter rankings. | **Use with full methodology and sensitivity checks.** |
| Candidate alignment test | Local and personally relevant. | Uneven response rates, candidate/party conflation, and a large data-collection burden. | **Optional and conditional:** only score candidates with comparable, disclosed response coverage. |
| Issue explorer / side-by-side matrix | Encourages deliberation and source checking. | Takes editorial effort to explain well. | **Required.** |
| Generic “left–right” political compass | Fast to build. | Does not map reliably to this ballot or to concrete Berlin policies. | **Do not use as the main product.** |
| LLM-generated biographies or voting advice | Can summarise internally with human review. | Hallucinated claims, unequal treatment, untraceable recommendations. | **Do not use in public-facing factual profiles or matching.** |

## Scientific product protocol

### A. Define the outcome before designing the quiz

Pre-register the aims in a public methodology page before collecting answers:

1. Improve accurate knowledge of options and issue differences.
2. Help users articulate priorities and find the evidence behind positions.
3. Preserve independent choice; do **not** optimize for moving votes or predicting a vote.
4. Deliver comparable information fairly across parties, candidates, constituencies, languages, and access needs.

Measure these outcomes rather than claiming that the tool makes people “vote correctly.”

### B. Build the statement set in an auditable way

1. Create a long list from Berlin-level competencies, official election material, party manifestos, documented resident concerns, and a structured consultation with diverse Berlin residents and independent subject experts.
2. Classify every proposed statement by policy domain and level of government: state, BVV, federal/EU, or out of scope.
3. Use published selection criteria before reading responses: **salience, controversy/discriminatory value, jurisdictional relevance, clarity, and breadth**. The bpb uses similar public criteria for its Wahl-O-Mat process. [8]
4. Red-team each item for double-barrelled wording, hidden factual premises, loaded language, false trade-offs, unequal consequences for groups, and positive/negative wording asymmetry. Avoid negation wherever possible. [21]
5. Run cognitive interviews with residents from different age groups, districts, German proficiency levels, education levels, and disability/access needs. Ask participants to explain the item in their own words; revise or drop misunderstood items.
6. Publish the final statement wording, definitions, domain, selection rationale, and version history.

Use a modest number of concrete statements. More items are not automatically more valid; every item needs a clear purpose and must be readable on a phone.

### C. Collect positions without pretending to read minds

For each admitted party and candidate, send the same questionnaire, deadline, response format, and correction process.

- Use a tested four-point agreement scale plus a separate `no answer / no position` option; do not silently turn missing data into a midpoint. Include an optional short rationale and source link.
- Ask a named authorised representative to sign off on a party response; record the respondent role and date, not their private contact details.
- For candidates, label answers as **candidate’s submitted position**, not as a fact-check of a promise.
- Treat publicly documented past actions separately: use primary parliamentary records or official documents, quote precisely, and perform a two-person source check.
- A non-response is **“not answered”**, never “neutral,” “unknown,” or an implied party position.
- Give every participant a defined review window and maintain a visible corrections log after launch.

Candidate pages should have data labels such as:

- `Official candidacy information` — source: election authority
- `Candidate’s answer` — source: submitted questionnaire, date
- `Documented past action` — source: named parliamentary/official record
- `Editorial explainer` — author, source, and last-reviewed date

### C.1 Candidate choice when the evidence is still incomplete

Do not turn a sparse collection of campaign pages into a pseudo-scientific
candidate test. The candidate helper should use a **decision journey**, with
three deliberately separate kinds of information:

| Stage | What the resident controls or sees | What the product may conclude |
| --- | --- | --- |
| **Ballot gate** | A Wahlkreis and its currently documented direct candidacies. | Who is relevant to the first vote, with a visible provisional/official status. |
| **Personal compass** | Up to two decisive and up to five important policy areas, plus an optional private question. | Only the order in which that resident reads evidence; never a candidate score. |
| **Comparable-answer matrix** | Answers to the same public question, same question-set version, and same response scale. | A transparent, question-by-question comparison—never an aggregate winner. |
| **Source context** | Candidate statements, official records, and publisher reporting with separate labels. | Context to inspect, not a conversion into a yes/no answer or a match value. |
| **Private decision trail** | The resident’s own “shortlist”, “check again”, notes, and a two-person source contrast. | Only that resident’s saved choices, held locally in the browser. |

The direct-comparison gate is strict. A response may appear as a comparable
questionnaire answer only when it has all of the following: a stable question
ID, questionnaire version, permitted answer value, candidate confirmation,
editorial approval, public publication status, and a source URL/locator.
Two people are directly compared only where both answered the same ID and
version. A campaign statement, social post, official action, or news report
can still be useful, but remains visibly non-comparable context.

This approach is intentionally non-compensatory: a source-count advantage on
one topic cannot hide an unanswered question or override a resident’s own
decisive concern. Missing source material is shown as a research gap, never as
agreement, disagreement, evasiveness, competence, or a negative mark.

### D. Use a simple, reproducible matching model

Choose one understandable default and publish it. A defensible default is a four-point agreement scale encoded from `0` (strongly disagree) to `3` (strongly agree), with `skip / no position` outside the scale. For each jointly answered item:

```text
distance_i = abs(user_position_i - actor_position_i) / 3
alignment = 1 - sum(weight_i × distance_i) / sum(weight_i)
```

Allow a resident to mark an issue important (for example, weight `2` rather than `1`), skip items, and edit answers. Show the exact items used in the denominator.

Guardrails are as important as the formula:

- Show **response coverage** beside every result, e.g. “24 of 28 comparable answers.”
- Do not calculate a candidate rank below a pre-published coverage threshold; show the profile and unanswered items instead.
- Display the raw issue matrix and rationales before or alongside an ordered result.
- Run a sensitivity analysis using at least two reasonable alternative metrics and leave-one-item-out checks. If top results change materially, say: “Several options are close; explore the issue differences.”
- Unit-test the scoring code against a published fixture; version the dataset and formula.
- Do not combine party/list and individual-candidate scores. A resident may compare them, but the product must explain that they answer different ballot questions.

### E. Establish reliability, validity, and fairness evidence

This is the core scientific work—not a post-launch marketing survey.

| Quality question | Test before or during launch |
| --- | --- |
| **Content validity** — do the items cover meaningful Berlin choices? | Independent political-science and policy review; documented resident consultation; jurisdiction tags. |
| **Comprehension validity** — do residents understand what they answer? | Think-aloud interviews and plain-language testing; revise failed items. |
| **Position validity** — are displayed positions traceable? | Party/candidate sign-off, primary-source links, two independent coders with recorded agreement for non-self-reported factual records, and a correction log. |
| **Algorithmic robustness** — does one arbitrary design choice drive the result? | Statement-selection audit, alternative-model sensitivity report, versioned score tests. |
| **Equity** — does the experience work comparably? | Accessibility test, low-bandwidth/mobile test, language review, and outcome analysis by voluntarily reported groups only if lawful and consented. |
| **Learning effect** — do users learn, rather than just feel certain? | Optional consented pre/post knowledge questions using factual position recall; compare an explanatory result view with a score-only view, not alternative political messages. Do not generalise self-selected visitor surveys to all Berlin voters. |

Do not use Cronbach’s alpha as the main quality claim: the issue set is intentionally multidimensional, not one psychological scale. Instead, report the tests above, response coverage, missingness, and scoring robustness.

### F. Put independence into the operating model

Before launch, publish an editorial charter containing:

- funding sources, owners, partners, and conflicts of interest;
- names/roles of the editorial, technical, accessibility, and scientific reviewers;
- a rule that editorial selection and scoring cannot be changed after seeing a politically convenient result;
- equal outreach and equal publication rules for every officially admitted actor;
- data sources, update cadence, a correction/appeal channel, decision times, and a public change log;
- a policy against political advertising, paid ranking, microtargeting, and dark patterns;
- an archive of each released data and methodology version.

An advisory group should include political-methods expertise, election-law/privacy review, accessibility expertise, and Berlin residents with varied lived experience. The group should audit the process, not choose political winners.

## Data strategy for all candidates

Treat the project as a data-provenance system first. Do not begin with scraped biographies.

### Canonical record model

| Entity | Minimum fields |
| --- | --- |
| `Election` | official name, date, scope, official source URL, retrieval date, version |
| `Candidate` | canonical ID, official name, only necessary public biographical fields, source citation |
| `Candidacy` | candidate ID, party/list, direct constituency and/or list type, list position if official, publication status (`provisional`, `admitted`, `officially published`), source/version |
| `Party` | official name, ballot/list type, official source, questionnaire contact/status |
| `Issue` | stable ID, wording, jurisdiction, domain, definitions, selection rationale, version |
| `Position` | actor ID, issue ID, response, rationale, source URL, source type, received/checked/published dates |
| `Correction` | claim/record ID, requester category, evidence, resolution, timestamp, visible change note |

### Source hierarchy

1. **Official election authority / official notices** for candidacy, constituency, list, and ballot facts.
2. **Direct, signed party or candidate responses** for current political positions.
3. **Official parliamentary documents and votes** for incumbents’ documented actions.
4. **Official party programme and campaign documents** for party commitments.
5. Reputable secondary reporting only as a labelled pointer, never as the sole proof of a contested profile claim.

Do not copy photos, biographies, or social-media claims without a rights and provenance check. Avoid collecting private contact data, family details, home addresses, or sensitive personal information that is irrelevant to the ballot.

Until the official nomination publication, the application may prepare the schema, official-source importer, candidate invitation workflow, and an explicitly provisional internal review queue. It should not market a complete final candidate directory or use unofficial campaign announcements as a substitute for the official register.

## Privacy, legal, and accessibility baseline

This is a research and product recommendation, not legal advice. Obtain a German election/media/privacy-law review before launch.

### Voter data

Quiz answers can reveal political opinions when connected to a person. GDPR Article 9 treats personal data revealing political opinions as a special category; Articles 5 and 25 require purpose limitation, data minimisation, and data protection by design/default. [11]

The safest default architecture is:

- no account, no server-side storage of quiz answers, and calculation in the browser;
- no third-party behavioural analytics or ad pixels;
- no sharing result URLs unless a person explicitly asks for it;
- optional research surveys separated from the quiz, with explicit consent, plain-language information, retention limits, and no linkage back to a score;
- a documented DPIA screening and, if needed, a full Data Protection Impact Assessment before any profiling, tracking, or broad research collection.

Check TDDDG §25 before adding cookies or other device storage/access that is not strictly necessary to provide the requested service. [16]

### Candidate data and publication

Use only necessary public election information, distinguish public-source facts from claims, preserve evidence, offer correction, and obtain a legal review for the publication basis, copyright/database rights, image rights, defamation risk, *Impressum*, and privacy notice.

### Accessibility and inclusion

Target **WCAG 2.2 AA** from the first prototype, regardless of the eventual legal classification of the service. [12] Test keyboard-only use, screen readers, zoom/reflow, contrast, mobile and slow connections, clear error recovery, and accessible charts/tables. Provide easy-language election explanations, use professionally reviewed translations where offered, and do not rely on colour or a percentage alone to communicate a result. Partner distribution through libraries, community organisations, and print-friendly views can reduce the digital-access gap.

## 2026 launch plan and quality gates

There are only weeks until the election. The launch plan must favour trust over feature count.

| Window | Deliverable | Quality gate |
| --- | --- | --- |
| 4–7 Aug | Publish charter; establish source ledger; prepare the official importer and candidate-review queue. | No candidate is presented as officially admitted before the official publication. |
| 4–21 Aug | Freeze statement-selection protocol; recruit review panel; conduct rapid cognitive and accessibility tests; send equal questionnaires. | No ambiguous or out-of-scope statement survives testing. |
| 12–29 Aug | Build the party/issue comparison, deterministic matching, sensitivity tests, and corrections workflow. | Raw comparisons, coverage, sources, and corrections workflow work end-to-end. |
| 30 Aug onward | Ingest the official published nominations; launch the reviewed candidate/constituency companion once roster verification is complete; continue documented corrections. | Never publish a rank whose coverage or robustness gate fails. |
| Before 20 Sep | Publish a dated final methodology/data snapshot, while leaving urgent factual corrections visible. | Users can see what changed, when, and why. |

### Non-negotiable no-go conditions

Launch the directory and comparison pages, but **withhold the matching/ranking feature**, if any of these is true:

- the official candidate roster cannot be verified;
- parties or candidates have materially unequal opportunities to respond;
- questionnaire wording has not passed comprehension review;
- sources, formula, or version history are not public;
- response coverage makes comparisons misleading;
- sensitivity testing shows an unstable apparent “winner” without an adequate explanation;
- a keyboard or screen-reader user cannot complete the core task;
- quiz responses leave the browser or are tracked without a lawful, transparent basis.

## What to build first

The first implementation should be the **provenance-aware candidate directory and issue comparison system**, not the quiz UI. It unlocks every later feature, makes the project immediately useful, and lets the matching tool consume reviewed data rather than unverified content.

Suggested first build sequence:

1. Data schema and source/version ledger.
2. Official candidate/list importer plus manual review queue, ready to run when nominations are officially published.
3. Candidate page with evidence labels, source links, and correction request flow.
4. Issue matrix with party/candidate response coverage.
5. Transparent alignment test only after the scientific and legal gates above are satisfied.

## Cognitive-psychology layer: how people actually choose and how to design around it

**Added:** 14 August 2026

The sections above address data integrity and algorithmic fairness. This section addresses the other half of the design problem: the systematic ways human psychology distorts political decision-making, and the UX interventions that counter them without overriding voter autonomy.

### The core failure modes

**Identity-protective cognition (Kahan, 2017).** People do not evaluate policies and then pick a party. They affiliate with a social group, absorb that group's positions, and then rationalize those positions. Showing a user "CDU position: X" before they have formed their own view activates tribal processing — they evaluate whether to accept their in-group's view, not whether X is good policy. This is the strongest single reason not to lead with party labels.

**Attribute substitution (Kahneman, 2011).** When asked "which party best represents my interests?" the brain substitutes an easier question: "which party do I feel good about?" Affect, familiarity, and candidate likeability drive choices that people sincerely believe are policy-based. Concrete policy trade-offs must precede affect-laden party comparisons.

**Hot cognition / motivated reasoning (Lodge & Taber, 2013).** Political information is processed emotionally first and rationally second. Counter-arguments to a favored party are scrutinized harder than supporting arguments. People can feel *more* certain after encountering mixed evidence. Structuring the journey so users see all positions before anchoring on one party directly counteracts this.

**Values upstream of issues (Schwartz, 2012; Haidt, 2012).** Stable personal values — security vs. openness to change, individual freedom vs. social solidarity, loyalty vs. universalism — predict party choice more reliably than any individual issue position. Issue positions are downstream of values. Measuring only issue positions captures symptoms rather than causes, and makes it easy for a user's result to shift arbitrarily based on which issues happened to be included.

**Negativity bias (Baumeister et al., 2001).** Negative information about a party carries approximately 2.5× the psychological weight of equivalent positive information. Party comparisons that include negatively framed items — or that surface scandals alongside policies — systematically disadvantage the affected party regardless of the user's genuine priorities. The symmetric framing rules in section B of the scientific product protocol are necessary, not cosmetic.

**Familiarity heuristic.** Users who have heard a party name many times rate it more positively on a first encounter than unfamiliar parties (Zajonc's mere exposure effect). Alphabetical display and equal visual treatment directly counteract this; so does withholding popularity signals.

**Candidate personality heuristics (Todorov et al., 2005).** Voters form competence judgments from candidate faces in under one second, and these judgments predict a meaningful share of election outcomes. Leading a candidate profile with a photograph before documented positions activates personality processing that is difficult to override with subsequent policy information.

### Proposed UX responses

#### Entry layer: values warm-up (~3 minutes)

Before any party or policy content, present eight scenario cards that are deliberately non-political and carry no party label. Each card poses one concrete everyday trade-off that maps onto a values dimension from Schwartz's Basic Human Values framework:

| Card topic | Values dimension tested |
| --- | --- |
| Park renovation: quick simple vs. slow participatory | Short-term efficiency vs. long-term inclusion |
| Neighborhood rule: individual exception vs. consistent enforcement | Individual freedom vs. social order |
| Local business support: targeted subsidy vs. open competition | Solidarity vs. market competition |
| Infrastructure investment: proven method vs. experimental approach | Stability/tradition vs. openness to change |
| Public safety measure: wider authority vs. stronger oversight | Security vs. civil liberties |
| Budget shortfall: cut services vs. temporary borrowing | Present needs vs. future burden |
| School curriculum: standardized content vs. local adaptation | Centralized reliability vs. local autonomy |
| Housing conflict: speed of new supply vs. protection of existing tenants | Efficiency vs. protection |

The cards produce a private values fingerprint, never sent to the server, that frames the rest of the journey without scoring or labeling it politically. The output is not a match percentage — it is contextual framing: *"You appear to prioritize X and Y. Here are the main Berlin debates where these tensions arise."*

Why this works: indirect measurement is more accurate than asking users what they value directly, because people sincerely report valuing everything. Non-political framing avoids identity-protective activation. Creating a values profile before any party exposure inoculates against anchoring and in-group processing. It also functions as an engaging entry — concrete scenario cards feel like a thinking exercise, not a civics test.

#### Policy layer: blind-first trade-off test

The four Berlin trade-off questions (housing, mobility, climate, budget) from the draft question bank are presented without party labels. After a user answers, the result is shown as an anonymous position matrix — "Party A, B, C…" in randomized order. The user identifies which anonymous positions resonate. Only then do labels reveal.

This blind-reveal mechanic is grounded in research by Ahler and Broockman (2018): when voters see policy positions without party labels, they frequently agree with parties they would otherwise reflexively dismiss. The label reveal creates a genuine moment of discovery — "that was the SPD?" — which is the most identity-updating experience the tool can offer, and one that users remember and share.

Per-card additions:
- A "why this is hard" one-sentence explainer (the genuine tension, not partisan framing).
- A "real Berlin example" (a recent concrete decision where this trade-off was live).
- A **consider-the-opposite prompt** after each answer: *"What would have to be true for you to choose the other option?"* This technique (Mussweiler & Strack, 1999) is among the most reliably effective debiasing interventions documented in the psychology literature; it reduces overconfidence and anchoring without requiring users to change their view.

#### Evidence layer: bias-aware copy additions

The existing source atlas structure is correct. The following additions address specific bias failure modes without altering the data model:

- **Pre-matrix framing:** *"Our views on parties are often shaped by who around us votes for them. The following comparison is based only on documented positions."* Place before the party matrix, not on a separate explainer page.
- **Unfamiliar-party prompt:** When a user has not yet opened a profile for a party whose documented positions are close to their expressed priorities, surface a soft prompt: *"Parties you're less familiar with sometimes hold documented positions closer to your priorities. Here's what the sources say for [Party X]."* This is a non-coercive exposure-to-alternatives nudge, not a recommendation.
- **Sparse-profile label:** Any candidate or party with below-threshold documented coverage displays: *"This profile has fewer documented positions than others. This reflects a data gap in this collection, not a finding about the party."*

#### Candidate layer: position-first, photo-second

Given the strength of personality heuristics in candidate evaluation:

- Candidate profiles lead with documented positions and evidence coverage, not photograph or biography.
- The photograph is presented only after the user has scrolled past or interacted with at least one substantive position card.
- Evidence depth (count of documented positions) is displayed prominently and framed as an information state, never as a quality signal.

### Anti-patterns and their rationale

| Do not | Reason | Alternative |
| --- | --- | --- |
| Show a percentage match score | Creates false precision; users anchor on the number and stop reading the reasoning | Show issue-by-issue agreements and disagreements |
| Reveal party labels before positions | Activates identity-protective cognition before the user has formed a view | Blind-first reveal; labels appear after positions |
| Ask "do you agree with X?" where X is a party slogan or programme title | Measures familiarity and affect, not genuine agreement with the underlying policy | Use neutral policy trade-off wording with named instrument and context |
| Rank candidates by "fit" | Personality heuristics dominate; sparse profiles systematically disadvantage parties that responded honestly | Non-dominated evidence frontier only, subject to coverage threshold |
| Use a left–right political compass as the main product | Does not map reliably to the Berlin ballot; collapses a multidimensional space into one axis | Issue-by-issue comparison in the user's own priority order |
| Display "most popular" or "most used" parties first | Bandwagon effect; suppresses smaller parties before evidence is read | Alphabetical display, equal treatment, no popularity signals |
| Aggregate issue scores into one number | Compensatory logic allows many small agreements to mask one decisive disagreement | Non-compensatory display: show clashes explicitly alongside agreements |
| Use party colours as the primary visual signal | Conditions visual familiarity before position reading; excludes colour-blind users | Text, table headers, accessible patterns, and labels carry the information |

### Engagement principles that do not trivialize the decision

- **Progress through discovery, not score reveal.** *"You've explored 3 of 5 key Berlin debates"* is motivating without gamifying the vote itself.
- **The surprise moment.** The blind label-reveal in the policy layer is inherently memorable and shareable — but only with explicit opt-in, and sharing must reveal nothing about private answers or values profile.
- **Kiez anchoring.** Abstract state-level policies become more engaging when linked to a user's own borough or Wahlkreis. Where source evidence supports it, show a local example alongside the state-level framing.
- **Decision journal.** A private, browser-local log of "what I found" and "what would change my mind" puts the user in the role of investigator rather than quiz-taker. This also operationalizes the counterfactual commitment — the most important deliberative step — in a form the user can return to.
- **Cognitive load ceiling.** Maximum three priority topics, four trade-off cards, four parties in a side-by-side comparison. The paradox of choice research (Iyengar & Lepper, 2000) documents that more options reduce decision quality and satisfaction. Hard limits are a feature.

### Proposed end-to-end user journey

```
1. Values warm-up           (~3 min)
   8 non-political trade-off cards → private values fingerprint (browser only)
   → framing: "You seem to prioritize X and Y — here's where those tensions appear in Berlin"

2. Blind policy test        (~5–8 min)
   4 Berlin trade-offs → anonymous party positions → consider-the-opposite prompt
   → label reveal → discovery moment → opt-in sharing

3. Evidence atlas           (self-directed, 5–15 min)
   Alphabetical party matrix → source context → bias-aware framing copy
   → "challenge your shortlist" exposure nudge for unfamiliar parties

4. Provisional shortlist + counterfactual journal
   "What would change my mind?" → stored in browser only, never sent

5. Candidate explorer       (Erststimme, separate task)
   Evidence depth first → position cards → photo/biography below
   Comparable-answer matrix only where both candidates answered same question/version

6. Ballot brief
   Private summary: two separate decisions, open questions, what still needs checking
```

Steps 2 and 3 are gated by the scientific and legal go/no-go conditions in the 2026 launch plan. The values warm-up (step 1) and decision journal (step 4) contain no party data and can be built and released independently of those gates.

### References for this section

22. Kahan, D. M. (2017). *Misconceptions, misinformation, and the logic of identity-protective cognition*. Cultural Cognition Project Working Paper Series No. 164. Yale Law School. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2973067
23. Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
24. Lodge, M., & Taber, C. S. (2013). *The Rationalizing Voter*. Cambridge University Press. https://doi.org/10.1017/CBO9781139032490
25. Schwartz, S. H. (2012). An overview of the Schwartz theory of basic values. *Online Readings in Psychology and Culture*, 2(1). https://doi.org/10.9707/2307-0919.1116
26. Haidt, J. (2012). *The Righteous Mind: Why Good People Are Divided by Politics and Religion*. Pantheon Books.
27. Baumeister, R. F., Bratslavsky, E., Finkenauer, C., & Vohs, K. D. (2001). Bad is stronger than good. *Review of General Psychology*, 5(4), 323–370. https://doi.org/10.1037/1089-2680.5.4.323
28. Todorov, A., Mandisodza, A. N., Goren, A., & Hall, C. C. (2005). Inferences of competence from faces predict election outcomes. *Science*, 308(5728), 1623–1626. https://doi.org/10.1126/science.1110589
29. Ahler, D. J., & Broockman, D. E. (2018). The delegate paradox: Why polarized politicians can represent citizens best. *Journal of Politics*, 80(4), 1117–1133. https://doi.org/10.1086/698755
30. Mussweiler, T., & Strack, F. (1999). Hypothesis-consistent testing and semantic priming in the anchoring paradigm: A selective accessibility model. *Journal of Experimental Social Psychology*, 35(2), 136–164. https://doi.org/10.1006/jesp.1998.1364
31. Iyengar, S. S., & Lepper, M. R. (2000). When choice is demotivating: Can one desire too much of a good thing? *Journal of Personality and Social Psychology*, 79(6), 995–1006. https://doi.org/10.1037/0022-3514.79.6.995
32. Zajonc, R. B. (1968). Attitudinal effects of mere exposure. *Journal of Personality and Social Psychology Monograph Supplement*, 9(2, Pt. 2), 1–27. https://doi.org/10.1037/h0025848

## References

All web sources were accessed on 4 August 2026.

1. [Landeswahlleiter Berlin — General information for the 2026 Berlin elections](https://www.berlin.de/wahlen/wahlen/berliner-wahlen-2026/allgemeine-informationen/artikel.1578239.php)
2. [Landeswahlleiter Berlin — 12 state lists admitted, 24 July 2026](https://www.berlin.de/wahlen/pressemitteilungen/2026/pressemitteilung.1697177.php)
3. [Landeswahlleiter Berlin — Election proposals and admissions timetable](https://www.berlin.de/wahlen/wahlen/berliner-wahlen-2026/wahlvorschlaege/artikel.1600254.php)
4. Walgrave, S., Nuytemans, M., & Pepermans, K. (2009). *Voting Aid Applications and the Effect of Statement Selection*. West European Politics, 32(6), 1161–1180. [https://doi.org/10.1080/01402380903230637](https://doi.org/10.1080/01402380903230637)
5. Louwerse, T., & Rosema, M. (2014). *The design effects of voting advice applications: Comparing methods of calculating matches*. Acta Politica, 49, 286–312. [https://doi.org/10.1057/ap.2013.30](https://doi.org/10.1057/ap.2013.30)
6. Gemenis, K. (2013). *Estimating parties’ policy positions through voting advice applications: Some methodological considerations*. Acta Politica, 48, 268–295. [https://doi.org/10.1057/ap.2012.36](https://doi.org/10.1057/ap.2012.36)
7. Walgrave, S., van Aelst, P., & Nuytemans, M. (2008). *‘Do the Vote Test’: The Electoral Effects of a Popular Vote Advice Application at the 2004 Belgian Elections*. Acta Politica, 43, 50–70. [https://doi.org/10.1057/palgrave.ap.5500209](https://doi.org/10.1057/palgrave.ap.5500209)
8. [bpb — How the Wahl-O-Mat works](https://www.bpb.de/themen/wahl-o-mat/294576/wie-funktioniert-der-wahl-o-mat/)
9. [bpb — Research on the effects of the Wahl-O-Mat](https://www.bpb.de/themen/wahl-o-mat/177432/die-wirkung-des-wahl-o-mat/)
10. [bpb — Beutelsbacher Consensus](https://www.bpb.de/die-bpb/ueber-uns/auftrag/51310/beutelsbacher-konsens/)
11. [Regulation (EU) 2016/679 (GDPR), especially Articles 5, 9, and 25](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng)
12. [W3C Web Content Accessibility Guidelines (WCAG) 2.2](https://www.w3.org/TR/WCAG22/)
13. [Amt für Statistik Berlin-Brandenburg — Abgeordnetenhaus and BVV elections](https://www.statistik-berlin-brandenburg.de/abgeordnetenhauswahlen-bvv-berlin)
14. [Landeswahlleiter Berlin — 2026 election timetable (PDF), p. 1](https://www.berlin.de/wahlen/wahlen/berliner-wahlen-2026/allgemeine-informationen/terminplan.pdf?ts=1784559033)
15. [bpb — Wahl-O-Mat datasets and conditions of use](https://www.bpb.de/themen/wahl-o-mat/556865/datensaetze-des-wahl-o-mat/)
16. [TDDDG §25 — protection of privacy on terminal equipment](https://www.gesetze-im-internet.de/ttdsg/__25.html)
17. [bpb — Wahl-O-Mat launch information, including Berlin on 24 August 2026](https://www.bpb.de/themen/wahl-o-mat/)
18. Lau, R. R., & Redlawsk, D. P. (1997). *Voting Correctly*. American Political Science Review, 91(3), 585–598. [https://doi.org/10.2307/2952076](https://doi.org/10.2307/2952076)
19. Munzert, S., & Ramirez-Ruiz, S. (2021). *Meta-Analysis of the Effects of Voting Advice Applications*. Political Communication, 38(6), 691–706. [https://doi.org/10.1080/10584609.2020.1843572](https://doi.org/10.1080/10584609.2020.1843572)
20. Lefevere, J., & Walgrave, S. (2014). *A perfect match? The impact of statement selection on voting advice applications’ ability to match voters and parties*. Electoral Studies, 36, 252–262. [https://doi.org/10.1016/j.electstud.2014.04.002](https://doi.org/10.1016/j.electstud.2014.04.002)
21. Holleman, B., Kamoen, N., Krouwel, A., van de Pol, J., & de Vreese, C. (2016). *Positive vs. Negative: The Impact of Question Polarity in Voting Advice Applications*. PLOS ONE, 11(10), e0164184. [https://doi.org/10.1371/journal.pone.0164184](https://doi.org/10.1371/journal.pone.0164184)
