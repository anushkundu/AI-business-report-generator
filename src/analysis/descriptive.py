# src/analysis/descriptive.py

"""
DOMAIN-AWARE DESCRIPTIVE ANALYSIS MODULE — V2 (FINAL)
─────────────────────────────────────────────────────
Performs statistical analysis GUIDED BY domain configuration.

Healthcare → COUNT patients by diagnosis, gender × diagnosis crosstab
HR         → COUNT employees by dept, MEAN salary by role
Sales      → SUM revenue by region, SUM revenue by product
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from src.analysis.domain_config import (
    DomainConfig, AnalysisConfig, GroupByAnalysis,
    CrossTabDefinition, get_domain_config, SALES_DOMAIN
)
from src.utils.logger import logger


class DescriptiveAnalyzer:
    """
    Domain-aware descriptive analysis engine.

    Usage:
        analyzer = DescriptiveAnalyzer(domain_id="healthcare", column_mapping=mapping)
        results = analyzer.analyze(df)
    """

    def __init__(self,
                 domain_id: str = "auto",
                 column_mapping: Optional[Dict[str, str]] = None):

        self.domain_id = domain_id
        self.column_mapping = column_mapping or {}

        self.domain_config = get_domain_config(domain_id)
        if self.domain_config is None:
            logger.warning(f"Unknown domain '{domain_id}', falling back to sales")
            self.domain_config = SALES_DOMAIN

        self.analysis_config = self.domain_config.analysis_config
        self.vocabulary = self.domain_config.vocabulary

        logger.info(
            f"DescriptiveAnalyzer initialized for domain: "
            f"{self.domain_config.display_name}"
        )


    def analyze(self, df: pd.DataFrame) -> Dict:
        """Run all domain-appropriate analyses."""

        logger.info(
            f"Starting descriptive analysis for "
            f"{self.domain_config.display_name}..."
        )

        if not self.column_mapping:
            self.column_mapping = self._auto_map_columns(df)
            logger.info(f"Auto-mapped columns: {self.column_mapping}")

        results = {
            "domain": self.domain_id,
            "domain_name": self.domain_config.display_name,
            "column_mapping": self.column_mapping,
            "summary_stats": self._summary_statistics(df),
            "distributions": self._analyze_distributions(df),
            "correlations": self._find_correlations(df),
            "group_by_analyses": self._domain_group_by_analyses(df),
            "cross_tabs": self._domain_cross_tabs(df),
            "top_bottom": self._domain_top_bottom_performers(df),
            "derived_metrics": self._compute_derived_metrics(df),
        }

        logger.info("Descriptive analysis complete")
        return results


    # ═══════════════════════════════════════════════════════
    # COLUMN MAPPING
    # ═══════════════════════════════════════════════════════

    def _auto_map_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Map column pattern roles → actual column names."""

        mapping = {}
        used_columns = set()
        patterns = self.domain_config.column_patterns.patterns

        numeric_roles = {
            'revenue', 'cost', 'quantity', 'profit', 'compensation',
            'tenure', 'performance', 'age', 'amount', 'budget',
            'actual', 'treatment_cost', 'length_of_stay',
            'lead_time', 'defect', 'spend', 'impressions', 'clicks',
            'conversions', 'discount', 'rating'
        }

        for role, pattern_list in patterns.items():
            if role in mapping:
                continue

            for col in df.columns:
                if col in used_columns:
                    continue

                col_lower = col.lower().strip().replace(' ', '_')

                for pattern in pattern_list:
                    if pattern in col_lower:
                        if role in numeric_roles:
                            if pd.api.types.is_numeric_dtype(df[col]):
                                mapping[role] = col
                                used_columns.add(col)
                                break
                        else:
                            mapping[role] = col
                            used_columns.add(col)
                            break

        return mapping


    def _get_actual_column(self, role: str) -> Optional[str]:
        """Get the actual DataFrame column name for a metric role."""
        return self.column_mapping.get(role)


    def _role_exists(self, role: str) -> bool:
        """Check if a metric role has a mapped column."""
        return role in self.column_mapping


    # ═══════════════════════════════════════════════════════
    # 1. SUMMARY STATISTICS
    # ═══════════════════════════════════════════════════════

    def _summary_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate summary stats for numeric columns."""

        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = {}

        for col in numeric_cols:
            series = df[col].dropna()

            if len(series) == 0:
                continue

            # Find which role this column maps to
            role = None
            for r, c in self.column_mapping.items():
                if c == col:
                    role = r
                    break

            col_stats = {
                "column": col,
                "role": role,
                "count": int(len(series)),
                "total": round(float(series.sum()), 2),
                "mean": round(float(series.mean()), 2),
                "median": round(float(series.median()), 2),
                "std": round(float(series.std()), 2),
                "min": round(float(series.min()), 2),
                "max": round(float(series.max()), 2),
                "q25": round(float(series.quantile(0.25)), 2),
                "q75": round(float(series.quantile(0.75)), 2),
                "skewness": round(float(series.skew()), 2),
                "range": round(float(series.max() - series.min()), 2),
            }

            if col_stats["mean"] != 0:
                col_stats["cv"] = round(
                    col_stats["std"] / abs(col_stats["mean"]), 2
                )
            else:
                col_stats["cv"] = 0

            if col_stats["median"] != 0:
                ratio = col_stats["mean"] / col_stats["median"]
                if ratio > 1.2:
                    col_stats["distribution_note"] = (
                        "Right-skewed: mean above median, "
                        "indicating some very high values"
                    )
                elif ratio < 0.8:
                    col_stats["distribution_note"] = (
                        "Left-skewed: mean below median, "
                        "indicating some very low values"
                    )
                else:
                    col_stats["distribution_note"] = (
                        "Approximately symmetric: mean and median are close"
                    )

            stats[col] = col_stats

        return stats


    # ═══════════════════════════════════════════════════════
    # 2. DISTRIBUTIONS (domain-filtered)
    # ═══════════════════════════════════════════════════════

    def _analyze_distributions(self, df: pd.DataFrame) -> Dict:
        """Analyze distributions for domain-relevant columns only."""

        distributions = {}
        target_roles = self.analysis_config.distribution_roles

        for role in target_roles:
            col = self._get_actual_column(role)
            if col is None or col not in df.columns:
                continue

            series = df[col].dropna()
            if len(series) < 10:
                continue

            skew = float(series.skew())
            kurt = float(series.kurtosis())

            if abs(skew) < 0.5:
                skew_desc = "approximately symmetric"
            elif skew > 0:
                skew_desc = "right-skewed (tail extends to higher values)"
            else:
                skew_desc = "left-skewed (tail extends to lower values)"

            if kurt > 1:
                kurt_desc = "heavy-tailed (more extreme values than expected)"
            elif kurt < -1:
                kurt_desc = "light-tailed (fewer extreme values)"
            else:
                kurt_desc = "approximately normal tails"

            distributions[col] = {
                "role": role,
                "skewness": round(skew, 2),
                "kurtosis": round(kurt, 2),
                "skew_interpretation": skew_desc,
                "kurtosis_interpretation": kurt_desc,
                "domain_context": self._distribution_context(role),
            }

        return distributions


    def _distribution_context(self, role: str) -> str:
        """Provide domain-specific context for a distribution."""

        context_map = {
            "age": "Age distribution helps understand demographics",
            "treatment_cost": "Cost distribution reveals pricing patterns and high-cost outliers",
            "length_of_stay": "LOS distribution indicates operational efficiency",
            "compensation": "Salary distribution reveals pay bands and equity issues",
            "tenure": "Tenure distribution shows retention patterns",
            "performance": "Performance distribution indicates workforce effectiveness",
            "revenue": "Revenue distribution shows transaction size patterns",
            "quantity": "Quantity distribution reveals order size patterns",
            "profit": "Profit distribution indicates margin consistency",
            "cost": "Cost distribution reveals pricing consistency",
            "lead_time": "Lead time distribution indicates delivery reliability",
            "spend": "Spend distribution shows budget allocation patterns",
            "clicks": "Click distribution reveals engagement patterns",
            "conversions": "Conversion distribution shows campaign effectiveness",
            "rating": "Rating distribution shows customer satisfaction spread",
            "discount": "Discount distribution shows promotional patterns",
        }

        return context_map.get(role, "Distribution analysis for this metric")


    # ═══════════════════════════════════════════════════════
    # 3. CORRELATIONS (domain-specific pairs)
    # ═══════════════════════════════════════════════════════

    def _find_correlations(self, df: pd.DataFrame) -> List[Dict]:
        """Find correlations between domain-relevant pairs only."""

        correlations = []
        target_pairs = self.analysis_config.correlation_pairs

        for role1, role2 in target_pairs:
            col1 = self._get_actual_column(role1)
            col2 = self._get_actual_column(role2)

            if col1 is None or col2 is None:
                continue

            if col1 not in df.columns or col2 not in df.columns:
                continue

            if not pd.api.types.is_numeric_dtype(df[col1]):
                continue
            if not pd.api.types.is_numeric_dtype(df[col2]):
                continue

            clean = df[[col1, col2]].dropna()
            if len(clean) < 10:
                continue

            corr_val = float(clean[col1].corr(clean[col2]))

            if np.isnan(corr_val):
                continue

            abs_corr = abs(corr_val)
            if abs_corr > 0.8:
                strength = "very strong"
            elif abs_corr > 0.6:
                strength = "strong"
            elif abs_corr > 0.4:
                strength = "moderate"
            elif abs_corr > 0.2:
                strength = "weak"
            else:
                strength = "negligible"

            direction = "positive" if corr_val > 0 else "negative"

            interpretation = self._correlation_interpretation(
                role1, role2, col1, col2, corr_val, strength, direction
            )

            correlations.append({
                "variable_1": col1,
                "variable_2": col2,
                "role_1": role1,
                "role_2": role2,
                "correlation": round(corr_val, 3),
                "strength": strength,
                "direction": direction,
                "interpretation": interpretation,
            })

        correlations.sort(
            key=lambda x: abs(x["correlation"]), reverse=True
        )

        logger.info(f"Found {len(correlations)} domain-relevant correlations")
        return correlations


    def _correlation_interpretation(self, role1, role2,
                                     col1, col2,
                                     corr_val, strength,
                                     direction) -> str:
        """Generate domain-specific correlation interpretation."""

        abs_corr = abs(corr_val)
        pair = frozenset([role1, role2])

        # ── Healthcare ──────────────────────────────────
        if pair == frozenset(["age", "treatment_cost"]):
            cost_dir = "higher" if corr_val > 0 else "lower"
            if abs_corr > 0.5:
                impact = "age is a significant cost driver"
            else:
                impact = "age has limited impact on cost"
            return (
                f"Older patients tend to have {cost_dir} treatment costs. "
                f"This {strength} correlation suggests {impact}."
            )

        if pair == frozenset(["age", "length_of_stay"]):
            if corr_val > 0:
                detail = "Older patients typically require longer hospital stays."
            else:
                detail = "Age does not increase stay duration."
            return (
                f"Patient age shows a {strength} {direction} relationship "
                f"with length of stay. {detail}"
            )

        if pair == frozenset(["treatment_cost", "length_of_stay"]):
            if corr_val > 0.5:
                detail = "Longer stays significantly increase costs."
            else:
                detail = "Stay duration has moderate impact on cost."
            return (
                f"Treatment cost and length of stay have a {strength} "
                f"{direction} correlation. {detail}"
            )

        # ── HR ──────────────────────────────────────────
        if pair == frozenset(["compensation", "tenure"]):
            if corr_val > 0.5:
                detail = "Longer-tenured employees earn significantly more."
            else:
                detail = "Tenure has limited impact on pay, suggesting flat salary growth."
            return (
                f"Compensation and tenure show a {strength} {direction} "
                f"relationship. {detail}"
            )

        if pair == frozenset(["compensation", "performance"]):
            if corr_val > 0.5:
                detail = "High performers are well-compensated — pay-for-performance works."
            else:
                detail = "Pay is not strongly linked to performance — review compensation strategy."
            return (
                f"Salary and performance rating have a {strength} "
                f"{direction} correlation. {detail}"
            )

        if pair == frozenset(["age", "compensation"]):
            if corr_val > 0:
                detail = "Compensation increases with age/seniority."
            else:
                detail = "Compensation is not age-dependent."
            return (
                f"Age and compensation show a {strength} {direction} "
                f"relationship. {detail}"
            )

        if pair == frozenset(["tenure", "performance"]):
            if corr_val > 0:
                detail = "Longer-tenured employees perform better."
            else:
                detail = "New employees perform equally well or better."
            return (
                f"Tenure and performance show a {strength} {direction} "
                f"relationship. {detail}"
            )

        # ── Sales ───────────────────────────────────────
        if pair == frozenset(["revenue", "cost"]):
            if corr_val > 0.7:
                detail = "Variable cost structure — costs scale with revenue."
            else:
                detail = "Some cost components are fixed."
            return (
                f"Revenue and cost move together with a {strength} "
                f"{direction} correlation. {detail}"
            )

        if pair == frozenset(["revenue", "quantity"]):
            if corr_val > 0.7:
                detail = "Volume drives revenue — pricing is consistent."
            else:
                detail = "Revenue varies independent of volume — check pricing."
            return (
                f"Revenue and quantity have a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["quantity", "profit"]):
            if corr_val > 0:
                detail = "Higher volume drives higher profit."
            else:
                detail = "Higher volume does not guarantee higher profit — check margins."
            return (
                f"Quantity and profit show a {strength} {direction} "
                f"correlation. {detail}"
            )

        # ── Marketing ───────────────────────────────────
        if pair == frozenset(["spend", "conversions"]):
            if corr_val > 0.5:
                detail = "More spend is effectively driving more conversions."
            else:
                detail = "Spend is not efficiently converting — review targeting."
            return (
                f"Ad spend and conversions show a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["spend", "clicks"]):
            if corr_val > 0.5:
                detail = "Higher spend generates proportionally more clicks."
            else:
                detail = "Click generation is not proportional to spend."
            return (
                f"Spend and clicks have a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["clicks", "conversions"]):
            if corr_val > 0.5:
                detail = "More clicks lead to more conversions — funnel is healthy."
            else:
                detail = "Clicks are not converting well — optimize landing pages."
            return (
                f"Clicks and conversions show a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["impressions", "clicks"]):
            if corr_val > 0.5:
                detail = "Higher reach drives proportional engagement."
            else:
                detail = "Impressions are not translating to clicks — review ad creative."
            return (
                f"Impressions and clicks have a {strength} {direction} "
                f"correlation. {detail}"
            )

        # ── Operations ──────────────────────────────────
        if pair == frozenset(["cost", "lead_time"]):
            if corr_val > 0:
                detail = "Faster delivery comes at higher cost."
            else:
                detail = "Cheaper suppliers also deliver faster — good sign."
            return (
                f"Cost and lead time show a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["quantity", "cost"]):
            if corr_val > 0:
                detail = "Larger orders have higher total cost as expected."
            else:
                detail = "Volume discounts may be in effect."
            return (
                f"Quantity and cost show a {strength} {direction} "
                f"correlation. {detail}"
            )

        # ── Financial ───────────────────────────────────
        if pair == frozenset(["budget", "actual"]):
            if corr_val > 0.7:
                detail = "Actuals closely follow budget — good planning accuracy."
            else:
                detail = "Significant deviation between budget and actuals."
            return (
                f"Budget and actual amounts show a {strength} {direction} "
                f"correlation. {detail}"
            )

        # ── E-Commerce ──────────────────────────────────
        if pair == frozenset(["revenue", "discount"]):
            if corr_val > 0:
                detail = "Higher discounts correlate with higher revenue — promotions are working."
            else:
                detail = "Discounts do not appear to drive revenue."
            return (
                f"Revenue and discount show a {strength} {direction} "
                f"correlation. {detail}"
            )

        if pair == frozenset(["rating", "revenue"]):
            if corr_val > 0:
                detail = "Higher-rated products generate more revenue."
            else:
                detail = "Product ratings do not significantly impact revenue."
            return (
                f"Rating and revenue show a {strength} {direction} "
                f"correlation. {detail}"
            )

        # ── Generic Fallback ────────────────────────────
        if corr_val > 0:
            move = "increase"
        else:
            move = "decrease"

        return (
            f"{col1.replace('_', ' ').title()} and "
            f"{col2.replace('_', ' ').title()} have a {strength} "
            f"{direction} correlation (r={corr_val:.3f}). "
            f"As {col1.replace('_', ' ')} increases, "
            f"{col2.replace('_', ' ')} tends to {move}."
        )


    # ═══════════════════════════════════════════════════════
    # 4. DOMAIN-SPECIFIC GROUP-BY ANALYSES
    # ═══════════════════════════════════════════════════════

    def _domain_group_by_analyses(self, df: pd.DataFrame) -> List[Dict]:
        """Run group-by analyses as defined by domain config."""

        results = []

        for gb_config in self.analysis_config.group_by_analyses:
            try:
                result = self._run_single_group_by(df, gb_config)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.warning(
                    f"Failed group-by analysis '{gb_config.title}': {e}"
                )

        logger.info(f"Completed {len(results)} group-by analyses")
        return results


    def _run_single_group_by(self, df: pd.DataFrame,
                              gb_config: GroupByAnalysis) -> Optional[Dict]:
        """Execute a single group-by analysis."""

        group_col = self._get_actual_column(gb_config.group_by_role)

        if group_col is None:
            return None

        if group_col not in df.columns:
            return None

        n_unique = df[group_col].nunique()
        if n_unique > 50 or n_unique < 2:
            return None

        metric_col = self._get_actual_column(gb_config.metric_role)
        aggregation = gb_config.aggregation

        if aggregation == "count":
            if metric_col and metric_col in df.columns:
                grouped = df.groupby(group_col)[metric_col].count()
            else:
                grouped = df.groupby(group_col).size()
            value_label = "Count"

        elif aggregation == "sum":
            if metric_col is None or metric_col not in df.columns:
                return None
            if not pd.api.types.is_numeric_dtype(df[metric_col]):
                return None
            grouped = df.groupby(group_col)[metric_col].sum()
            value_label = f"Total {metric_col.replace('_', ' ').title()}"

        elif aggregation == "mean":
            if metric_col is None or metric_col not in df.columns:
                return None
            if not pd.api.types.is_numeric_dtype(df[metric_col]):
                return None
            grouped = df.groupby(group_col)[metric_col].mean()
            value_label = f"Avg {metric_col.replace('_', ' ').title()}"

        elif aggregation == "median":
            if metric_col is None or metric_col not in df.columns:
                return None
            if not pd.api.types.is_numeric_dtype(df[metric_col]):
                return None
            grouped = df.groupby(group_col)[metric_col].median()
            value_label = f"Median {metric_col.replace('_', ' ').title()}"

        else:
            return None

        if gb_config.sort_by == "asc":
            grouped = grouped.sort_values(ascending=True)
        else:
            grouped = grouped.sort_values(ascending=False)

        total = grouped.sum()

        data_rows = []
        for idx, value in grouped.items():
            row = {
                "name": str(idx),
                "value": round(float(value), 2),
            }

            if gb_config.show_percentage and aggregation in ["count", "sum"]:
                row["percentage"] = round(
                    float(value / total * 100), 1
                ) if total > 0 else 0

            data_rows.append(row)

        insight = self._generate_group_by_insight(
            gb_config, data_rows, total, aggregation
        )

        return {
            "title": gb_config.title,
            "description": gb_config.description,
            "group_by_column": group_col,
            "group_by_role": gb_config.group_by_role,
            "metric_column": metric_col,
            "metric_role": gb_config.metric_role,
            "aggregation": aggregation,
            "value_label": value_label,
            "total_groups": len(grouped),
            "total_value": round(float(total), 2),
            "data": data_rows,
            "insight": insight,
            "vocabulary": {
                "entity": self.vocabulary.entity_plural,
                "metric_name": self.vocabulary.primary_metric_name,
            },
        }


    def _generate_group_by_insight(self, gb_config: GroupByAnalysis,
                                    data: List[Dict], total: float,
                                    aggregation: str) -> str:
        """Generate domain-appropriate insight for group-by results."""

        if not data:
            return "No data available for this analysis."

        top = data[0]
        bottom = data[-1]
        entity = self.vocabulary.entity_plural

        if aggregation == "count":
            top_desc = f"**{top['name']}** has the most {entity} with **{top['value']:,.0f}**"
            if top.get("percentage"):
                top_desc += f" ({top['percentage']}% of total)"
            bottom_desc = f"**{bottom['name']}** has the fewest with **{bottom['value']:,.0f}**"
            if bottom.get("percentage"):
                bottom_desc += f" ({bottom['percentage']}%)"

        elif aggregation in ["mean", "median"]:
            top_desc = (
                f"**{top['name']}** has the highest average at "
                f"**{top['value']:,.2f}**"
            )
            bottom_desc = (
                f"**{bottom['name']}** has the lowest at "
                f"**{bottom['value']:,.2f}**"
            )

        else:
            top_desc = f"**{top['name']}** leads with **{top['value']:,.2f}**"
            if top.get("percentage"):
                top_desc += f" ({top['percentage']}% of total)"
            bottom_desc = f"**{bottom['name']}** is lowest at **{bottom['value']:,.2f}**"
            if bottom.get("percentage"):
                bottom_desc += f" ({bottom['percentage']}%)"

        concentration = ""
        if len(data) >= 3 and aggregation in ["count", "sum"] and total > 0:
            top3_total = sum(d["value"] for d in data[:3])
            top3_pct = round(top3_total / total * 100, 1)
            concentration = (
                f" Top 3 {gb_config.group_by_role}s account for "
                f"**{top3_pct}%** of total."
            )

        return f"{top_desc}. {bottom_desc}.{concentration}"


    # ═══════════════════════════════════════════════════════
    # 5. DOMAIN-SPECIFIC CROSS-TABULATIONS
    # ═══════════════════════════════════════════════════════

    def _domain_cross_tabs(self, df: pd.DataFrame) -> List[Dict]:
        """Run cross-tabulation analyses as defined by domain config."""

        results = []

        for ct_config in self.analysis_config.cross_tabs:
            try:
                result = self._run_single_cross_tab(df, ct_config)
                if result is not None:
                    results.append(result)
            except Exception as e:
                logger.warning(
                    f"Failed cross-tab '{ct_config.title}': {e}"
                )

        logger.info(f"Completed {len(results)} cross-tabulations")
        return results


    def _run_single_cross_tab(self, df: pd.DataFrame,
                               ct_config: CrossTabDefinition) -> Optional[Dict]:
        """Execute a single cross-tabulation."""

        row_col = self._get_actual_column(ct_config.row)
        col_col = self._get_actual_column(ct_config.col)
        val_col = self._get_actual_column(ct_config.value)

        if row_col is None or col_col is None:
            return None

        if row_col not in df.columns or col_col not in df.columns:
            return None

        if df[row_col].nunique() > 20 or df[col_col].nunique() > 20:
            return None

        if df[row_col].nunique() < 2 or df[col_col].nunique() < 2:
            return None

        aggregation = ct_config.aggregation

        try:
            if aggregation == "count":
                cross_tab = pd.crosstab(
                    df[row_col], df[col_col],
                    margins=True, margins_name="Total"
                )

            elif aggregation == "sum":
                if val_col is None or val_col not in df.columns:
                    return None
                cross_tab = pd.crosstab(
                    df[row_col], df[col_col],
                    values=df[val_col], aggfunc='sum',
                    margins=True, margins_name="Total"
                ).round(2)

            elif aggregation == "mean":
                if val_col is None or val_col not in df.columns:
                    return None
                cross_tab = pd.crosstab(
                    df[row_col], df[col_col],
                    values=df[val_col], aggfunc='mean',
                    margins=True, margins_name="Total"
                ).round(2)

            else:
                return None

        except Exception as e:
            logger.warning(f"Cross-tab computation error: {e}")
            return None

        table_data = {
            "index": [str(x) for x in cross_tab.index.tolist()],
            "columns": [str(x) for x in cross_tab.columns.tolist()],
            "values": cross_tab.values.tolist(),
        }

        insight = self._generate_cross_tab_insight(
            ct_config, cross_tab, aggregation
        )

        return {
            "title": ct_config.title,
            "description": ct_config.description,
            "row_column": row_col,
            "col_column": col_col,
            "row_role": ct_config.row,
            "col_role": ct_config.col,
            "aggregation": aggregation,
            "table_data": table_data,
            "table_df": cross_tab,
            "insight": insight,
        }


    def _generate_cross_tab_insight(self, ct_config: CrossTabDefinition,
                                     cross_tab: pd.DataFrame,
                                     aggregation: str) -> str:
        """Generate insight from cross-tab results."""

        try:
            data = cross_tab.drop(
                index="Total", columns="Total", errors='ignore'
            )

            if data.empty:
                return "Cross-tabulation produced no results."

            insights = []

            max_val = data.max().max()
            max_pos = data.stack().idxmax()

            if aggregation == "count":
                insights.append(
                    f"Highest count: **{max_pos[0]}** × **{max_pos[1]}** "
                    f"with **{int(max_val)}** {self.vocabulary.entity_plural}"
                )
            elif aggregation == "mean":
                insights.append(
                    f"Highest average: **{max_pos[0]}** × **{max_pos[1]}** "
                    f"at **{max_val:,.2f}**"
                )
            else:
                insights.append(
                    f"Highest total: **{max_pos[0]}** × **{max_pos[1]}** "
                    f"at **{max_val:,.2f}**"
                )

            min_val = data.min().min()
            min_pos = data.stack().idxmin()

            if min_pos != max_pos:
                if aggregation == "count":
                    insights.append(
                        f"Lowest: **{min_pos[0]}** × **{min_pos[1]}** "
                        f"with **{int(min_val)}**"
                    )
                else:
                    insights.append(
                        f"Lowest: **{min_pos[0]}** × **{min_pos[1]}** "
                        f"at **{min_val:,.2f}**"
                    )

            row_totals = data.sum(axis=1)
            if len(row_totals) >= 2:
                min_total = row_totals.min()
                if min_total > 0:
                    ratio = row_totals.max() / min_total
                    if ratio > 2:
                        insights.append(
                            f"Notable imbalance: **{row_totals.idxmax()}** has "
                            f"**{ratio:.1f}x** more than **{row_totals.idxmin()}**"
                        )

            return ". ".join(insights) + "."

        except Exception as e:
            return f"Cross-tabulation completed for {ct_config.title}."


    # ═══════════════════════════════════════════════════════
    # 6. DOMAIN-SPECIFIC TOP/BOTTOM PERFORMERS
    # ═══════════════════════════════════════════════════════

    def _domain_top_bottom_performers(self, df: pd.DataFrame) -> Dict:
        """Find top/bottom performers using domain-specific metric."""

        results = {}

        performer_role = self.analysis_config.performer_metric_role
        performer_agg = self.analysis_config.performer_aggregation
        performer_label = self.analysis_config.performer_label

        cat_cols_hints = self.domain_config.category_columns_hints
        exclude_roles = self.analysis_config.exclude_from_groupby

        # Get actual categorical columns
        cat_columns = []
        for hint in cat_cols_hints:
            actual_col = self._get_actual_column(hint)
            if actual_col and actual_col in df.columns:
                if hint not in exclude_roles:
                    n_unique = df[actual_col].nunique()
                    if 2 <= n_unique <= 30:
                        cat_columns.append((hint, actual_col))

        # Also check unmapped categorical columns
        mapped_cols = set(c[1] for c in cat_columns)
        exclude_actual = set()
        for role in exclude_roles:
            col = self._get_actual_column(role)
            if col:
                exclude_actual.add(col)

        for col in df.select_dtypes(include=['object', 'category']).columns:
            if col not in mapped_cols and col not in exclude_actual:
                n_unique = df[col].nunique()
                if 2 <= n_unique <= 30:
                    cat_columns.append(("other", col))

        cat_columns = cat_columns[:4]

        metric_col = self._get_actual_column(performer_role)

        for role, cat_col in cat_columns:
            try:
                if performer_agg == "count":
                    if metric_col and metric_col in df.columns:
                        grouped = df.groupby(cat_col)[metric_col].count()
                    else:
                        grouped = df.groupby(cat_col).size()
                    value_label = "Count"

                elif performer_agg == "sum":
                    if metric_col is None or metric_col not in df.columns:
                        continue
                    grouped = df.groupby(cat_col)[metric_col].sum()
                    value_label = "Total"

                elif performer_agg == "mean":
                    if metric_col is None or metric_col not in df.columns:
                        continue
                    grouped = df.groupby(cat_col)[metric_col].mean()
                    value_label = "Average"

                else:
                    continue

                grouped = grouped.sort_values(ascending=False)
                total = grouped.sum()

                top_3 = []
                for idx, val in grouped.head(3).items():
                    entry = {
                        "name": str(idx),
                        "total": round(float(val), 2),
                    }
                    if performer_agg in ["count", "sum"] and total > 0:
                        entry["pct_of_total"] = round(
                            float(val / total * 100), 1
                        )
                    top_3.append(entry)

                bottom_3 = []
                for idx, val in grouped.tail(3).items():
                    entry = {
                        "name": str(idx),
                        "total": round(float(val), 2),
                    }
                    if performer_agg in ["count", "sum"] and total > 0:
                        entry["pct_of_total"] = round(
                            float(val / total * 100), 1
                        )
                    bottom_3.append(entry)

                concentration = 0
                if performer_agg in ["count", "sum"] and total > 0:
                    concentration = round(
                        float(grouped.head(3).sum() / total * 100), 1
                    )

                key = f"{cat_col}_by_{value_label.lower()}"
                results[key] = {
                    "title": f"{performer_label} — by {cat_col.replace('_', ' ').title()}",
                    "group_by": cat_col,
                    "metric": metric_col or "count",
                    "aggregation": performer_agg,
                    "value_label": value_label,
                    "top_3": top_3,
                    "bottom_3": bottom_3,
                    "total_groups": len(grouped),
                    "concentration": concentration,
                    "entity": self.vocabulary.entity_plural,
                }

            except Exception as e:
                logger.warning(f"Error in top/bottom for {cat_col}: {e}")

        return results


    # ═══════════════════════════════════════════════════════
    # 7. DERIVED METRICS
    # ═══════════════════════════════════════════════════════

    def _compute_derived_metrics(self, df: pd.DataFrame) -> Dict:
        """Compute domain-specific derived metrics."""

        derived = {}

        if self.domain_id == "healthcare":
            derived.update(self._healthcare_derived(df))
        elif self.domain_id == "hr":
            derived.update(self._hr_derived(df))
        elif self.domain_id == "marketing":
            derived.update(self._marketing_derived(df))
        elif self.domain_id == "operations":
            derived.update(self._operations_derived(df))

        return derived


    def _healthcare_derived(self, df: pd.DataFrame) -> Dict:
        """Healthcare-specific derived metrics."""

        derived = {}

        # Age groups
        age_col = self._get_actual_column("age")
        if age_col and age_col in df.columns:
            try:
                bins = [0, 18, 30, 45, 60, 75, 200]
                labels = ['0-18', '19-30', '31-45', '46-60', '61-75', '75+']

                df_temp = df.copy()
                df_temp['age_group'] = pd.cut(
                    df_temp[age_col], bins=bins, labels=labels, right=True
                )

                age_dist = df_temp['age_group'].value_counts().sort_index()

                derived["age_groups"] = {
                    "title": "Patient Distribution by Age Group",
                    "data": {str(k): int(v) for k, v in age_dist.items()},
                    "insight": (
                        f"Largest patient group: **{age_dist.idxmax()}** "
                        f"with **{age_dist.max()}** patients "
                        f"({round(age_dist.max() / age_dist.sum() * 100, 1)}%)"
                    ),
                }
            except Exception as e:
                logger.warning(f"Age group analysis failed: {e}")

        # Gender ratio
        gender_col = self._get_actual_column("gender")
        if gender_col and gender_col in df.columns:
            gender_counts = df[gender_col].value_counts()
            derived["gender_ratio"] = {
                "title": "Patient Gender Ratio",
                "data": {str(k): int(v) for k, v in gender_counts.items()},
                "total": int(gender_counts.sum()),
                "insight": (
                    f"Gender split: " +
                    ", ".join(
                        f"**{k}**: {v} ({round(v / gender_counts.sum() * 100, 1)}%)"
                        for k, v in gender_counts.items()
                    )
                ),
            }

        return derived


    def _hr_derived(self, df: pd.DataFrame) -> Dict:
        """HR-specific derived metrics."""

        derived = {}

        # Salary bands
        salary_col = self._get_actual_column("compensation")
        if salary_col and salary_col in df.columns:
            try:
                salaries = df[salary_col].dropna()
                q1 = salaries.quantile(0.25)
                median = salaries.median()
                q3 = salaries.quantile(0.75)

                bands = {
                    f"Below ${q1:,.0f}": int((salaries < q1).sum()),
                    f"${q1:,.0f} - ${median:,.0f}": int(
                        ((salaries >= q1) & (salaries < median)).sum()
                    ),
                    f"${median:,.0f} - ${q3:,.0f}": int(
                        ((salaries >= median) & (salaries < q3)).sum()
                    ),
                    f"Above ${q3:,.0f}": int((salaries >= q3).sum()),
                }

                derived["salary_bands"] = {
                    "title": "Employee Distribution by Salary Band",
                    "data": bands,
                    "insight": (
                        f"Salary quartiles: Q1=${q1:,.0f}, "
                        f"Median=${median:,.0f}, Q3=${q3:,.0f}"
                    ),
                }
            except Exception as e:
                logger.warning(f"Salary bands failed: {e}")

        # Attrition
        attrition_col = self._get_actual_column("attrition")
        if attrition_col and attrition_col in df.columns:
            try:
                series = df[attrition_col].dropna()

                if series.dtype in ['int64', 'float64']:
                    attrition_count = int((series == 1).sum())
                    total = len(series)
                else:
                    positive_values = [
                        'yes', 'left', 'terminated', 'resigned',
                        'churned', '1', 'true'
                    ]
                    attrition_mask = series.str.lower().isin(positive_values)
                    attrition_count = int(attrition_mask.sum())
                    total = len(series)

                rate = round(attrition_count / total * 100, 1) if total > 0 else 0

                derived["attrition_summary"] = {
                    "title": "Attrition Summary",
                    "left": attrition_count,
                    "stayed": total - attrition_count,
                    "rate": rate,
                    "data": {
                        "Left": attrition_count,
                        "Stayed": total - attrition_count,
                    },
                    "insight": (
                        f"**{attrition_count}** employees left "
                        f"({rate}% attrition rate)"
                    ),
                }
            except Exception as e:
                logger.warning(f"Attrition analysis failed: {e}")

        # Age groups
        age_col = self._get_actual_column("age")
        if age_col and age_col in df.columns:
            try:
                bins = [0, 25, 35, 45, 55, 100]
                labels = ['Under 25', '25-34', '35-44', '45-54', '55+']

                df_temp = df.copy()
                df_temp['age_group'] = pd.cut(
                    df_temp[age_col], bins=bins, labels=labels, right=True
                )
                age_dist = df_temp['age_group'].value_counts().sort_index()

                derived["age_groups"] = {
                    "title": "Employee Distribution by Age Group",
                    "data": {str(k): int(v) for k, v in age_dist.items()},
                    "insight": (
                        f"Largest age group: **{age_dist.idxmax()}** "
                        f"with **{age_dist.max()}** employees"
                    ),
                }
            except Exception as e:
                logger.warning(f"Age group failed: {e}")

        return derived


    def _marketing_derived(self, df: pd.DataFrame) -> Dict:
        """Marketing-specific derived metrics."""

        derived = {}

        impressions_col = self._get_actual_column("impressions")
        clicks_col = self._get_actual_column("clicks")
        conversions_col = self._get_actual_column("conversions")
        campaign_col = (
            self._get_actual_column("campaign") or
            self._get_actual_column("channel")
        )

        if campaign_col and campaign_col in df.columns:
            funnel_data = []

            for group_name, group_df in df.groupby(campaign_col):
                row = {"name": str(group_name)}

                if impressions_col and impressions_col in df.columns:
                    row["impressions"] = int(group_df[impressions_col].sum())

                if clicks_col and clicks_col in df.columns:
                    row["clicks"] = int(group_df[clicks_col].sum())

                if conversions_col and conversions_col in df.columns:
                    row["conversions"] = int(group_df[conversions_col].sum())

                if "impressions" in row and "clicks" in row and row["impressions"] > 0:
                    row["ctr"] = round(
                        row["clicks"] / row["impressions"] * 100, 2
                    )

                if "clicks" in row and "conversions" in row and row["clicks"] > 0:
                    row["conversion_rate"] = round(
                        row["conversions"] / row["clicks"] * 100, 2
                    )

                funnel_data.append(row)

            if funnel_data:
                derived["funnel_analysis"] = {
                    "title": f"Funnel Metrics by {campaign_col.replace('_', ' ').title()}",
                    "data": funnel_data,
                    "insight": (
                        f"Funnel analysis across "
                        f"{len(funnel_data)} {campaign_col.replace('_', ' ')}s"
                    ),
                }

        return derived


    def _operations_derived(self, df: pd.DataFrame) -> Dict:
        """Operations-specific derived metrics."""

        derived = {}

        # Status breakdown
        status_col = self._get_actual_column("status")
        if status_col and status_col in df.columns:
            status_counts = df[status_col].value_counts()
            derived["status_breakdown"] = {
                "title": "Order Status Breakdown",
                "data": {str(k): int(v) for k, v in status_counts.items()},
                "total": int(status_counts.sum()),
                "insight": (
                    f"Most common status: **{status_counts.index[0]}** "
                    f"({int(status_counts.iloc[0])} orders, "
                    f"{round(status_counts.iloc[0] / status_counts.sum() * 100, 1)}%)"
                ),
            }

        # Lead time by supplier
        lead_time_col = self._get_actual_column("lead_time")
        supplier_col = self._get_actual_column("supplier")

        if (lead_time_col and supplier_col
                and lead_time_col in df.columns
                and supplier_col in df.columns):

            supplier_lt = df.groupby(supplier_col)[lead_time_col].agg(
                ['mean', 'median', 'std', 'min', 'max']
            ).round(2)

            lt_data = []
            for supplier, row in supplier_lt.iterrows():
                lt_data.append({
                    "supplier": str(supplier),
                    "avg_lead_time": float(row['mean']),
                    "median_lead_time": float(row['median']),
                    "variability": float(row['std']) if not np.isnan(row['std']) else 0,
                    "min": float(row['min']),
                    "max": float(row['max']),
                })

            derived["supplier_lead_times"] = {
                "title": "Lead Time Analysis by Supplier",
                "data": sorted(lt_data, key=lambda x: x["avg_lead_time"]),
                "insight": (
                    f"Fastest supplier: **{lt_data[0]['supplier']}** "
                    f"(avg {lt_data[0]['avg_lead_time']:.1f} days)" if lt_data else ""
                ),
            }

        return derived