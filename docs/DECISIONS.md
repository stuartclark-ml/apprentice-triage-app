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