# src/narrative/prompts.py

"""
PROMPT TEMPLATES FOR REPORT GENERATION — V2
────────────────────────────────────────────
Updated to work with domain-aware analysis (V2 descriptive.py).

CHANGES FROM V1:
1. SYSTEM_PROMPT enforces domain vocabulary rules
2. KPI section prompt includes group-by analyses + derived metrics
3. Recommendations prompt includes domain-specific performer data
4. All prompts reference domain context for correct terminology

PROMPT ENGINEERING TECHNIQUES:
- Role assignment ("You are a senior analyst...")
- Domain vocabulary enforcement (NEVER say "revenue" for healthcare)
- Chain-of-thought (analyze → interpret → recommend)
- Output format specs (markdown, headers, bold)
- Guardrails (cite data only, no hallucination)
"""


# ═══════════════════════════════════════════════════════════
# SYSTEM PROMPTS
# ═══════════════════════════════════════════════════════════

SYSTEM_PROMPT_BASE = """You are a senior business intelligence analyst at a top consulting firm.
You write clear, insightful, and actionable business reports.

WRITING PRINCIPLES:
1. DATA-DRIVEN: Always cite specific numbers from the provided data. Never invent statistics.
2. INSIGHTFUL: Don't just describe what happened — explain WHY it matters and WHAT to do about it.
3. ACTIONABLE: Every section should end with a clear implication or next step.
4. PROFESSIONAL: Write in executive-ready language suitable for C-suite presentation.
5. CONCISE: Every sentence must add value. No filler phrases like "it is important to note that."
6. STRUCTURED: Use clear headers, bullet points, and bold text for key metrics.

STRICT RULES:
- ONLY reference numbers that exist in the provided data
- NEVER fabricate statistics or percentages
- If data is insufficient for a conclusion, say so explicitly
- Use **bold** for key metrics and numbers
- Use bullet points for lists of 3+ items
- ALWAYS follow the TERMINOLOGY RULES provided in the domain context section
- If the domain context says "NEVER use these words" — absolutely DO NOT use them
- If the domain says entities are "patients", call them "patients" not "customers"
- If the domain says entities are "employees", call them "employees" not "transactions"
- Match the primary metric name to the domain (headcount for HR, patient count for healthcare, revenue for sales)
- Do NOT assume all data is sales/revenue data — read the domain context carefully"""


TONE_INSTRUCTIONS = {
    "executive": """
TONE: C-SUITE EXECUTIVE
- Ultra-concise: Get to the point in the first sentence
- Focus on strategic implications, not operational details
- Lead with the most impactful insight
- Use phrases like "bottom line," "strategic priority," "key takeaway"
- Numbers should be rounded for quick comprehension ($1.2M, not $1,234,567.89)
- Include forward-looking statements and risk callouts
- Maximum 150-200 words per section""",

    "manager": """
TONE: DEPARTMENT MANAGER
- Balance between strategic and operational detail
- Include specific action items with clear ownership
- Reference both high-level trends and notable specifics
- Use phrases like "action required," "key driver," "area of concern"
- Numbers can be moderately detailed ($1.23M or $1,234K)
- Include comparative context (vs last month, vs target)
- Maximum 200-300 words per section""",

    "analyst": """
TONE: DATA ANALYST
- Detailed and thorough analysis
- Include statistical context (standard deviations, distributions, confidence)
- Reference methodology when relevant
- Use precise numbers ($1,234,567.89)
- Include caveats and data quality notes
- Discuss correlations and potential confounding factors
- Maximum 300-400 words per section""",
}


# ═══════════════════════════════════════════════════════════
# SECTION PROMPTS
# ═══════════════════════════════════════════════════════════

EXECUTIVE_SUMMARY_PROMPT = """Write an Executive Summary for a business report based on the data analysis below.

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

REPORT PERIOD: {report_period}

KEY METRICS (KPIs):
{kpis_text}

TREND ANALYSIS:
{trends_text}

ANOMALY ALERTS:
{anomalies_text}

TOP/BOTTOM PERFORMERS:
{performers_text}

INSTRUCTIONS:
1. Start with ONE powerful opening sentence that captures the overall performance
   — use the CORRECT domain terminology (e.g., "patient admissions" not "revenue" for healthcare)
2. Highlight the 2-3 MOST important KPIs with their values
3. Summarize the overall trend direction and growth rate
4. Flag any critical anomalies or risks (if any)
5. End with a 1-sentence forward-looking statement

FORMAT: Use markdown. Bold key numbers. Keep to {word_limit} words.

{tone_instruction}"""


KPIS_SECTION_PROMPT = """Write a "Key Performance Indicators" section analyzing the following metrics.

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

KPI DATA:
{kpis_text}

DETAILED ANALYSES & BREAKDOWNS:
{breakdown_text}

INSTRUCTIONS:
1. Present the most important KPIs in a logical order
2. For each KPI, don't just state the number — provide CONTEXT
   (Is this good or bad? How does it compare to typical benchmarks?)
3. Highlight the relationship between KPIs
   For example:
   - Healthcare: "The average length of stay of X days combined with Y average cost suggests..."
   - HR: "Despite a headcount of X, the attrition rate of Y% indicates talent retention challenges..."
   - Sales: "Despite high revenue, the profit margin of X% suggests cost pressure..."
4. Reference the group-by breakdowns to show which segments perform best/worst
5. Include any derived metrics or cross-tabulation insights
6. Call out any KPI that seems unusual or concerning
7. End with a 1-2 sentence overall assessment

FORMAT: Use markdown with bullet points. Bold KPI values.

{tone_instruction}"""


TREND_ANALYSIS_PROMPT = """Write a "Trend Analysis" section based on the following time-series analysis.

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

OVERALL TREND:
{overall_trend_text}

GROWTH ANALYSIS:
{growth_text}

PERIOD COMPARISON (Current vs Previous):
{comparison_text}

BEST/WORST PERIODS:
{best_worst_text}

MOMENTUM:
{momentum_text}

SEASONALITY:
{seasonality_text}

SECONDARY METRICS TRENDS:
{secondary_trends_text}

INSTRUCTIONS:
1. Lead with the overall trend direction and its strength
   — use domain-appropriate language (e.g., "admissions trending upward" for healthcare)
2. Discuss growth rates — both recent and average
3. Compare current period to previous period
4. Highlight best and worst performing periods with hypotheses for WHY
5. Discuss momentum — is growth accelerating or slowing?
6. Mention seasonality if detected — what does it mean for planning?
7. Briefly mention secondary metric trends if relevant
8. End with a forward-looking prediction or concern

FORMAT: Use markdown headers (###) for sub-sections. Bold key growth numbers.

{tone_instruction}"""


ANOMALY_ALERTS_PROMPT = """Write a "Key Observations & Alerts" section based on detected anomalies.

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

STATISTICAL OUTLIERS:
{column_anomalies_text}

TIME-BASED SPIKES:
{time_anomalies_text}

BUSINESS RULE ALERTS:
{business_alerts_text}

OVERALL SEVERITY: {overall_severity}

INSTRUCTIONS:
1. Start with the overall data quality / anomaly assessment
2. For EACH significant anomaly:
   - What was detected (be specific with numbers)
   - Why it matters for THIS SPECIFIC DOMAIN
     (e.g., healthcare: "unusually high treatment cost may indicate billing errors"
      vs. sales: "revenue spike may indicate a bulk order")
   - Recommended action (investigate? ignore? fix?)
3. Prioritize: Critical issues first, then warnings, then informational
4. Use these severity indicators:
   🔴 CRITICAL — needs immediate attention
   🟠 HIGH — investigate within this week
   🟡 MEDIUM — monitor going forward
   🟢 LOW — likely normal variation
5. If no significant anomalies, state that data quality is good
6. End with an overall data quality assessment

FORMAT: Use markdown. Use emoji severity indicators. Bold the anomaly values.

{tone_instruction}"""


RECOMMENDATIONS_PROMPT = """Write a "Strategic Recommendations" section based on ALL the analysis below.

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

FULL ANALYSIS SUMMARY:
- KPIs: {kpis_summary}
- Trend: {trend_summary}
- Anomalies: {anomaly_summary}
- Top Performers: {top_performers_summary}
- Detailed Breakdowns: {detailed_breakdowns}

INSTRUCTIONS:
1. Provide 4-6 specific, actionable recommendations
2. EVERY recommendation must be relevant to this SPECIFIC DOMAIN:
   - Healthcare: focus on patient outcomes, cost management, department efficiency
   - HR: focus on retention, compensation equity, workforce planning
   - Sales: focus on revenue growth, margin improvement, customer expansion
   - Marketing: focus on ROAS, channel optimization, conversion improvement
   - Operations: focus on lead time reduction, supplier management, cost efficiency
3. Structure each recommendation as:
   **[Priority] Recommendation Title**
   - What: Specific action to take
   - Why: Data point that supports this recommendation
   - Expected Impact: What will improve if this is done
4. Prioritize recommendations:
   🔴 URGENT (do this week)
   🟡 IMPORTANT (do this month)
   🟢 STRATEGIC (plan for next quarter)
5. Recommendations MUST be grounded in the actual data provided
6. Include at least one "quick win" and one "strategic initiative"
7. If applicable, suggest what data to track going forward

FORMAT: Numbered list with bold headers. Include priority tags.

{tone_instruction}"""


FULL_REPORT_PROMPT = """Generate a complete business intelligence report based on the following analysis.

REPORT METADATA:
- Title: {title}
- Period: {period}
- Generated: {generated_date}
- Domain: {domain_name}

DOMAIN CONTEXT (READ CAREFULLY — follow terminology rules):
{domain_context}

DATA PROFILE:
{data_profile}

KPIs:
{kpis_text}

GROUP-BY ANALYSES:
{group_by_text}

CROSS-TABULATIONS:
{cross_tabs_text}

DERIVED METRICS:
{derived_metrics_text}

TREND ANALYSIS:
{trends_text}

ANOMALIES:
{anomalies_text}

TOP/BOTTOM PERFORMERS:
{performers_text}

INCLUDE THESE SECTIONS (in order):
1. ## Executive Summary (150 words)
2. ## Key Performance Indicators (200 words)
3. ## Trend Analysis (250 words)
4. ## Key Observations & Alerts (150 words)
5. ## Recommendations (200 words)
6. ## Methodology Note (50 words — briefly mention AI-assisted analysis)

TOTAL TARGET: 800-1200 words

STRICT RULES:
- Only use numbers from the data provided above
- Use CORRECT domain terminology throughout (see DOMAIN CONTEXT)
- Start each section with ## header
- Use **bold** for important numbers
- Use bullet points for lists
- Make it flow as a cohesive narrative, not disjointed sections
- End the report on a forward-looking note

{tone_instruction}"""