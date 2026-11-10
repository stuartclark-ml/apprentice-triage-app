## 1. Form fields replace chat input (12 October 2026)

**Context.** The Week 2 version took free-text chat; Gemini read the message and
called a vacancy search tool. Apprentice applicants are often 16 or 17. Gemini's
API terms do not permit applications likely to be used by under-18s, and free
text can carry special category data (health, disability) about a minor. That
text would also reach LangSmith traces and the database.

**Decision.** Input is three form fields: postcode, distance, arrive-by time. No
applicant text is sent to Gemini. Vacancy search is a plain step, not a model
tool call. Gemini only writes the final explanation, from vacancy and journey
data.

**Rejected.** Keeping chat with filtering (a filter can miss things); adding an
artificial tool so Gemini still calls one (extra scope, contrived).

**Consequences.** The hazard is removed at design stage, by elimination: the top
of the hierarchy of controls, not a later safeguard. Tool calling remains
evidenced by the Week 2 commit and trace. The README states: portfolio
demonstration, not for live use by under-18s.

## 2. Coverage limited to London and nearby (finding, 2 November 2026)

**Context.** Journey checks use Transport for London's journey planner.

**Finding.** It cannot plan journeys far outside London: a Northumberland
postcode returned "degraded" for every vacancy.

**Decision.** Accept the limit for the 20 November release; state it in the
README. The route still ends safely with a plain explanation, not a crash.

**Next.** A national journey planner, after 20 November.

## 3. Data minimisation (decision, 3–5 November 2026)

**Context.** The applicant gives a postcode. Vacancy listings carry employer
contact names, email addresses, phone numbers and site addresses. LangSmith
records the graph's starting input, and Gemini receives whatever the
explanation step sends it.

**Decision.**
- Sanitise before the graph starts. The postcode is looked up once, before
  the graph is invoked; only the area name and coordinates rounded to two
  decimal places enter state. `SafeLocation` has no postcode field, so state
  cannot hold one: privacy comes from the type, not from deleting later.
- Round coordinates to two decimal places: a point moves at most about 550
  metres. Measured cost: journey times of 7, 21 and 23 minutes against 8, 20
  and 24 with exact coordinates.
- Send Gemini an allow-list of six fields only: title, employer, level,
  closing date, journey minutes and feasibility. Never contacts, addresses or
  descriptions; a real listing named a contact person and email address.
- Catch failures by name. A rate limit or server error gives fixed fallback
  wording; configuration errors still crash. Error wording is fixed text and
  never repeats what the user typed.

**Alternatives rejected.** Cleaning inside the first node: the trace has
already recorded the input. Sending the whole vacancy to Gemini: it would
include personal contact details.

**Evidence.** Tests: the postcode is dropped and coordinates rounded;
Gemini receives exactly the allow-listed facts, with no email, postcode or
coordinates; the fallback works on a rate limit. A manual check of a traced
run found no postcode, coordinates, email or address. An unused tool that
accepted a raw postcode was removed on 5 November.

**Limits.** The trace check is manual. The area name is used, not the area
code. Production would add LangSmith input masking and a scheduled scan for
postcode patterns.

**Evidence (10 November).** A database query across all three checkpoint
tables (`checkpoints`, `checkpoint_blobs`, `checkpoint_writes`) found no
applicant postcode in any saved run; the pattern ignored case and spaces. A
control search for an employer name found it in all three tables, so the
search reads the stored data. Rounded coordinates are stored; at two
decimal places each covers many postcodes, and coverage is London-only
(section 2).

## 4. Human review and saved runs (decision, 9–10 November 2026)

**Context.** Gemini's explanation goes to a young applicant (section 1). A
model can state something the source facts do not support, so a person
should check the text before release. That check may take hours, so a
paused run must survive the program stopping.

**Decision.**
- Review comes after Gemini writes. A careers adviser reads the explanation
  beside the six source facts (section 3) and answers `approve` or `reject`.
  Approve releases the text; reject gives fixed wording; any other answer is
  a bug and raises an error, so nothing is released by accident.
- The pause is its own small node. On resume, LangGraph re-runs the paused
  node from its first line; if the pause sat inside the Gemini step, Gemini
  would write again and the adviser would approve text they never saw.
- Runs are saved after every node to PostgreSQL (Neon in development; a
  local container for the demonstration). Code reads only `DATABASE_URL`.
- Two commands, `start` and `resume`, so every resume runs in a new process:
  each review is also a restart test.
- Saved state is rebuilt only from five named classes. Anything else comes
  back as a plain dictionary and fails loudly, instead of the library's
  default of rebuilding any class with a warning.

**Alternatives rejected.** Review before Gemini writes: the adviser would not
see the text the applicant receives. Free-text answers from the adviser: they
cannot be tested, and would put unchecked text into the run. Keeping state in
memory: a restart would lose every waiting review.

**Evidence.** Four tests cover pause, approve, reject and an unknown answer;
40 tests pass in continuous integration. A run paused on 9 November was
resumed on 10 November from a new process and released the saved text
unchanged. A second run after the allow-list was added resumed with no
deserialisation warnings. Database check: section 3.

**Limits.**
- Checkpoints store full vacancy records, including employer contact names,
  email addresses and site postcodes. Gemini never sees them (section 3),
  but the database holds them.
- Review is requested even when the explanation is already fixed wording.
- The resume path is tested only for runs where transport checks succeed; a
  degraded run may store a class not yet on the allow-list.
- Saved checkpoints are never deleted. The adviser copies the run identifier
  from the terminal; there is no list of waiting reviews.

**Next.** First after 20 November: store only the six allow-listed fields
in state. Then: rejection reasons from a fixed list; an automated pre-check
(code for numbers and dates, a small judge model from a different provider
for unsupported wording) that flags issues to the adviser, scored against
the recorded rejection reasons; skip review for fixed wording; and
checkpoint clean-up.

## 5. Area deprivation not used in routing (decision, 10 November 2026)

**Context.** The original design listed the Office for National Statistics
deprivation score as local context, since the service aims to help people
in economically deprived areas.

**Decision.** Deprivation plays no part in routing or the explanation.
Routing answers one question: can the applicant reach this vacancy in time?
An area's deprivation score does not change that answer, so it adds no
value to the decision.

**Alternatives rejected.** As an eligibility gate or priority: it judges a
person by their area's average (the ecological fallacy), so a low-income
applicant in a low-deprivation area would be ranked lower or excluded. As
context in the explanation: no decision depends on it, and it would add a
label about the applicant's area to state and to Gemini's input.

**Evidence.** State holds no deprivation field, and Gemini's six-field
allow-list (section 3) has none. The area code that deprivation data is
keyed by is not stored (section 3), so it cannot be looked up later.