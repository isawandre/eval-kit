#!/usr/bin/env python3
"""setup_premium_packs.py — Creates all 4 premium rubric packs."""
import os, json, textwrap

BASE = os.path.expanduser("~/Desktop/ai_hustle/eval-kit/rubrics")

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(textwrap.dedent(content).lstrip("\n"))
    print(f"  ✅ {path}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATCH 6 — HR COMPLIANCE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n📦 Batch 6 — HR Compliance")

write(f"{BASE}/hr_compliance/manifest.yaml", """
    name: hr_compliance
    version: "1.0.0"
    description: >
      Evaluates LLM-generated HR communications for legal safety,
      bias detection, policy adherence, and documentation quality.
    author: eval-kit
    license: proprietary
    filters:
      - rubric: bias_detection
        weight: 0.20
        scoring_mode: penalty
      - rubric: policy_adherence
        weight: 0.20
        scoring_mode: additive
      - rubric: legal_language
        weight: 0.18
        scoring_mode: penalty
      - rubric: accommodation_compliance
        weight: 0.15
        scoring_mode: additive
      - rubric: termination_protocol
        weight: 0.15
        scoring_mode: penalty
      - rubric: documentation_standards
        weight: 0.12
        scoring_mode: additive
    thresholds:
      pass: 0.80
      partial: 0.55
      fail: 0.0
""")

write(f"{BASE}/hr_compliance/bias_detection.yaml", """
    name: bias_detection
    description: >
      Flags gendered, racial, age-based, or disability-related
      language that could expose the organization to EEOC claims.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: gendered_language
        description: Detects he/she assumptions, gendered job titles
        patterns:
          - "\\\\b(chairman|manpower|policeman|fireman|stewardess)\\\\b"
          - "\\\\b(he|she) (should|must|will)\\\\b"
        penalty: 0.15
        severity: high
        message: "Gendered language detected — use neutral alternatives"

      - id: age_indicators
        description: Flags age-suggestive phrasing
        patterns:
          - "\\\\b(young|youthful|energetic|digital native|mature|seasoned)\\\\b"
          - "\\\\b(recent graduate|fresh out of|old school)\\\\b"
        penalty: 0.15
        severity: high
        message: "Age-indicative language — potential ADEA violation"

      - id: racial_cultural_markers
        description: Detects culturally coded or exclusionary phrasing
        patterns:
          - "\\\\b(culture fit|urban|articulate|well-spoken|exotic)\\\\b"
          - "\\\\b(native english|american-born)\\\\b"
        penalty: 0.20
        severity: critical
        message: "Culturally coded language — disparate impact risk"

      - id: disability_language
        description: Flags ableist terms or physical requirement assumptions
        patterns:
          - "\\\\b(handicapped|crippled|suffers from|wheelchair-bound)\\\\b"
          - "\\\\b(must be able to stand|physically fit|able-bodied)\\\\b"
        penalty: 0.15
        severity: high
        message: "Ableist language or unnecessary physical requirements"

      - id: religious_markers
        description: Detects religious scheduling or belief assumptions
        patterns:
          - "\\\\b(christian values|faith-based|church|sunday availability)\\\\b"
        penalty: 0.10
        severity: medium
        message: "Religious language detected — Title VII concern"
    strengths:
      - pattern: "\\\\b(they|them|the candidate|the applicant|the employee)\\\\b"
        label: "Uses inclusive, gender-neutral references"
      - pattern: "\\\\b(reasonable accommodation|accessible|inclusive)\\\\b"
        label: "Proactive inclusion language"
""")

write(f"{BASE}/hr_compliance/policy_adherence.yaml", """
    name: policy_adherence
    description: >
      Checks that HR responses reference appropriate company policies,
      handbooks, and standard operating procedures.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: handbook_reference
        description: References employee handbook or policy manual
        patterns:
          - "\\\\b(employee handbook|policy manual|company policy|section \\\\d+)\\\\b"
          - "\\\\b(per our policy|as outlined in|in accordance with)\\\\b"
        score: 0.20
        severity: medium
        message: "References organizational policy documentation"

      - id: process_steps
        description: Provides clear procedural steps
        patterns:
          - "\\\\b(step \\\\d|first[,:]|next[,:]|then[,:]|finally[,:])\\\\b"
          - "\\\\b(submit to|file with|notify your|contact HR)\\\\b"
        score: 0.20
        severity: medium
        message: "Outlines clear procedural steps"

      - id: timeline_specificity
        description: Includes specific timeframes or deadlines
        patterns:
          - "\\\\b(within \\\\d+ (days|hours|business days)|by (monday|friday|end of))\\\\b"
          - "\\\\b(deadline|due date|no later than|as soon as)\\\\b"
        score: 0.20
        severity: medium
        message: "Specifies concrete timelines"

      - id: escalation_path
        description: Provides escalation or appeal path
        patterns:
          - "\\\\b(escalate|appeal|grievance|ombudsman|open door)\\\\b"
          - "\\\\b(manager|supervisor|HR director|VP of people)\\\\b"
        score: 0.20
        severity: medium
        message: "Includes escalation or appeal process"

      - id: documentation_directive
        description: Instructs employee to document or retain records
        patterns:
          - "\\\\b(document|keep a record|written confirmation|save a copy)\\\\b"
          - "\\\\b(email trail|paper trail|for your records)\\\\b"
        score: 0.20
        severity: low
        message: "Directs employee to maintain documentation"
    strengths:
      - pattern: "\\\\b(handbook|policy \\\\d+|SOP)\\\\b"
        label: "Direct policy citation"
""")

write(f"{BASE}/hr_compliance/legal_language.yaml", """
    name: legal_language
    description: >
      Ensures HR communications avoid legally dangerous phrasing
      that could create implied contracts or admissions of liability.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: implied_contract
        description: Flags language that could create an implied employment contract
        patterns:
          - "\\\\b(guaranteed|permanent position|job security|we promise)\\\\b"
          - "\\\\b(as long as you want|lifetime|forever)\\\\b"
        penalty: 0.25
        severity: critical
        message: "Implied contract language — at-will employment risk"

      - id: liability_admission
        description: Detects admissions of fault or liability
        patterns:
          - "\\\\b(our fault|we were wrong|we admit|company is responsible)\\\\b"
          - "\\\\b(we failed to|we neglected|we should have)\\\\b"
        penalty: 0.20
        severity: critical
        message: "Potential liability admission detected"

      - id: retaliation_indicators
        description: Flags phrasing that could suggest retaliation
        patterns:
          - "\\\\b(because you filed|since you complained|after your report)\\\\b"
          - "\\\\b(consequence of reporting|result of your grievance)\\\\b"
        penalty: 0.25
        severity: critical
        message: "Retaliatory language — potential whistleblower violation"

      - id: hipaa_phi
        description: Detects protected health information disclosure
        patterns:
          - "\\\\b(diagnosis|medical condition|prescription|treatment for)\\\\b"
          - "\\\\b(doctor said|medical records show|health issue)\\\\b"
        penalty: 0.20
        severity: critical
        message: "Possible PHI disclosure — HIPAA concern"

      - id: missing_at_will_disclaimer
        description: Checks for at-will employment disclaimer when relevant
        patterns:
          - "\\\\b(at-will|at will|does not constitute a contract)\\\\b"
        penalty: -0.10
        severity: low
        message: "Missing at-will disclaimer in employment communication"
    strengths:
      - pattern: "\\\\b(at-will|does not constitute|not a guarantee)\\\\b"
        label: "Proper legal disclaimers present"
""")

write(f"{BASE}/hr_compliance/accommodation_compliance.yaml", """
    name: accommodation_compliance
    description: >
      Evaluates ADA/FMLA accommodation request responses for
      interactive process compliance and reasonable accommodation language.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: interactive_process
        description: Initiates or continues the interactive accommodation process
        patterns:
          - "\\\\b(interactive process|work together to|discuss your needs)\\\\b"
          - "\\\\b(explore options|find a solution|accommodate)\\\\b"
        score: 0.25
        severity: high
        message: "Engages the interactive accommodation process"

      - id: reasonable_accommodation
        description: Offers or discusses specific accommodations
        patterns:
          - "\\\\b(modified schedule|remote work|assistive technology|ergonomic)\\\\b"
          - "\\\\b(reassignment|light duty|leave of absence|flexible hours)\\\\b"
        score: 0.25
        severity: high
        message: "Proposes specific reasonable accommodations"

      - id: medical_documentation
        description: Properly requests supporting documentation
        patterns:
          - "\\\\b(medical documentation|healthcare provider|certification form)\\\\b"
          - "\\\\b(supporting documentation|physician statement)\\\\b"
        score: 0.20
        severity: medium
        message: "Appropriately requests medical documentation"

      - id: confidentiality_assurance
        description: Assures confidential handling of medical information
        patterns:
          - "\\\\b(confidential|private|separate file|need-to-know)\\\\b"
          - "\\\\b(will not be shared|protected information|secure)\\\\b"
        score: 0.15
        severity: medium
        message: "Provides confidentiality assurance for medical info"

      - id: timeline_communication
        description: Sets expectations for accommodation timeline
        patterns:
          - "\\\\b(within \\\\d+|we will respond|expect to hear|follow up by)\\\\b"
        score: 0.15
        severity: low
        message: "Communicates accommodation decision timeline"
    strengths:
      - pattern: "\\\\b(ADA|FMLA|interactive process|reasonable accommodation)\\\\b"
        label: "Cites relevant legislation or framework"
""")

write(f"{BASE}/hr_compliance/termination_protocol.yaml", """
    name: termination_protocol
    description: >
      Evaluates involuntary termination communications for legal
      safety, factual basis, and proper procedural language.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: emotional_language
        description: Flags emotionally charged phrasing inappropriate for termination docs
        patterns:
          - "\\\\b(disappointed in you|let us down|betrayed|disgusted)\\\\b"
          - "\\\\b(you always|you never|everyone knows|attitude problem)\\\\b"
        penalty: 0.20
        severity: high
        message: "Emotional or subjective language — document with facts"

      - id: discriminatory_timing
        description: Flags references suggesting discriminatory termination timing
        patterns:
          - "\\\\b(after (your|the) pregnancy|since (your|the) diagnosis)\\\\b"
          - "\\\\b(after you turned \\\\d+|since you filed)\\\\b"
        penalty: 0.25
        severity: critical
        message: "Timing language suggests discriminatory motive"

      - id: missing_factual_basis
        description: Checks for documented, specific performance issues
        patterns:
          - "\\\\b(on \\\\d{1,2}/\\\\d{1,2}|dated|documented|written warning)\\\\b"
          - "\\\\b(performance review|PIP|improvement plan|incident report)\\\\b"
        penalty: -0.15
        severity: high
        message: "Provide specific dates and documented incidents"

      - id: benefits_cobra_info
        description: Includes COBRA and benefits continuation information
        patterns:
          - "\\\\b(COBRA|benefits continuation|health insurance|coverage end)\\\\b"
          - "\\\\b(final paycheck|accrued PTO|severance)\\\\b"
        penalty: -0.15
        severity: medium
        message: "Include COBRA/benefits and final compensation details"

      - id: release_agreement_mention
        description: References separation agreement if applicable
        patterns:
          - "\\\\b(separation agreement|release|waiver|non-compete)\\\\b"
          - "\\\\b(\\\\d+ days to review|consult an attorney|revocation period)\\\\b"
        penalty: -0.10
        severity: medium
        message: "Mention separation agreement review period"
    strengths:
      - pattern: "\\\\b(documented|on \\\\d|written warning|PIP)\\\\b"
        label: "Factual, documented basis for decision"
""")

write(f"{BASE}/hr_compliance/documentation_standards.yaml", """
    name: documentation_standards
    description: >
      Ensures HR communications meet professional documentation
      standards including clarity, completeness, and proper formatting.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: professional_tone
        description: Uses professional, neutral tone throughout
        patterns:
          - "\\\\b(please|thank you|we appreciate|we understand)\\\\b"
          - "\\\\b(respectfully|for your information|as discussed)\\\\b"
        score: 0.15
        severity: low
        message: "Maintains professional tone"

      - id: action_items
        description: Lists clear action items or next steps
        patterns:
          - "\\\\b(action item|next step|please (complete|submit|contact|return))\\\\b"
          - "\\\\b(you will need to|required to|expected to)\\\\b"
        score: 0.20
        severity: medium
        message: "Includes clear action items"

      - id: contact_information
        description: Provides specific contact for questions
        patterns:
          - "\\\\b(contact|reach out to|questions.+(email|call|phone))\\\\b"
          - "\\\\b(HR (department|representative|team)|your manager)\\\\b"
        score: 0.20
        severity: medium
        message: "Provides point of contact for follow-up"

      - id: date_stamping
        description: Includes dates or references temporal context
        patterns:
          - "\\\\b(effective|as of|dated|beginning|starting)\\\\b"
          - "\\\\b(\\\\d{1,2}/\\\\d{1,2}/\\\\d{2,4}|january|february|march|april|may|june|july|august|september|october|november|december)\\\\b"
        score: 0.20
        severity: medium
        message: "Includes date references for record-keeping"

      - id: signature_block
        description: Ends with appropriate sign-off
        patterns:
          - "\\\\b(sincerely|regards|respectfully|best regards|thank you)\\\\b"
          - "\\\\b(HR department|human resources|people operations)\\\\b"
        score: 0.15
        severity: low
        message: "Proper professional sign-off"

      - id: cc_or_distribution
        description: Notes distribution or copies
        patterns:
          - "\\\\b(cc:|copy to|distributed to|filed in|personnel file)\\\\b"
        score: 0.10
        severity: low
        message: "Notes document distribution"
    strengths:
      - pattern: "\\\\b(attached|enclosed|see appendix|refer to)\\\\b"
        label: "References supporting documents"
""")

# HR Compliance benchmarks
benchmarks_hr = [
    {
        "id": "hr_001",
        "text": "Dear Employee, We are pleased to inform you that your request for a modified work schedule has been approved as part of the interactive accommodation process under the ADA. As discussed on 03/15/2025, you will transition to a 4x10 schedule effective 04/01/2025. Your healthcare provider's documentation has been received and filed confidentially in a separate medical file. Please contact HR at hr@company.com or ext. 4200 with any questions. Your manager has been notified of the schedule change on a need-to-know basis only. Per company policy Section 7.2, this accommodation will be reviewed in 90 days. Please submit any changes in your condition to HR within 5 business days. This letter does not constitute a contract and your employment remains at-will. Sincerely, Human Resources Department. CC: Personnel file.",
        "expected_score_min": 0.85,
        "expected_verdict": "pass",
        "description": "Strong accommodation response with all compliance elements"
    },
    {
        "id": "hr_002",
        "text": "Hey, so we need to talk about your performance. Honestly everyone on the team is pretty disappointed. You've had an attitude problem since day one and frankly we should have let you go a long time ago. Since you turned 50 last year things have really gone downhill. Consider this your notice.",
        "expected_score_max": 0.30,
        "expected_verdict": "fail",
        "description": "Terrible termination communication — emotional, discriminatory, no documentation"
    },
    {
        "id": "hr_003",
        "text": "We are writing to confirm the termination of your employment effective 03/20/2025. As documented in your Performance Improvement Plan dated 01/10/2025 and the written warning issued on 02/14/2025, the required performance benchmarks were not met within the specified 60-day period. Your final paycheck including 5 days of accrued PTO will be mailed to your address on file. COBRA continuation coverage information will be sent separately within 14 days. Please return your laptop and badge to IT by 5 PM on your last day. You have 21 days to review the enclosed separation agreement and are encouraged to consult an attorney. Contact Sarah Chen in HR at schen@company.com with questions. Regards, Human Resources.",
        "expected_score_min": 0.75,
        "expected_verdict": "pass",
        "description": "Proper termination with documented basis and all required info"
    },
    {
        "id": "hr_004",
        "text": "We need a young, energetic digital native to join our fast-paced team. He should be physically fit and able-bodied with a strong Christian work ethic. Must be a native English speaker. Culture fit is essential. The chairman needs someone who can keep up.",
        "expected_score_max": 0.20,
        "expected_verdict": "fail",
        "description": "Job posting riddled with bias — age, gender, religion, disability, cultural"
    }
]

benchmarks_path = f"{BASE}/hr_compliance/benchmarks"
os.makedirs(benchmarks_path, exist_ok=True)
with open(f"{benchmarks_path}/hr_compliance.jsonl", "w") as f:
    for entry in benchmarks_hr:
        f.write(json.dumps(entry) + "\n")
print(f"  ✅ {benchmarks_path}/hr_compliance.jsonl")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATCH 7 — SALES ENABLEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n📦 Batch 7 — Sales Enablement")

write(f"{BASE}/sales_enablement/manifest.yaml", """
    name: sales_enablement
    version: "1.0.0"
    description: >
      Evaluates LLM-generated sales communications for persuasion
      quality, objection handling, value articulation, and closing technique.
    author: eval-kit
    license: proprietary
    filters:
      - rubric: objection_handling
        weight: 0.20
        scoring_mode: additive
      - rubric: value_proposition
        weight: 0.20
        scoring_mode: additive
      - rubric: urgency_creation
        weight: 0.15
        scoring_mode: additive
      - rubric: competitor_positioning
        weight: 0.15
        scoring_mode: additive
      - rubric: closing_technique
        weight: 0.15
        scoring_mode: additive
      - rubric: rapport_building
        weight: 0.15
        scoring_mode: additive
    thresholds:
      pass: 0.75
      partial: 0.50
      fail: 0.0
""")

write(f"{BASE}/sales_enablement/objection_handling.yaml", """
    name: objection_handling
    description: >
      Evaluates quality of objection acknowledgment, reframing,
      and evidence-based responses to common buyer pushback.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: acknowledgment
        description: Validates the prospect's concern before responding
        patterns:
          - "\\\\b(I understand|that's a fair|valid concern|I hear you|makes sense)\\\\b"
          - "\\\\b(you're right to|many (customers|clients) ask|common question)\\\\b"
        score: 0.20
        severity: high
        message: "Acknowledges objection before responding"

      - id: reframe
        description: Reframes the objection as an opportunity or different angle
        patterns:
          - "\\\\b(what if|another way to look|consider this|the flip side)\\\\b"
          - "\\\\b(actually.+benefit|turns out|in practice)\\\\b"
        score: 0.20
        severity: high
        message: "Reframes objection constructively"

      - id: social_proof
        description: Uses case studies, testimonials, or data to support response
        patterns:
          - "\\\\b(for example|one of our clients|case study|we saw \\\\d+%)\\\\b"
          - "\\\\b(company like yours|similar situation|industry average)\\\\b"
        score: 0.25
        severity: high
        message: "Provides social proof or evidence"

      - id: specificity
        description: Gives specific numbers, timelines, or outcomes
        patterns:
          - "\\\\b(\\\\d+%|\\\\$\\\\d+|within \\\\d+ (days|weeks|months))\\\\b"
          - "\\\\b(ROI|payback period|saved|reduced|increased)\\\\b"
        score: 0.20
        severity: medium
        message: "Uses specific metrics and outcomes"

      - id: bridge_to_next
        description: Transitions smoothly to next step after handling objection
        patterns:
          - "\\\\b(would it help if|shall I|can I show you|let me)\\\\b"
          - "\\\\b(next step|walk you through|demo|free trial)\\\\b"
        score: 0.15
        severity: medium
        message: "Bridges objection handling to forward momentum"
    strengths:
      - pattern: "\\\\b(ROI|\\\\d+%|saved|case study)\\\\b"
        label: "Data-driven objection response"
""")

write(f"{BASE}/sales_enablement/value_proposition.yaml", """
    name: value_proposition
    description: >
      Measures how effectively the response articulates unique
      value, ROI, and differentiated benefits for the prospect.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: outcome_focus
        description: Leads with outcomes, not features
        patterns:
          - "\\\\b(you'll (see|get|achieve|save|reduce|gain))\\\\b"
          - "\\\\b(result(s| is)|outcome|impact|bottom line)\\\\b"
        score: 0.25
        severity: high
        message: "Focuses on outcomes over features"

      - id: quantified_benefit
        description: Attaches numbers to claimed benefits
        patterns:
          - "\\\\b(\\\\d+%|\\\\d+x|\\\\$\\\\d+|\\\\d+ hours)\\\\b"
          - "\\\\b(reduce.+by|increase.+by|save.+per)\\\\b"
        score: 0.25
        severity: high
        message: "Quantifies the value proposition"

      - id: pain_point_alignment
        description: Connects value directly to stated prospect pain
        patterns:
          - "\\\\b(you mentioned|your challenge|your team's|the problem you)\\\\b"
          - "\\\\b(struggle with|pain point|bottleneck|frustration)\\\\b"
        score: 0.20
        severity: medium
        message: "Aligns value with prospect's specific pain"

      - id: differentiation
        description: Explains what makes this solution unique
        patterns:
          - "\\\\b(only|unique|unlike|no other|what sets us apart)\\\\b"
          - "\\\\b(proprietary|patented|exclusive|built specifically)\\\\b"
        score: 0.15
        severity: medium
        message: "Articulates competitive differentiation"

      - id: risk_reduction
        description: Reduces perceived risk of purchase
        patterns:
          - "\\\\b(guarantee|free trial|no commitment|money back)\\\\b"
          - "\\\\b(pilot|proof of concept|risk-free|cancel anytime)\\\\b"
        score: 0.15
        severity: medium
        message: "Reduces purchase risk for prospect"
    strengths:
      - pattern: "\\\\b(you'll|your team will|your company)\\\\b"
        label: "Prospect-centered value framing"
""")

write(f"{BASE}/sales_enablement/urgency_creation.yaml", """
    name: urgency_creation
    description: >
      Evaluates use of ethical urgency and scarcity tactics to
      motivate prospect action without manipulation.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: time_bound_offer
        description: Presents a legitimate time-limited opportunity
        patterns:
          - "\\\\b(this (week|month|quarter)|by (Friday|end of)|limited time)\\\\b"
          - "\\\\b(expires|deadline|before|offer ends)\\\\b"
        score: 0.25
        severity: medium
        message: "Creates legitimate time-bound urgency"

      - id: cost_of_inaction
        description: Illustrates what happens if prospect does nothing
        patterns:
          - "\\\\b(every (day|week|month) you|continuing to|without this)\\\\b"
          - "\\\\b(cost of doing nothing|status quo|falling behind|competitors are)\\\\b"
        score: 0.25
        severity: medium
        message: "Quantifies cost of inaction"

      - id: scarcity_signal
        description: Signals limited availability or capacity
        patterns:
          - "\\\\b(limited (spots|seats|capacity)|only \\\\d+ (left|remaining))\\\\b"
          - "\\\\b(waitlist|fully booked|next (cohort|batch|slot))\\\\b"
        score: 0.20
        severity: medium
        message: "Uses ethical scarcity signals"

      - id: momentum_language
        description: Uses forward-moving, action-oriented phrasing
        patterns:
          - "\\\\b(get started|hit the ground|launch|kick off|begin)\\\\b"
          - "\\\\b(today|right now|immediately|this afternoon)\\\\b"
        score: 0.15
        severity: low
        message: "Uses momentum language"

      - id: peer_movement
        description: Shows competitors or peers already acting
        patterns:
          - "\\\\b(your competitors|industry is moving|peers are already)\\\\b"
          - "\\\\b(companies like|teams at|just signed|recently adopted)\\\\b"
        score: 0.15
        severity: low
        message: "Shows peer/competitor movement"
    strengths:
      - pattern: "\\\\b(this quarter|before|get started today)\\\\b"
        label: "Clean urgency without desperation"
""")

write(f"{BASE}/sales_enablement/competitor_positioning.yaml", """
    name: competitor_positioning
    description: >
      Evaluates how the response positions against competitors
      without badmouthing — professional contrast over attack.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: professional_contrast
        description: Draws comparison without negative language
        patterns:
          - "\\\\b(where we differ|our approach|we focus on|we prioritize)\\\\b"
          - "\\\\b(compared to|while others|traditional solutions)\\\\b"
        score: 0.25
        severity: high
        message: "Professional competitive contrast"

      - id: strength_based
        description: Leads with own strengths rather than competitor weaknesses
        patterns:
          - "\\\\b(our strength|what we do (well|best)|we excel)\\\\b"
          - "\\\\b(built for|designed to|optimized for|specializ)\\\\b"
        score: 0.25
        severity: high
        message: "Strength-based positioning"

      - id: use_case_fit
        description: Positions based on specific use-case superiority
        patterns:
          - "\\\\b(for (teams|companies|workflows) like yours)\\\\b"
          - "\\\\b(your specific|in your (industry|space|market))\\\\b"
        score: 0.20
        severity: medium
        message: "Use-case-specific positioning"

      - id: migration_ease
        description: Addresses switching cost concerns
        patterns:
          - "\\\\b(easy to switch|migration|import|onboarding takes)\\\\b"
          - "\\\\b(we handle the|transition|up and running in)\\\\b"
        score: 0.15
        severity: medium
        message: "Addresses switching friction"

      - id: honest_limitations
        description: Acknowledges own limitations honestly
        patterns:
          - "\\\\b(we're not the best fit if|where we're still growing)\\\\b"
          - "\\\\b(honestly|to be transparent|fair to say)\\\\b"
        score: 0.15
        severity: low
        message: "Honest about limitations — builds trust"
    strengths:
      - pattern: "\\\\b(where we differ|our approach|built for)\\\\b"
        label: "Mature competitive positioning"
""")

write(f"{BASE}/sales_enablement/closing_technique.yaml", """
    name: closing_technique
    description: >
      Evaluates the quality and clarity of the call-to-action,
      next-step proposal, and closing momentum.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: clear_ask
        description: Makes a specific, unambiguous ask
        patterns:
          - "\\\\b(can we schedule|would (Tuesday|Thursday|next week) work)\\\\b"
          - "\\\\b(I'd like to|shall I send|let's book|how about)\\\\b"
        score: 0.25
        severity: high
        message: "Clear, specific call to action"

      - id: assumed_close
        description: Uses assumptive closing language (when appropriate)
        patterns:
          - "\\\\b(when you're ready|once we get started|after you sign up)\\\\b"
          - "\\\\b(your onboarding|your account|your team's access)\\\\b"
        score: 0.20
        severity: medium
        message: "Assumptive closing language"

      - id: two_option_close
        description: Offers two choices instead of yes/no
        patterns:
          - "\\\\b(would you prefer.+or|option A.+option B|this week or next)\\\\b"
          - "\\\\b(morning or afternoon|starter or pro|monthly or annual)\\\\b"
        score: 0.20
        severity: medium
        message: "Two-option close — avoids binary yes/no"

      - id: next_step_specificity
        description: Proposes a concrete, calendar-specific next step
        patterns:
          - "\\\\b(this (Monday|Tuesday|Wednesday|Thursday|Friday)|at \\\\d+)\\\\b"
          - "\\\\b(15-minute|30-minute|quick call|demo on)\\\\b"
        score: 0.20
        severity: medium
        message: "Proposes specific next step with timing"

      - id: low_commitment_entry
        description: Offers low-friction first step
        patterns:
          - "\\\\b(no commitment|just a quick|free|no obligation|5 minutes)\\\\b"
          - "\\\\b(take a look|check it out|see if|explore)\\\\b"
        score: 0.15
        severity: low
        message: "Low-commitment entry point reduces friction"
    strengths:
      - pattern: "\\\\b(schedule|book|this week|Tuesday|demo)\\\\b"
        label: "Calendar-specific closing"
""")

write(f"{BASE}/sales_enablement/rapport_building.yaml", """
    name: rapport_building
    description: >
      Evaluates personalization, empathy signals, and
      relationship-building language in sales communications.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: personalization
        description: References prospect-specific details
        patterns:
          - "\\\\b(you mentioned|I noticed (your|on your)|your (company|team|website))\\\\b"
          - "\\\\b(based on our (call|chat|conversation)|as you said)\\\\b"
        score: 0.25
        severity: high
        message: "Personalized to prospect's context"

      - id: empathy_signals
        description: Shows understanding of prospect's situation
        patterns:
          - "\\\\b(I (get|understand) (how|that|why)|that must be|sounds like)\\\\b"
          - "\\\\b(challenging|frustrating|exciting|important to you)\\\\b"
        score: 0.20
        severity: medium
        message: "Empathy signals present"

      - id: name_usage
        description: Uses prospect's name naturally
        patterns:
          - "\\\\b(Hi |Hey |Dear |Thanks )\\\\w+\\\\b"
        score: 0.15
        severity: low
        message: "Natural name usage"

      - id: shared_context
        description: References shared experiences or mutual connections
        patterns:
          - "\\\\b(we both|like you|in our industry|as a fellow)\\\\b"
          - "\\\\b(mutual|referred by|connected through|at the conference)\\\\b"
        score: 0.20
        severity: medium
        message: "Establishes shared context"

      - id: genuine_curiosity
        description: Asks about prospect's goals beyond the sale
        patterns:
          - "\\\\b(what are you hoping|where do you see|what's your vision)\\\\b"
          - "\\\\b(long-term|bigger picture|beyond just|what matters most)\\\\b"
        score: 0.20
        severity: medium
        message: "Shows genuine curiosity about prospect's goals"
    strengths:
      - pattern: "\\\\b(you mentioned|I noticed|based on our)\\\\b"
        label: "Prospect-specific personalization"
""")

# Sales benchmarks
benchmarks_sales = [
    {
        "id": "sales_001",
        "text": "Hi Sarah, thanks for taking the time on Tuesday — I really enjoyed learning about how your team at Meridian handles inbound qualification. You mentioned the big bottleneck is lead scoring taking 3 hours per rep per day. I understand how frustrating that must be, especially heading into Q4. Here's the thing: companies like yours — mid-market SaaS with 15-30 SDRs — typically see a 62% reduction in manual scoring time within the first month on our platform. TechCorp, who's in a similar space, went from 3 hours to 45 minutes per rep and increased their qualified pipeline by 28% last quarter. Where we differ from tools like Clearbit or MadKudu is that we're built specifically for high-velocity B2B teams. Our scoring model trains on your historical conversion data, not generic firmographics. Now, I know switching platforms mid-quarter sounds painful — our onboarding team handles the full migration and most teams are live within 5 business days. Would next Thursday afternoon work for a 30-minute demo with your head of RevOps? I can show the scoring dashboard on your actual lead data. No commitment — just want to show you what 45 minutes looks like instead of 3 hours.",
        "expected_score_min": 0.80,
        "expected_verdict": "pass",
        "description": "Excellent sales email with personalization, data, urgency, and clear close"
    },
    {
        "id": "sales_002",
        "text": "Hey, just checking in to see if you had any thoughts on our product. We're the best in the market and way better than the competition. Let me know if you want to buy. Thanks.",
        "expected_score_max": 0.25,
        "expected_verdict": "fail",
        "description": "Lazy follow-up with no personalization, no value, no technique"
    }
]

benchmarks_path = f"{BASE}/sales_enablement/benchmarks"
os.makedirs(benchmarks_path, exist_ok=True)
with open(f"{benchmarks_path}/sales_enablement.jsonl", "w") as f:
    for entry in benchmarks_sales:
        f.write(json.dumps(entry) + "\n")
print(f"  ✅ {benchmarks_path}/sales_enablement.jsonl")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATCH 8 — TECHNICAL DOCS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n📦 Batch 8 — Technical Documentation")

write(f"{BASE}/technical_docs/manifest.yaml", """
    name: technical_docs
    version: "1.0.0"
    description: >
      Evaluates LLM-generated technical documentation for accuracy,
      completeness, code quality, readability, and reference standards.
    author: eval-kit
    license: proprietary
    filters:
      - rubric: accuracy
        weight: 0.22
        scoring_mode: penalty
      - rubric: completeness
        weight: 0.20
        scoring_mode: additive
      - rubric: code_examples
        weight: 0.18
        scoring_mode: additive
      - rubric: readability
        weight: 0.15
        scoring_mode: additive
      - rubric: versioning
        weight: 0.12
        scoring_mode: additive
      - rubric: api_reference
        weight: 0.13
        scoring_mode: additive
    thresholds:
      pass: 0.78
      partial: 0.50
      fail: 0.0
""")

write(f"{BASE}/technical_docs/accuracy.yaml", """
    name: accuracy
    description: >
      Detects inaccurate, outdated, or misleading technical claims
      including deprecated syntax, wrong defaults, and hallucinated APIs.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: deprecated_syntax
        description: Flags known deprecated patterns
        patterns:
          - "\\\\b(var |document\\\\.write|eval\\\\()\\\\b"
          - "\\\\b(componentWillMount|componentWillReceiveProps)\\\\b"
        penalty: 0.15
        severity: high
        message: "Uses deprecated syntax or API"

      - id: incorrect_defaults
        description: Flags commonly hallucinated default values
        patterns:
          - "\\\\b(defaults? to null|default(s| is) undefined)\\\\b"
        penalty: 0.10
        severity: medium
        message: "Possibly incorrect default value claim"

      - id: version_mismatch
        description: References features from wrong versions
        patterns:
          - "\\\\b(Python 2|ES5|React 15|Node 8|Angular 1|jQuery)\\\\b"
        penalty: 0.10
        severity: medium
        message: "References outdated version or framework"

      - id: security_antipattern
        description: Suggests insecure practices
        patterns:
          - "\\\\b(disable SSL|verify=False|--no-check-certificate)\\\\b"
          - "\\\\b(chmod 777|password in (url|query|source|code))\\\\b"
        penalty: 0.20
        severity: critical
        message: "Documents insecure practice without warning"

      - id: ambiguous_claim
        description: Makes unsupported absolute claims
        patterns:
          - "\\\\b(always works|never fails|guaranteed to|100% (safe|secure|reliable))\\\\b"
        penalty: 0.10
        severity: medium
        message: "Unsupported absolute claim"
    strengths:
      - pattern: "\\\\b(as of version|since \\\\d+\\\\.\\\\d+|introduced in|deprecated since)\\\\b"
        label: "Version-aware documentation"
""")

write(f"{BASE}/technical_docs/completeness.yaml", """
    name: completeness
    description: >
      Checks that technical documentation covers prerequisites,
      parameters, return values, errors, and edge cases.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: prerequisites
        description: Lists prerequisites, dependencies, or requirements
        patterns:
          - "\\\\b(prerequisite|requires?|dependency|you'll need|install|setup)\\\\b"
          - "\\\\b(before you (begin|start)|make sure|ensure that)\\\\b"
        score: 0.20
        severity: high
        message: "Includes prerequisites or setup requirements"

      - id: parameters_documented
        description: Documents function/API parameters
        patterns:
          - "\\\\b(param(eter)?s?|argument|option|flag|accepts?)\\\\b"
          - "\\\\b(type:|string|int|bool|float|array|object|dict|list)\\\\b"
        score: 0.20
        severity: high
        message: "Documents parameters with types"

      - id: return_values
        description: Specifies what the function/endpoint returns
        patterns:
          - "\\\\b(returns?|response|output|result|yields?)\\\\b"
          - "\\\\b(status code|payload|body|JSON|object)\\\\b"
        score: 0.20
        severity: high
        message: "Documents return values"

      - id: error_handling
        description: Documents possible errors and how to handle them
        patterns:
          - "\\\\b(error|exception|throws?|raises?|fails? (with|when|if))\\\\b"
          - "\\\\b(try|catch|except|error code|4\\\\d{2}|5\\\\d{2})\\\\b"
        score: 0.20
        severity: high
        message: "Documents error cases"

      - id: edge_cases
        description: Mentions edge cases, limitations, or gotchas
        patterns:
          - "\\\\b(edge case|caveat|gotcha|limitation|note that|be aware)\\\\b"
          - "\\\\b(does not (support|handle|work)|won't work (if|when|with))\\\\b"
        score: 0.20
        severity: medium
        message: "Addresses edge cases or limitations"
    strengths:
      - pattern: "\\\\b(caveat|gotcha|edge case|note:|warning:)\\\\b"
        label: "Proactive about edge cases"
""")

write(f"{BASE}/technical_docs/code_examples.yaml", """
    name: code_examples
    description: >
      Evaluates quality of code examples including runnability,
      context, comments, and output samples.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: has_code_block
        description: Includes at least one formatted code block
        patterns:
          - "```"
          - "\\\\b(example|snippet|sample code|usage|here's how)\\\\b"
        score: 0.20
        severity: high
        message: "Includes code examples"

      - id: language_specified
        description: Code blocks specify the language for syntax highlighting
        patterns:
          - "```(python|javascript|typescript|bash|shell|java|go|rust|sql|yaml|json)"
        score: 0.15
        severity: medium
        message: "Code blocks specify language"

      - id: comments_present
        description: Code includes inline comments explaining key lines
        patterns:
          - "(#|//) .{10,}"
        score: 0.15
        severity: medium
        message: "Code includes explanatory comments"

      - id: expected_output
        description: Shows expected output or result of running the code
        patterns:
          - "\\\\b(output|result|returns|prints|produces|you'll see)\\\\b"
          - "\\\\b(>>> |\\\\$ |expected:|# Output)\\\\b"
        score: 0.20
        severity: high
        message: "Shows expected output"

      - id: imports_included
        description: Includes necessary imports and setup code
        patterns:
          - "\\\\b(import |from .+ import|require\\\\(|include|using )\\\\b"
        score: 0.15
        severity: medium
        message: "Includes imports and dependencies"

      - id: copy_paste_ready
        description: Code is complete enough to copy-paste and run
        patterns:
          - "\\\\b(def |function |class |const |let |async )\\\\b"
        score: 0.15
        severity: medium
        message: "Code appears copy-paste runnable"
    strengths:
      - pattern: "```(python|javascript|typescript)"
        label: "Properly formatted code blocks"
""")

write(f"{BASE}/technical_docs/readability.yaml", """
    name: readability
    description: >
      Evaluates documentation readability including structure,
      headers, paragraph length, and jargon management.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: headers_present
        description: Uses headers to organize content
        patterns:
          - "^#{1,4} "
          - "\\\\b(overview|getting started|installation|usage|configuration|API)\\\\b"
        score: 0.20
        severity: medium
        message: "Uses headers for structure"

      - id: short_paragraphs
        description: Keeps paragraphs focused and scannable
        patterns:
          - "\\\\n\\\\n"
        score: 0.15
        severity: low
        message: "Uses paragraph breaks for scannability"

      - id: bullet_lists
        description: Uses lists for multi-item information
        patterns:
          - "^[\\\\-\\\\*] "
          - "^\\\\d+\\\\. "
        score: 0.15
        severity: low
        message: "Uses lists for structured information"

      - id: jargon_defined
        description: Defines technical terms on first use
        patterns:
          - "\\\\b(i\\\\.e\\\\.|meaning|also known as|refers to|defined as)\\\\b"
          - "\\\\b(\\\\(.+\\\\)|— .+—)\\\\b"
        score: 0.20
        severity: medium
        message: "Defines technical terms for clarity"

      - id: transition_signals
        description: Uses transitions between sections
        patterns:
          - "\\\\b(next|then|after|now that|once you've|with that done)\\\\b"
          - "\\\\b(first|second|finally|additionally|however)\\\\b"
        score: 0.15
        severity: low
        message: "Uses transition language between sections"

      - id: tldr_summary
        description: Includes a summary or TL;DR
        patterns:
          - "\\\\b(TL;?DR|summary|in short|key takeaway|quick start)\\\\b"
        score: 0.15
        severity: low
        message: "Includes summary or quick-start section"
    strengths:
      - pattern: "\\\\b(TL;?DR|quick start|getting started)\\\\b"
        label: "Reader-friendly entry point"
""")

write(f"{BASE}/technical_docs/versioning.yaml", """
    name: versioning
    description: >
      Checks that documentation references specific versions,
      changelogs, deprecation notices, and migration guides.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: version_numbers
        description: References specific version numbers
        patterns:
          - "\\\\b(v?\\\\d+\\\\.\\\\d+(\\\\.\\\\d+)?|version \\\\d+)\\\\b"
          - "\\\\b(latest|stable|LTS|nightly|beta|alpha)\\\\b"
        score: 0.25
        severity: high
        message: "References specific versions"

      - id: changelog_reference
        description: Points to changelog or release notes
        patterns:
          - "\\\\b(changelog|release notes|what's new|breaking changes)\\\\b"
          - "\\\\b(added in|removed in|changed in|fixed in)\\\\b"
        score: 0.20
        severity: medium
        message: "References changelog or release notes"

      - id: deprecation_notice
        description: Marks deprecated features clearly
        patterns:
          - "\\\\b(deprecated|will be removed|legacy|replaced by|use .+ instead)\\\\b"
        score: 0.20
        severity: high
        message: "Includes deprecation notices"

      - id: migration_guidance
        description: Provides upgrade or migration instructions
        patterns:
          - "\\\\b(migrat|upgrad|switch (from|to)|moving from)\\\\b"
          - "\\\\b(before:.+after:|old:.+new:|replace .+ with)\\\\b"
        score: 0.20
        severity: medium
        message: "Includes migration guidance"

      - id: compatibility_matrix
        description: Lists compatibility with other tools or versions
        patterns:
          - "\\\\b(compatible with|works with|requires .+ \\\\d+|supported on)\\\\b"
          - "\\\\b(tested (on|with)|minimum version|recommended version)\\\\b"
        score: 0.15
        severity: medium
        message: "Includes compatibility information"
    strengths:
      - pattern: "\\\\b(v\\\\d+\\\\.\\\\d+|migration|deprecated)\\\\b"
        label: "Version-conscious documentation"
""")

write(f"{BASE}/technical_docs/api_reference.yaml", """
    name: api_reference
    description: >
      Evaluates API documentation for endpoint clarity, request/response
      schemas, authentication details, and rate limit disclosure.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: endpoint_format
        description: Documents endpoints with HTTP method and path
        patterns:
          - "\\\\b(GET|POST|PUT|PATCH|DELETE|HEAD)\\\\b"
          - "\\\\b(/api/|/v\\\\d+/|endpoint|route|URL)\\\\b"
        score: 0.20
        severity: high
        message: "Documents API endpoints with HTTP methods"

      - id: request_schema
        description: Shows request body or query parameter structure
        patterns:
          - "\\\\b(request body|payload|query param|header|content-type)\\\\b"
          - "\\\\b(required|optional|default|type)\\\\b"
        score: 0.20
        severity: high
        message: "Documents request schema"

      - id: response_schema
        description: Shows response structure with field descriptions
        patterns:
          - "\\\\b(response|returns|status \\\\d{3}|body|schema)\\\\b"
          - "\\\\b(field|property|key|value|nested)\\\\b"
        score: 0.20
        severity: high
        message: "Documents response schema"

      - id: auth_details
        description: Explains authentication requirements
        patterns:
          - "\\\\b(auth|token|API key|bearer|OAuth|JWT|credentials)\\\\b"
          - "\\\\b(header|Authorization|X-API-Key|login|session)\\\\b"
        score: 0.20
        severity: high
        message: "Documents authentication requirements"

      - id: rate_limits
        description: Discloses rate limiting or quotas
        patterns:
          - "\\\\b(rate limit|quota|throttl|requests per|per (minute|second|hour))\\\\b"
          - "\\\\b(429|too many requests|retry-after|backoff)\\\\b"
        score: 0.10
        severity: medium
        message: "Discloses rate limits"

      - id: curl_example
        description: Includes a curl or equivalent request example
        patterns:
          - "\\\\b(curl|httpie|fetch|axios|requests\\\\.)\\\\b"
        score: 0.10
        severity: low
        message: "Includes request example"
    strengths:
      - pattern: "\\\\b(curl|GET /|POST /|status 200)\\\\b"
        label: "Concrete API examples"
""")

# Technical docs benchmarks
benchmarks_tech = [
    {
        "id": "tech_001",
        "text": "# User Authentication API\\n\\n## Overview\\n\\nThe Auth API handles user registration, login, and token management. Requires v2.3.0 or later.\\n\\n## Prerequisites\\n\\n- Node.js >= 18.0\\n- Redis 7.x for session storage\\n- `npm install @acme/auth-sdk`\\n\\n## POST /api/v2/auth/login\\n\\nAuthenticates a user and returns a JWT.\\n\\n**Request Body** (JSON):\\n\\n| Field | Type | Required | Description |\\n|-------|------|----------|-------------|\\n| email | string | yes | User email |\\n| password | string | yes | Min 8 chars |\\n\\n```bash\\ncurl -X POST https://api.acme.com/v2/auth/login \\\\\\n  -H 'Content-Type: application/json' \\\\\\n  -d '{\"email\": \"user@test.com\", \"password\": \"s3cure!\"}' \\n# Output: {\"token\": \"eyJhbG...\", \"expires_in\": 3600}\\n```\\n\\n**Response** (200 OK):\\n\\n```json\\n{\\n  \"token\": \"eyJhbGciOiJIUzI1NiIs...\",\\n  \"expires_in\": 3600,\\n  \"refresh_token\": \"dGhpcyBpcyBh...\"\\n}\\n```\\n\\n**Errors:**\\n- `401 Unauthorized` — Invalid credentials\\n- `429 Too Many Requests` — Rate limit exceeded (100 req/min per IP). Retry after `Retry-After` header value.\\n\\n**Authentication:** Pass JWT in `Authorization: Bearer <token>` header for all subsequent requests.\\n\\n> **Note:** As of v2.3.0, the `X-API-Key` header auth method is deprecated. Use Bearer tokens instead. See [migration guide](/docs/migrate-to-jwt).\\n\\n## Edge Cases\\n\\n- Accounts locked after 5 failed attempts within 15 minutes\\n- Passwords with unicode characters are supported since v2.1.0\\n- Rate limits reset on a rolling window, not fixed intervals",
        "expected_score_min": 0.85,
        "expected_verdict": "pass",
        "description": "Excellent API doc with all elements present"
    },
    {
        "id": "tech_002",
        "text": "To login just call the login endpoint and pass your email and password. It will return a token. Use that token for other requests. Easy!",
        "expected_score_max": 0.20,
        "expected_verdict": "fail",
        "description": "Minimal docs — no code, no schema, no errors, no versions"
    }
]

benchmarks_path = f"{BASE}/technical_docs/benchmarks"
os.makedirs(benchmarks_path, exist_ok=True)
with open(f"{benchmarks_path}/technical_docs.jsonl", "w") as f:
    for entry in benchmarks_tech:
        f.write(json.dumps(entry) + "\n")
print(f"  ✅ {benchmarks_path}/technical_docs.jsonl")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BATCH 9 — REAL ESTATE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n📦 Batch 9 — Real Estate")

write(f"{BASE}/real_estate/manifest.yaml", """
    name: real_estate
    version: "1.0.0"
    description: >
      Evaluates LLM-generated real estate content for listing quality,
      legal compliance, market accuracy, and client communication standards.
    author: eval-kit
    license: proprietary
    filters:
      - rubric: property_description
        weight: 0.20
        scoring_mode: additive
      - rubric: legal_compliance
        weight: 0.22
        scoring_mode: penalty
      - rubric: market_analysis
        weight: 0.18
        scoring_mode: additive
      - rubric: client_communication
        weight: 0.15
        scoring_mode: additive
      - rubric: listing_accuracy
        weight: 0.13
        scoring_mode: penalty
      - rubric: neighborhood_detail
        weight: 0.12
        scoring_mode: additive
    thresholds:
      pass: 0.76
      partial: 0.50
      fail: 0.0
""")

write(f"{BASE}/real_estate/property_description.yaml", """
    name: property_description
    description: >
      Evaluates quality of property listing descriptions including
      sensory language, feature highlighting, and buyer appeal.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: sensory_language
        description: Uses visual, tactile, or spatial language
        patterns:
          - "\\\\b(sun-drenched|open-concept|vaulted|hardwood|granite|stainless)\\\\b"
          - "\\\\b(natural light|panoramic|lush|manicured|spacious|cozy)\\\\b"
        score: 0.20
        severity: medium
        message: "Uses sensory and evocative language"

      - id: room_by_room
        description: Describes individual rooms or spaces
        patterns:
          - "\\\\b(kitchen|bedroom|bathroom|living room|dining|office|garage)\\\\b"
          - "\\\\b(primary suite|en-suite|walk-in|mudroom|laundry|basement)\\\\b"
        score: 0.20
        severity: high
        message: "Provides room-by-room description"

      - id: dimensions_specs
        description: Includes specific measurements or counts
        patterns:
          - "\\\\b(\\\\d+[,.]?\\\\d* (sq|square) (ft|feet)|\\\\d+ bed|\\\\d+ bath)\\\\b"
          - "\\\\b(\\\\d+-car garage|\\\\d+ acre|lot size|built in \\\\d{4})\\\\b"
        score: 0.20
        severity: high
        message: "Includes specific dimensions and counts"

      - id: lifestyle_framing
        description: Frames features as lifestyle benefits
        patterns:
          - "\\\\b(entertain|morning coffee|family|retreat|unwind|host)\\\\b"
          - "\\\\b(perfect for|ideal for|imagine|picture yourself)\\\\b"
        score: 0.20
        severity: medium
        message: "Frames features as lifestyle benefits"

      - id: recent_updates
        description: Mentions renovations, upgrades, or new systems
        patterns:
          - "\\\\b(recently (renovated|updated|replaced)|new (roof|HVAC|windows))\\\\b"
          - "\\\\b(upgraded|remodeled|custom|brand new|\\\\d{4} renovation)\\\\b"
        score: 0.20
        severity: medium
        message: "Highlights recent updates or renovations"
    strengths:
      - pattern: "\\\\b(sq ft|acre|built in \\\\d{4}|renovated)\\\\b"
        label: "Specific, factual property details"
""")

write(f"{BASE}/real_estate/legal_compliance.yaml", """
    name: legal_compliance
    description: >
      Detects Fair Housing Act violations, steering language,
      and discriminatory phrasing in real estate content.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: familial_status
        description: Flags language discriminating based on family status
        patterns:
          - "\\\\b(no children|adults only|perfect for (singles|couples)|not suitable for families)\\\\b"
          - "\\\\b(no kids|child-free|mature (residents|community))\\\\b"
        penalty: 0.25
        severity: critical
        message: "Familial status discrimination — Fair Housing Act violation"

      - id: racial_steering
        description: Detects racial or ethnic characterization of neighborhoods
        patterns:
          - "\\\\b(ethnic|diverse neighborhood|changing area|urban feel)\\\\b"
          - "\\\\b(good neighbors|safe (neighborhood|area|community))\\\\b"
        penalty: 0.20
        severity: critical
        message: "Possible steering language — Fair Housing concern"

      - id: religious_markers
        description: Flags religious community characterization
        patterns:
          - "\\\\b(christian|muslim|jewish|church|mosque|synagogue|temple) (community|neighborhood|area)\\\\b"
        penalty: 0.20
        severity: critical
        message: "Religious characterization of area — Fair Housing violation"

      - id: disability_exclusion
        description: Detects language excluding persons with disabilities
        patterns:
          - "\\\\b(no wheelchair|must (climb|walk)|able-bodied|handicap(?!ped accessible))\\\\b"
        penalty: 0.20
        severity: critical
        message: "Disability-exclusionary language"

      - id: gender_preference
        description: Flags gender-based preferences
        patterns:
          - "\\\\b(bachelor pad|man cave|woman's touch|ladies|gentlemen)\\\\b"
        penalty: 0.10
        severity: medium
        message: "Gender-suggestive language in listing"

      - id: national_origin
        description: Detects national origin references
        patterns:
          - "\\\\b(american-born|english.speaking (neighborhood|area)|immigrant)\\\\b"
          - "\\\\b(foreign|speaks english|citizen(s| only))\\\\b"
        penalty: 0.20
        severity: critical
        message: "National origin reference — Fair Housing violation"
    strengths:
      - pattern: "\\\\b(equal (housing|opportunity)|fair housing|accessible|ADA)\\\\b"
        label: "Fair Housing compliant language"
""")

write(f"{BASE}/real_estate/market_analysis.yaml", """
    name: market_analysis
    description: >
      Evaluates market analysis content for data-driven insights,
      trend identification, and comparative market positioning.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: price_data
        description: Includes specific pricing data or comparisons
        patterns:
          - "\\\\b(\\\\$\\\\d+[,.]?\\\\d*|price per sq|median price|average price)\\\\b"
          - "\\\\b(list price|sold for|asking price|assessed at)\\\\b"
        score: 0.25
        severity: high
        message: "Includes specific pricing data"

      - id: comparable_sales
        description: References comparable recent sales
        patterns:
          - "\\\\b(comp(arable)?s?|recently sold|similar (home|property)|nearby sale)\\\\b"
          - "\\\\b(sold (in|on|within)|closed at|comparable at)\\\\b"
        score: 0.20
        severity: high
        message: "References comparable sales"

      - id: market_trend
        description: Identifies market direction or trend
        patterns:
          - "\\\\b(market (trend|is|has)|appreciation|depreciation|inventory)\\\\b"
          - "\\\\b(buyer's market|seller's market|days on market|DOM)\\\\b"
        score: 0.20
        severity: medium
        message: "Identifies market trends"

      - id: time_context
        description: Grounds analysis in specific time period
        patterns:
          - "\\\\b(Q[1-4] \\\\d{4}|last (month|quarter|year)|year-over-year|YOY)\\\\b"
          - "\\\\b(since (January|February|March|April|May|June|July|August|September|October|November|December))\\\\b"
        score: 0.20
        severity: medium
        message: "Time-specific market analysis"

      - id: data_source
        description: Cites data source or MLS
        patterns:
          - "\\\\b(MLS|Zillow|Redfin|Realtor\\\\.com|county records|tax records)\\\\b"
          - "\\\\b(according to|data from|source:|per the)\\\\b"
        score: 0.15
        severity: medium
        message: "Cites data source"
    strengths:
      - pattern: "\\\\b(MLS|comp|median|DOM|year-over-year)\\\\b"
        label: "Data-driven market analysis"
""")

write(f"{BASE}/real_estate/client_communication.yaml", """
    name: client_communication
    description: >
      Evaluates agent-to-client communication for professionalism,
      clarity, expectation setting, and responsiveness cues.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: personalization
        description: Addresses client by name or references their specific needs
        patterns:
          - "\\\\b(you mentioned|based on your|your (criteria|budget|timeline|needs))\\\\b"
          - "\\\\b(as we discussed|per your request|you were looking for)\\\\b"
        score: 0.25
        severity: high
        message: "Personalized to client's specific needs"

      - id: expectation_setting
        description: Sets clear expectations for process or timeline
        patterns:
          - "\\\\b(expect|timeline|typically takes|next (step|steps)|you can anticipate)\\\\b"
          - "\\\\b(within \\\\d+|by (Monday|Friday|next week)|process (is|takes))\\\\b"
        score: 0.20
        severity: medium
        message: "Sets clear expectations"

      - id: market_education
        description: Educates client on market conditions relevant to their decision
        patterns:
          - "\\\\b(in this market|current(ly)?|given the|inventory is)\\\\b"
          - "\\\\b(what this means for you|impact on your|strategy)\\\\b"
        score: 0.20
        severity: medium
        message: "Educates client on market context"

      - id: professional_tone
        description: Maintains professional, warm tone
        patterns:
          - "\\\\b(happy to|glad to|I'd recommend|let me know|don't hesitate)\\\\b"
          - "\\\\b(thank you|appreciate|looking forward|my pleasure)\\\\b"
        score: 0.15
        severity: low
        message: "Professional, approachable tone"

      - id: call_to_action
        description: Ends with clear next step or action
        patterns:
          - "\\\\b(shall I|would you like (to|me)|let's schedule|I'll send)\\\\b"
          - "\\\\b(call me at|available (Monday|this week|anytime))\\\\b"
        score: 0.20
        severity: medium
        message: "Includes clear call to action"
    strengths:
      - pattern: "\\\\b(you mentioned|your criteria|based on our)\\\\b"
        label: "Client-focused communication"
""")

write(f"{BASE}/real_estate/listing_accuracy.yaml", """
    name: listing_accuracy
    description: >
      Detects exaggerated, misleading, or unverifiable claims
      in property listings that could create legal exposure.
    version: "1.0.0"
    scoring_mode: penalty
    checks:
      - id: superlative_abuse
        description: Flags unsubstantiated superlatives
        patterns:
          - "\\\\b(best|most (beautiful|amazing|stunning)|one of a kind|like no other)\\\\b"
          - "\\\\b(unbelievable|incredible|once in a lifetime|dream home)\\\\b"
        penalty: 0.10
        severity: low
        message: "Unsubstantiated superlative — use specific features instead"

      - id: income_claims
        description: Flags unverified investment or income claims
        patterns:
          - "\\\\b(guaranteed (income|return|rental)|will (appreciate|increase))\\\\b"
          - "\\\\b(cash cow|money maker|passive income guaranteed)\\\\b"
        penalty: 0.20
        severity: high
        message: "Unverifiable financial claim in listing"

      - id: size_misrepresentation
        description: Detects vague size language that could mislead
        patterns:
          - "\\\\b(feels larger|deceptively spacious|bigger than it looks)\\\\b"
          - "\\\\b(generous|ample) (space|room|size)\\\\b"
        penalty: 0.10
        severity: medium
        message: "Vague size language — use actual measurements"

      - id: condition_hedging
        description: Flags condition language that hides problems
        patterns:
          - "\\\\b(as-is|handyman special|investor special|needs (TLC|love|work))\\\\b"
          - "\\\\b(bring your (vision|imagination|contractor))\\\\b"
        penalty: 0.05
        severity: low
        message: "Condition hedging language — be specific about repairs needed"

      - id: school_claims
        description: Flags school quality claims (Fair Housing sensitive)
        patterns:
          - "\\\\b(best schools|top-rated school|school district is)\\\\b"
        penalty: 0.10
        severity: medium
        message: "School quality claims — cite source (GreatSchools, Niche) or remove"
    strengths:
      - pattern: "\\\\b(\\\\d+ sq ft|built in \\\\d{4}|per county records)\\\\b"
        label: "Factual, verifiable listing claims"
""")

write(f"{BASE}/real_estate/neighborhood_detail.yaml", """
    name: neighborhood_detail
    description: >
      Evaluates neighborhood descriptions for walkability info,
      amenity proximity, commute data, and lifestyle context.
    version: "1.0.0"
    scoring_mode: additive
    checks:
      - id: proximity_amenities
        description: Lists nearby amenities with specifics
        patterns:
          - "\\\\b(minutes (from|to)|walking distance|steps from|blocks from)\\\\b"
          - "\\\\b(grocery|restaurant|park|school|hospital|gym|coffee)\\\\b"
        score: 0.25
        severity: high
        message: "Lists nearby amenities with proximity"

      - id: commute_info
        description: Includes commute or transportation details
        patterns:
          - "\\\\b(commute|highway|interstate|transit|bus|train|metro|freeway)\\\\b"
          - "\\\\b(\\\\d+ minute (drive|commute|walk)|easy access to)\\\\b"
        score: 0.20
        severity: medium
        message: "Includes commute and transportation info"

      - id: walkability
        description: References walkability or bike-friendliness
        patterns:
          - "\\\\b(walkable|walk score|bike (friendly|lane|path)|pedestrian)\\\\b"
          - "\\\\b(sidewalk|trail|greenway|bike score)\\\\b"
        score: 0.15
        severity: low
        message: "References walkability or bike access"

      - id: named_locations
        description: Uses specific location names, not just generic descriptors
        patterns:
          - "\\\\b[A-Z][a-z]+ (Park|Square|Mall|Center|District|Village|Station)\\\\b"
        score: 0.20
        severity: medium
        message: "References specific named locations"

      - id: lifestyle_context
        description: Paints a lifestyle picture of the neighborhood
        patterns:
          - "\\\\b(vibrant|quiet|family-friendly|up-and-coming|established)\\\\b"
          - "\\\\b(farmers market|nightlife|outdoor|community events|local)\\\\b"
        score: 0.20
        severity: medium
        message: "Provides neighborhood lifestyle context"
    strengths:
      - pattern: "\\\\b(walk score|\\\\d+ minute|named (park|square|center))\\\\b"
        label: "Specific, navigable neighborhood info"
""")

# Real estate benchmarks
benchmarks_re = [
    {
        "id": "re_001",
        "text": "Welcome to 742 Elmwood Drive — a beautifully renovated 4-bedroom, 3.5-bathroom Colonial nestled on 0.6 acres in the heart of Maplewood's sought-after Jefferson Park neighborhood. Built in 1928 and thoughtfully updated in a 2023 renovation, this 2,850 sq ft home blends period charm with modern function. Step through the original arched doorway into a sun-drenched living room with refinished oak hardwood floors, a restored gas fireplace, and 9-foot ceilings. The open-concept kitchen features quartz countertops, a 48-inch Wolf range, custom shaker cabinetry, and a center island that seats four — perfect for hosting while the kids do homework at the built-in desk nook. The primary suite on the second floor offers a walk-in closet with custom organizers and an en-suite bathroom with heated tile floors, a frameless glass rain shower, and double vanity. Three additional bedrooms share an updated full bath with subway tile and brushed nickel fixtures. The finished basement adds 600 sq ft of flex space — currently configured as a home office and playroom. New roof (2022), new HVAC (2023), and updated 200-amp electrical panel. The backyard features a bluestone patio, mature maple trees, and a fenced perimeter. Located 8 minutes from Maplewood Village with its coffee shops, restaurants, and weekend farmers market. NJ Transit's Maplewood station is a 12-minute walk — 45 minutes to Penn Station. Jefferson Elementary (rated 9/10 on GreatSchools) is three blocks away. Equal Housing Opportunity. Listed at $875,000. Contact Sarah Mitchell at 973-555-0142 or sarah@mitchellrealty.com to schedule a private showing.",
        "expected_score_min": 0.85,
        "expected_verdict": "pass",
        "description": "Excellent listing with specs, sensory detail, legal compliance, neighborhood"
    },
    {
        "id": "re_002",
        "text": "Amazing dream home in a safe neighborhood with the best schools! This incredible once-in-a-lifetime opportunity won't last. Perfect for a young Christian family. No kids under 12 in the building. Must be able to walk up 3 flights. Guaranteed rental income of $3000/month if used as investment. Feels way bigger than it looks!",
        "expected_score_max": 0.20,
        "expected_verdict": "fail",
        "description": "Listing filled with Fair Housing violations, superlatives, and false claims"
    }
]

benchmarks_path = f"{BASE}/real_estate/benchmarks"
os.makedirs(benchmarks_path, exist_ok=True)
with open(f"{benchmarks_path}/real_estate.jsonl", "w") as f:
    for entry in benchmarks_re:
        f.write(json.dumps(entry) + "\n")
print(f"  ✅ {benchmarks_path}/real_estate.jsonl")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GUMROAD PRODUCT COPY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
print("\n📝 Gumroad product copy")

gumroad_copy = {
    "hr_compliance": {
        "title": "eval-kit: HR Compliance Rubric Pack",
        "price": "$29",
        "tagline": "Stop your AI from writing you into a lawsuit.",
        "description": """Your HR chatbot just told an employee their position is "guaranteed" and referenced someone's medical diagnosis in a group email. That's an implied contract violation and a HIPAA breach — before lunch.

This rubric pack catches what your legal team would catch, but before it reaches anyone's inbox.

**What's inside:**

- **Bias Detection** — Flags gendered, racial, age-based, and ableist language that triggers EEOC complaints. Catches "digital native" (age), "culture fit" (racial proxy), and "chairman" (gendered) before they ship.
- **Legal Language** — Detects implied contract language ("guaranteed position"), liability admissions ("our fault"), retaliation phrasing, and HIPAA-adjacent PHI disclosure.
- **Policy Adherence** — Ensures responses reference handbook sections, include escalation paths, specify timelines, and direct employees to document interactions.
- **Accommodation Compliance** — Validates ADA/FMLA interactive process language, reasonable accommodation offers, confidentiality assurances, and medical documentation requests.
- **Termination Protocol** — Catches emotional language in termination docs, discriminatory timing references, and missing factual basis. Checks for COBRA info, separation agreement mention, and documented PIP references.
- **Documentation Standards** — Verifies professional tone, action items, contact information, date-stamping, and proper sign-off formatting.

**Also includes:**
- 4 benchmark scenarios with expected score ranges for validation
- Instant integration with eval-kit CLI: `eval-kit --pack hr_compliance --file responses.jsonl`

**Who needs this:**
- Teams deploying AI for internal HR communications
- HR tech startups building chatbots for employee self-service
- Compliance teams auditing LLM outputs before deployment
- Anyone whose AI writes things a lawyer would read"""
    },
    "sales_enablement": {
        "title": "eval-kit: Sales Enablement Rubric Pack",
        "price": "$29",
        "tagline": "Your AI sales rep should close deals, not kill them.",
        "description": """Your AI just sent a follow-up that said "just checking in to see if you had any thoughts." That email got deleted before the prospect finished the subject line.

This rubric pack ensures every AI-generated sales communication actually sells.

**What's inside:**

- **Objection Handling** — Scores acknowledgment, reframing technique, social proof usage, metric specificity, and bridge-to-next-step transitions. Your AI won't just hear objections — it'll handle them.
- **Value Proposition** — Checks for outcome-focused framing (not feature lists), quantified benefits, pain-point alignment, competitive differentiation, and risk-reduction language.
- **Urgency Creation** — Evaluates ethical urgency tactics: time-bound offers, cost-of-inaction framing, scarcity signals, momentum language, and peer movement references.
- **Competitor Positioning** — Ensures professional contrast over trash-talking. Checks for strength-based positioning, use-case fit, migration ease messaging, and honest limitation acknowledgment.
- **Closing Technique** — Scores clear asks, assumed closes, two-option framing, calendar-specific next steps, and low-commitment entry points.
- **Rapport Building** — Validates personalization, empathy signals, name usage, shared context, and genuine curiosity about prospect goals.

**Also includes:**
- 2 benchmark scenarios (strong email vs. lazy follow-up) with expected scores
- Works instantly: `eval-kit --pack sales_enablement --file outreach.jsonl`

**Who needs this:**
- SDR/BDR teams using AI for outreach and follow-up
- Sales enablement platforms with AI-generated playbooks
- Revenue ops teams auditing AI email quality at scale
- Founders who want their AI to sell like their best rep, not their worst"""
    },
    "technical_docs": {
        "title": "eval-kit: Technical Documentation Rubric Pack",
        "price": "$29",
        "tagline": "If your AI writes docs nobody can follow, nobody will use your product.",
        "description": """Your AI-generated API docs say "just call the endpoint and pass your credentials." That's not documentation. That's a Stack Overflow comment from 2014.

This rubric pack ensures AI-generated technical content is actually useful to developers.

**What's inside:**

- **Accuracy** — Catches deprecated syntax (componentWillMount, document.write), security anti-patterns (chmod 777, verify=False), version mismatches, incorrect defaults, and unsupported absolute claims.
- **Completeness** — Checks for prerequisites, parameter documentation with types, return value specs, error handling coverage, and edge case acknowledgment.
- **Code Examples** — Scores formatted code blocks, language specification, inline comments, expected output display, import inclusion, and copy-paste runnability.
- **Readability** — Evaluates header structure, paragraph length, list usage, jargon definitions, transition signals, and TL;DR/quick-start sections.
- **Versioning** — Checks for specific version references, changelog pointers, deprecation notices, migration guidance, and compatibility matrices.
- **API Reference** — Validates endpoint format with HTTP methods, request/response schemas, authentication details, rate limit disclosure, and curl examples.

**Also includes:**
- 2 benchmark scenarios (comprehensive API doc vs. lazy one-liner) with expected scores
- Drop-in usage: `eval-kit --pack technical_docs --file generated_docs.jsonl`

**Who needs this:**
- DevTool companies using AI to generate or assist documentation
- API platforms auto-generating endpoint references
- Technical writing teams auditing AI draft quality
- Any team where "the AI wrote the docs" needs to mean "the docs are actually good" """
    },
    "real_estate": {
        "title": "eval-kit: Real Estate Rubric Pack",
        "price": "$29",
        "tagline": "Your AI listing just violated the Fair Housing Act. Fix that.",
        "description": """Your AI wrote "perfect for a young Christian family" in a property listing. That's religious discrimination AND familial status discrimination in eight words. The fine starts at $16,000.

This rubric pack catches Fair Housing violations and listing quality issues before they go live.

**What's inside:**

- **Property Description** — Scores sensory language, room-by-room detail, specific dimensions, lifestyle framing, and renovation/upgrade mentions. No more "nice 3BR."
- **Legal Compliance** — Flags familial status discrimination, racial steering language, religious characterization, disability exclusion, gender preferences, and national origin references. Built from actual Fair Housing Act case law patterns.
- **Market Analysis** — Checks for specific pricing data, comparable sales references, market trend identification, time-period grounding, and data source citation.
- **Client Communication** — Validates personalization, expectation setting, market education, professional tone, and clear calls to action.
- **Listing Accuracy** — Penalizes superlative abuse ("dream home"), unverified income claims, vague size language, condition hedging, and unsourced school quality claims.
- **Neighborhood Detail** — Scores amenity proximity with specifics, commute data, walkability references, named locations, and lifestyle context.

**Also includes:**
- 2 benchmark scenarios (strong listing vs. violation-filled disaster) with expected scores
- Immediate use: `eval-kit --pack real_estate --file listings.jsonl`

**Who needs this:**
- Real estate platforms with AI listing generators
- Brokerages deploying chatbots for client communication
- PropTech startups automating CMA reports or listing descriptions
- Any agent using AI who doesn't want a $100K Fair Housing fine"""
    }
}

gumroad_path = os.path.expanduser("~/Desktop/ai_hustle/eval-kit/marketing")
os.makedirs(gumroad_path, exist_ok=True)

for pack_name, copy in gumroad_copy.items():
    filepath = f"{gumroad_path}/{pack_name}_gumroad.md"
    with open(filepath, "w") as f:
        f.write(f"# {copy['title']}\n\n")
        f.write(f"**Price:** {copy['price']}\n\n")
        f.write(f"*{copy['tagline']}*\n\n")
        f.write(copy['description'])
        f.write("\n")
    print(f"  ✅ {filepath}")

print("\n✅ All 4 premium packs created!")
print("   📦 hr_compliance — 6 rubrics + benchmarks")
print("   📦 sales_enablement — 6 rubrics + benchmarks")
print("   📦 technical_docs — 6 rubrics + benchmarks")
print("   📦 real_estate — 6 rubrics + benchmarks")
print("   📝 4 Gumroad product pages in /marketing/")
print("\n🚀 Run: python setup_premium_packs.py")