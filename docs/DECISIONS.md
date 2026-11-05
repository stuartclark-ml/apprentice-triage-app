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

**Next.** Week 3's database stores state, so the same boundary protects it;
the Week 3 test is a database query showing no postcodes.