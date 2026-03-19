# src/narrative/narrator.py

"""
REPORT NARRATOR — V2 (DOMAIN-AWARE)
────────────────────────────────────
Converts raw analysis data into narrative report sections.

CHANGES FROM V1:
1. _prepare_data_texts() reads NEW V2 descriptive format
   (group_by_analyses, cross_tabs, derived_metrics)
2. _get_domain_context() injects domain vocabulary rules
   (prevents calling patients "customers" etc.)
3. Section generators pass domain-specific data
4. Full report mode includes all new data sections

TWO MODES:
1. Section-by-Section: Better quality, shows progress
2. Full Report: Faster, one API call
"""

import json
from datetime import datetime
from typing import Dict, Optional, List
from src.utils.llm_client import llm
from src.analysis.domain_config import get_domain_config
from src.narrative.prompts import (
    SYSTEM_PROMPT_BASE,
    TONE_INSTRUCTIONS,
    EXECUTIVE_SUMMARY_PROMPT,
    KPIS_SECTION_PROMPT,
    TREND_ANALYSIS_PROMPT,
    ANOMALY_ALERTS_PROMPT,
    RECOMMENDATIONS_PROMPT,
    FULL_REPORT_PROMPT,
)
from src.utils.logger import logger


class ReportNarrator:
    """
    Orchestrates LLM calls to generate narrative report sections.

    Usage:
        narrator = ReportNarrator(tone="executive")

        # Section by section
        sections = narrator.generate_section_by_section(analysis_bundle)

        # Or full report
        report = narrator.generate_full_report(analysis_bundle)
    """

    def __init__(self, tone: str = "executive"):
        """
        Parameters:
        -----------
        tone : str
            'executive' — C-suite level, concise, strategic
            'manager' — balanced, actionable, moderate detail
            'analyst' — detailed, technical, thorough
        """

        self.tone = tone
        self.tone_instruction = TONE_INSTRUCTIONS.get(
            tone, TONE_INSTRUCTIONS["executive"]
        )

        # Word limits per tone
        self.word_limits = {
            "executive": 150,
            "manager": 250,
            "analyst": 350,
        }
        self.word_limit = self.word_limits.get(tone, 200)

        logger.info(f"ReportNarrator initialized with tone: {tone}")


    # ═══════════════════════════════════════════════════════
    # PUBLIC METHODS
    # ═══════════════════════════════════════════════════════

    def generate_section_by_section(self,
                                     analysis_bundle: Dict,
                                     progress_callback=None) -> Dict[str, str]:
        """
        Generate each report section independently.

        Parameters:
        -----------
        analysis_bundle : Dict
            All analysis results from previous modules
        progress_callback : callable, optional
            Function to call with progress updates
            Signature: callback(section_name: str, status: str)

        Returns:
        --------
        Dict[str, str] : {section_name: generated_text}
        """

        logger.info("Starting section-by-section report generation")

        prepared = self._prepare_data_texts(analysis_bundle)

        sections = {}
        section_generators = [
            ("executive_summary", self._generate_executive_summary),
            ("kpi_analysis", self._generate_kpi_section),
            ("trend_analysis", self._generate_trend_section),
            ("anomalies_alerts", self._generate_anomaly_section),
            ("recommendations", self._generate_recommendations),
        ]

        for section_name, generator_func in section_generators:
            try:
                if progress_callback:
                    progress_callback(section_name, "generating")

                logger.info(f"Generating section: {section_name}")
                content = generator_func(prepared, analysis_bundle)
                sections[section_name] = content

                if progress_callback:
                    progress_callback(section_name, "complete")

                logger.info(f"Section '{section_name}' generated successfully")

            except Exception as e:
                logger.error(f"Failed to generate '{section_name}': {e}")
                sections[section_name] = (
                    f"*[Error generating this section: {str(e)}. "
                    f"Please check your API key and try again.]*"
                )
                if progress_callback:
                    progress_callback(section_name, "error")

        return sections


    def generate_full_report(self, analysis_bundle: Dict,
                              title: str = None) -> str:
        """Generate complete report in one LLM call"""

        logger.info("Generating full report in single call")

        prepared = self._prepare_data_texts(analysis_bundle)
        domain_context = self._get_domain_context(analysis_bundle)

        prompt = FULL_REPORT_PROMPT.format(
            title=title or analysis_bundle.get(
                "report_title", "Business Report"
            ),
            period=analysis_bundle.get("report_period", "Current Period"),
            generated_date=datetime.now().strftime("%B %d, %Y"),
            domain_name=analysis_bundle.get("kpis", {}).get(
                "domain_name", "General"
            ),
            domain_context=domain_context,
            data_profile=prepared["profile"],
            kpis_text=prepared["kpis"],
            group_by_text=prepared["group_by_analyses"],
            cross_tabs_text=prepared["cross_tabs"],
            derived_metrics_text=prepared["derived_metrics"],
            trends_text=prepared["trends"],
            anomalies_text=prepared["anomalies"],
            performers_text=prepared["performers"],
            tone_instruction=self.tone_instruction,
        )

        report = llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.3,
            max_tokens=6000,
        )

        return report


    # ═══════════════════════════════════════════════════════
    # SECTION GENERATORS
    # ═══════════════════════════════════════════════════════

    def _generate_executive_summary(self, prepared: Dict,
                                     bundle: Dict) -> str:
        """Generate Executive Summary"""

        domain_context = self._get_domain_context(bundle)

        prompt = EXECUTIVE_SUMMARY_PROMPT.format(
            domain_context=domain_context,
            report_period=bundle.get("report_period", "Current Period"),
            kpis_text=prepared["kpis"],
            trends_text=prepared["trends_summary"],
            anomalies_text=prepared["anomalies_summary"],
            performers_text=prepared["performers"],
            word_limit=self.word_limit,
            tone_instruction=self.tone_instruction,
        )

        return llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.3,
        )


    def _generate_kpi_section(self, prepared: Dict,
                               bundle: Dict) -> str:
        """Generate KPI Analysis section"""

        domain_context = self._get_domain_context(bundle)

        # Combine all breakdown data into one text block
        breakdown_text = "\n\n".join(filter(None, [
            prepared["group_by_analyses"],
            prepared["breakdowns"],
            prepared["cross_tabs"],
            prepared["derived_metrics"],
        ]))

        prompt = KPIS_SECTION_PROMPT.format(
            domain_context=domain_context,
            kpis_text=prepared["kpis"],
            breakdown_text=breakdown_text,
            tone_instruction=self.tone_instruction,
        )

        return llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.3,
        )


    def _generate_trend_section(self, prepared: Dict,
                                 bundle: Dict) -> str:
        """Generate Trend Analysis section"""

        domain_context = self._get_domain_context(bundle)
        trends = bundle.get("trends", {})

        # Extract sub-components safely
        overall_trend = trends.get("overall_trend", {})
        growth = trends.get("growth_analysis", {})
        comparison = trends.get("period_comparison", {})
        best_worst = trends.get("best_worst_periods", {})
        momentum = trends.get("momentum", {})
        seasonality = trends.get("seasonality", {})
        secondary = trends.get("secondary_trends", {})

        prompt = TREND_ANALYSIS_PROMPT.format(
            domain_context=domain_context,
            overall_trend_text=json.dumps(
                overall_trend, indent=2, default=str
            ),
            growth_text=json.dumps(growth, indent=2, default=str),
            comparison_text=json.dumps(comparison, indent=2, default=str),
            best_worst_text=json.dumps(best_worst, indent=2, default=str),
            momentum_text=json.dumps(momentum, indent=2, default=str),
            seasonality_text=json.dumps(
                seasonality, indent=2, default=str
            ),
            secondary_trends_text=json.dumps(
                secondary, indent=2, default=str
            ),
            tone_instruction=self.tone_instruction,
        )

        return llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.3,
        )


    def _generate_anomaly_section(self, prepared: Dict,
                                   bundle: Dict) -> str:
        """Generate Anomalies & Alerts section"""

        domain_context = self._get_domain_context(bundle)
        anomalies = bundle.get("anomalies", {})

        prompt = ANOMALY_ALERTS_PROMPT.format(
            domain_context=domain_context,
            column_anomalies_text=json.dumps(
                anomalies.get("column_anomalies", {}),
                indent=2, default=str
            ),
            time_anomalies_text=json.dumps(
                anomalies.get("time_anomalies", {}),
                indent=2, default=str
            ),
            business_alerts_text=json.dumps(
                anomalies.get("business_rule_alerts", []),
                indent=2, default=str
            ),
            overall_severity=anomalies.get("summary", {}).get(
                "overall_severity", "unknown"
            ),
            tone_instruction=self.tone_instruction,
        )

        return llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.3,
        )


    def _generate_recommendations(self, prepared: Dict,
                                   bundle: Dict) -> str:
        """Generate Recommendations section"""

        domain_context = self._get_domain_context(bundle)

        prompt = RECOMMENDATIONS_PROMPT.format(
            domain_context=domain_context,
            kpis_summary=prepared["kpis"],
            trend_summary=prepared["trends_summary"],
            anomaly_summary=prepared["anomalies_summary"],
            top_performers_summary=prepared["performers"],
            detailed_breakdowns="\n\n".join(filter(None, [
                prepared["group_by_analyses"],
                prepared["cross_tabs"],
                prepared["derived_metrics"],
            ])),
            tone_instruction=self.tone_instruction,
        )

        return llm.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_BASE,
            temperature=0.5,    # slightly creative for recommendations
        )


    # ═══════════════════════════════════════════════════════
    # DATA PREPARATION (V2 — reads new descriptive format)
    # ═══════════════════════════════════════════════════════

    def _prepare_data_texts(self, bundle: Dict) -> Dict[str, str]:
        """
        Convert analysis results into clean text for prompts.

        UPDATED FOR V2:
        - Reads group_by_analyses (domain-specific groupings)
        - Reads cross_tabs (domain-specific cross-tabulations)
        - Reads derived_metrics (age groups, salary bands, etc.)
        - Reads new top_bottom format (with aggregation type)
        """

        prepared = {}

        # ── Profile ────────────────────────────────────
        profile = bundle.get("profile", {})
        overview = profile.get("overview", {})
        quality = profile.get("quality", {})

        profile_lines = [
            f"Dataset: {overview.get('total_rows', 'N/A'):,} rows × "
            f"{overview.get('total_columns', 'N/A')} columns",
            f"Data Quality: {quality.get('completeness_score', 'N/A')}% "
            f"({quality.get('quality_rating', 'N/A')})",
            f"Missing Values: {quality.get('total_missing_values', 0)}",
        ]

        if profile.get("date_info"):
            di = profile["date_info"]
            profile_lines.append(
                f"Date Range: {di.get('start_date', 'N/A')} "
                f"to {di.get('end_date', 'N/A')} "
                f"({di.get('total_days', 'N/A')} days)"
            )

        prepared["profile"] = "\n".join(profile_lines)

        # ── KPIs ───────────────────────────────────────
        kpis = bundle.get("kpis", {})
        kpi_data = kpis.get("kpis", {})
        kpi_defs = kpis.get("kpi_definitions", [])

        kpi_lines = []
        for kpi_def in kpi_defs:
            key = kpi_def["key"]
            if key in kpi_data:
                value = kpi_data[key]
                try:
                    formatted = kpi_def["format"].format(value)
                except (ValueError, KeyError):
                    formatted = str(value)
                kpi_lines.append(
                    f"- {kpi_def['name']}: {formatted} "
                    f"({kpi_def.get('description', '')})"
                )

        prepared["kpis"] = (
            "\n".join(kpi_lines) if kpi_lines
            else "No KPIs calculated"
        )

        # ── Category Breakdowns (from KPI calculator) ──
        breakdowns = kpis.get("category_breakdown", {})
        breakdown_lines = []

        for cat_name, cat_data in breakdowns.items():
            breakdown_lines.append(
                f"\n{cat_name.replace('_', ' ').title()}:"
            )
            if cat_data.get("insight"):
                breakdown_lines.append(f"  Insight: {cat_data['insight']}")
            for item in cat_data.get("data", [])[:5]:
                pct = f" ({item.get('pct_share', 0)}% share)" if 'pct_share' in item else ""
                breakdown_lines.append(
                    f"  - {item['name']}: {item['total']:,.2f}{pct}"
                )

        prepared["breakdowns"] = (
            "\n".join(breakdown_lines) if breakdown_lines
            else "No breakdowns available"
        )

        # ── Domain Group-By Analyses (V2 NEW) ──────────
        descriptive = bundle.get("descriptive", {})
        group_bys = descriptive.get("group_by_analyses", [])

        gb_lines = []
        for gb in group_bys:
            gb_lines.append(
                f"\n{gb['title']} "
                f"({gb['aggregation'].upper()} of {gb['metric_role']}):"
            )
            if gb.get("insight"):
                gb_lines.append(f"  Insight: {gb['insight']}")
            for item in gb.get("data", [])[:5]:
                pct = (
                    f" ({item['percentage']}%)"
                    if 'percentage' in item else ""
                )
                gb_lines.append(
                    f"  - {item['name']}: {item['value']:,.2f}{pct}"
                )

        prepared["group_by_analyses"] = (
            "\n".join(gb_lines) if gb_lines
            else "No group-by analyses available"
        )

        # ── Cross-Tabs (V2 NEW) ────────────────────────
        cross_tabs = descriptive.get("cross_tabs", [])
        ct_lines = []

        for ct in cross_tabs:
            ct_lines.append(
                f"\n{ct['title']} "
                f"({ct['row_column']} × {ct['col_column']}, "
                f"{ct['aggregation']}):"
            )
            if ct.get("insight"):
                ct_lines.append(f"  Insight: {ct['insight']}")

            # Add table summary for LLM context
            if "table_data" in ct:
                td = ct["table_data"]
                rows = td.get("index", [])
                cols = td.get("columns", [])
                values = td.get("values", [])

                # Format as simple text table
                if rows and cols and values:
                    # Header row
                    col_names = [str(c) for c in cols]
                    ct_lines.append(
                        f"  {'':>15} | " +
                        " | ".join(f"{c:>10}" for c in col_names)
                    )

                    # Data rows (limit to first 5)
                    for i, row_name in enumerate(rows[:5]):
                        if i < len(values):
                            row_vals = values[i]
                            formatted_vals = [
                                f"{v:>10,.0f}" if isinstance(v, (int, float))
                                else f"{str(v):>10}"
                                for v in row_vals
                            ]
                            ct_lines.append(
                                f"  {str(row_name):>15} | " +
                                " | ".join(formatted_vals)
                            )

        prepared["cross_tabs"] = (
            "\n".join(ct_lines) if ct_lines
            else "No cross-tabulations available"
        )

        # ── Derived Metrics (V2 NEW) ───────────────────
        derived = descriptive.get("derived_metrics", {})
        derived_lines = []

        for key, data in derived.items():
            title = data.get("title", key.replace("_", " ").title())
            derived_lines.append(f"\n{title}:")

            if data.get("insight"):
                derived_lines.append(f"  {data['insight']}")

            if isinstance(data.get("data"), dict):
                for k, v in list(data["data"].items())[:8]:
                    derived_lines.append(f"  - {k}: {v}")
            elif isinstance(data.get("data"), list):
                for item in data["data"][:5]:
                    if isinstance(item, dict):
                        summary_parts = []
                        for ik, iv in item.items():
                            if isinstance(iv, float):
                                summary_parts.append(f"{ik}={iv:,.2f}")
                            else:
                                summary_parts.append(f"{ik}={iv}")
                        derived_lines.append(
                            f"  - {', '.join(summary_parts[:4])}"
                        )

            # Additional fields
            if data.get("rate"):
                derived_lines.append(f"  Rate: {data['rate']}%")
            if data.get("left"):
                derived_lines.append(
                    f"  Left: {data['left']}, Stayed: {data.get('stayed', 'N/A')}"
                )

        prepared["derived_metrics"] = (
            "\n".join(derived_lines) if derived_lines
            else "No derived metrics"
        )

        # ── Performers (V2 NEW FORMAT) ─────────────────
        top_bottom = descriptive.get("top_bottom", {})
        performer_lines = []

        for key, data in top_bottom.items():
            title = data.get("title", key.replace("_", " ").title())
            agg = data.get("aggregation", "N/A").upper()
            entity = data.get("entity", "records")

            performer_lines.append(f"\n{title} ({agg} | {entity}):")

            if data.get("top_3"):
                performer_lines.append("  Top 3:")
                for item in data["top_3"]:
                    pct = (
                        f" ({item['pct_of_total']}%)"
                        if 'pct_of_total' in item else ""
                    )
                    performer_lines.append(
                        f"    - {item['name']}: {item['total']:,.2f}{pct}"
                    )

            if data.get("bottom_3"):
                performer_lines.append("  Bottom 3:")
                for item in data["bottom_3"]:
                    pct = (
                        f" ({item['pct_of_total']}%)"
                        if 'pct_of_total' in item else ""
                    )
                    performer_lines.append(
                        f"    - {item['name']}: {item['total']:,.2f}{pct}"
                    )

            if data.get("concentration"):
                performer_lines.append(
                    f"  Concentration: Top 3 = {data['concentration']}% of total"
                )

        prepared["performers"] = (
            "\n".join(performer_lines) if performer_lines
            else "No performer data available"
        )

        # ── Trends ─────────────────────────────────────
        trends = bundle.get("trends", {})

        if trends.get("available"):
            overall = trends.get("overall_trend", {})
            growth = trends.get("growth_analysis", {})
            comparison = trends.get("period_comparison", {})
            seasonality = trends.get("seasonality", {})
            momentum = trends.get("momentum", {})

            trend_lines = [
                f"Overall Direction: {overall.get('direction', 'N/A')} "
                f"({overall.get('strength', 'N/A')} trend)",
                f"R² (trend fit): {overall.get('r_squared', 'N/A')}",
                f"Interpretation: {overall.get('interpretation', 'N/A')}",
            ]

            if growth:
                trend_lines.extend([
                    f"\nGrowth Analysis:",
                    f"  Latest Growth Rate: {growth.get('latest_growth_rate', 'N/A')}%",
                    f"  Average Growth Rate: {growth.get('avg_growth_rate', 'N/A')}%",
                    f"  Growth Volatility: {growth.get('volatility', 'N/A')}%",
                    f"  CAGR: {growth.get('cagr', 'N/A')}%",
                    f"  Positive Periods: {growth.get('positive_periods', 0)}",
                    f"  Negative Periods: {growth.get('negative_periods', 0)}",
                ])
                if growth.get("interpretation"):
                    trend_lines.append(
                        f"  Growth Insight: {growth['interpretation']}"
                    )

            if comparison.get("available"):
                trend_lines.extend([
                    f"\nPeriod Comparison:",
                    f"  {comparison.get('interpretation', 'N/A')}",
                ])

            if seasonality.get("detected"):
                trend_lines.extend([
                    f"\nSeasonality:",
                    f"  {seasonality.get('interpretation', 'Detected')}",
                ])

            if momentum.get("available"):
                trend_lines.extend([
                    f"\nMomentum:",
                    f"  Status: {momentum.get('status', 'N/A')} "
                    f"{momentum.get('emoji', '')}",
                    f"  {momentum.get('description', '')}",
                ])

            prepared["trends"] = "\n".join(trend_lines)
            prepared["trends_summary"] = (
                f"Trend is {overall.get('direction', 'unknown')} "
                f"({overall.get('strength', 'N/A')}) "
                f"with {growth.get('latest_growth_rate', 0):+.1f}% latest growth. "
                f"Average growth: {growth.get('avg_growth_rate', 0):+.1f}%. "
                f"{'Seasonality detected. ' if seasonality.get('detected') else ''}"
                f"Momentum: {momentum.get('status', 'N/A')}."
            )
        else:
            reason = trends.get("reason", "No date column found")
            prepared["trends"] = f"Trend analysis not available: {reason}"
            prepared["trends_summary"] = "Trend analysis not available"

        # ── Anomalies ──────────────────────────────────
        anomalies = bundle.get("anomalies", {})
        summary = anomalies.get("summary", {})
        alerts = anomalies.get("alerts", [])

        anomaly_lines = [
            f"Overall Severity: {summary.get('overall_severity', 'N/A')} "
            f"{summary.get('severity_emoji', '')}",
            f"Total Anomalies: {summary.get('total_anomalies', 0)}",
            f"  Statistical Outliers: {summary.get('column_anomalies_count', 0)}",
            f"  Time Spikes: {summary.get('time_anomalies_count', 0)}",
            f"  Business Alerts: {summary.get('business_alerts_count', 0)}",
            f"Affected Columns: {', '.join(summary.get('affected_columns', []))}",
        ]

        if alerts:
            anomaly_lines.append("\nAlert Details:")
            for alert in alerts[:8]:
                anomaly_lines.append(
                    f"  {alert.get('emoji', '⚠️')} "
                    f"[{alert.get('severity', 'N/A').upper()}] "
                    f"{alert.get('title', '')}: "
                    f"{alert.get('message', '')}"
                )

        prepared["anomalies"] = "\n".join(anomaly_lines)
        prepared["anomalies_summary"] = (
            f"Severity: {summary.get('overall_severity', 'unknown')} "
            f"{summary.get('severity_emoji', '')}. "
            f"{summary.get('total_anomalies', 0)} total anomalies detected "
            f"({summary.get('column_anomalies_count', 0)} outliers, "
            f"{summary.get('time_anomalies_count', 0)} spikes, "
            f"{summary.get('business_alerts_count', 0)} alerts)."
        )

        return prepared


    # ═══════════════════════════════════════════════════════
    # DOMAIN CONTEXT (V2 — includes vocabulary rules)
    # ═══════════════════════════════════════════════════════

    def _get_domain_context(self, bundle: Dict) -> str:
        """
        Build domain-specific context string for prompts.

        This is CRITICAL for correct terminology:
        - Healthcare: "patients" not "customers"
        - HR: "employees" not "transactions"
        - Sales: "revenue" and "orders"

        The LLM reads this context and adjusts its language.
        """

        kpis = bundle.get("kpis", {})
        descriptive = bundle.get("descriptive", {})

        domain_name = kpis.get("domain_name", "General")
        llm_context = kpis.get("llm_context", "")
        domain_id = bundle.get("domain", "auto")

        # Basic context
        context_lines = [
            f"Domain: {domain_name}",
        ]

        if llm_context:
            context_lines.append(f"Focus: {llm_context}")

        # Column mapping
        mapping = kpis.get("column_mapping", {})
        if mapping:
            mapping_str = ", ".join(
                f"{role}='{col}'" for role, col in mapping.items()
            )
            context_lines.append(f"Detected columns: {mapping_str}")

        # Domain vocabulary (THE KEY ADDITION)
        domain_cfg = None
        if domain_id and domain_id != "auto":
            domain_cfg = get_domain_config(domain_id)

        if domain_cfg and domain_cfg.vocabulary:
            vocab = domain_cfg.vocabulary

            context_lines.append("")
            context_lines.append("TERMINOLOGY RULES (MUST FOLLOW):")
            context_lines.append(
                f"- Entity name: '{vocab.entity_name}' "
                f"(plural: '{vocab.entity_plural}')"
            )
            context_lines.append(
                f"- Primary metric: '{vocab.primary_metric_name}'"
            )
            context_lines.append(
                f"- When describing activity, say entities were "
                f"'{vocab.primary_metric_verb}'"
            )

            if vocab.preferred_terms:
                terms = ", ".join(vocab.preferred_terms[:8])
                context_lines.append(
                    f"- USE these terms: {terms}"
                )

            if vocab.forbidden_terms:
                terms = ", ".join(vocab.forbidden_terms)
                context_lines.append(
                    f"- NEVER use these words: {terms}"
                )

            if vocab.positive_descriptors:
                context_lines.append(
                    f"- For positive results, say: "
                    f"{', '.join(vocab.positive_descriptors[:3])}"
                )

            if vocab.negative_descriptors:
                context_lines.append(
                    f"- For negative results, say: "
                    f"{', '.join(vocab.negative_descriptors[:3])}"
                )

            if vocab.insight_questions:
                context_lines.append(
                    f"\nKEY QUESTIONS TO ADDRESS:"
                )
                for q in vocab.insight_questions[:5]:
                    context_lines.append(f"  - {q}")

        # Analysis config context
        if domain_cfg and domain_cfg.analysis_config:
            ac = domain_cfg.analysis_config
            context_lines.append(
                f"\nPrimary analysis metric: "
                f"{ac.primary_aggregation.upper()} of {ac.primary_metric_role}"
            )
            if ac.primary_aggregation == "count":
                context_lines.append(
                    f"NOTE: The primary metric is a COUNT, not a monetary sum. "
                    f"Do not describe it as revenue or financial figures."
                )

        return "\n".join(context_lines)