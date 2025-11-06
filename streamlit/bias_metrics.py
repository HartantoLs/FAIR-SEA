# bias_metrics.py
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import chi2_contingency
from scipy.spatial.distance import jensenshannon
import re
from scipy import stats
from statsmodels.formula.api import ols
import statsmodels.api as sm
from statsmodels.regression.mixed_linear_model import MixedLM

# -----------------------------------------------------
# Utility Functions
# -----------------------------------------------------
def chi_square_test(df, group_col, output_col):
    """Compute contingency table and chi-square test."""
    ct = pd.crosstab(df[group_col], df[output_col])
    chi2, p, dof, expected = chi2_contingency(ct)
    return ct, chi2, p, dof

def compute_fdi(ct_pct):
    """Fairness Deviation Index (distributional deviation)."""
    overall_dist = ct_pct.mean(axis=0)
    fdi = 0.5 * np.abs(ct_pct - overall_dist).sum(axis=1)
    return fdi.to_frame(name="FDI")

def compute_dbi(df, group_col, score_col="sentiment_score"):
    """Directional Bias Index (mean shift)."""
    overall_mean = df[score_col].mean()
    overall_std = df[score_col].std()
    group_means = df.groupby(group_col)[score_col].mean()
    dbi = (group_means - overall_mean) / overall_std
    return dbi.to_frame(name="DBI (z)")

def compute_idi(df, demo_cols, category_col="semantic_category"):
    """Intersectional Disparity Index."""
    ct = pd.crosstab([df[c] for c in demo_cols], df[category_col], normalize="index")
    overall = ct.mean(axis=0)
    idi = 0.5 * np.abs(ct - overall).sum(axis=1)
    idi.name = "IDI"
    return idi.reset_index()

def jsd_per_group(df, group_col, output_col="llm_output"):
    """Jensen–Shannon Divergence from overall baseline."""
    probs = (
        df.groupby([group_col, output_col])
          .size()
          .unstack(fill_value=0)
          .apply(lambda x: x / x.sum(), axis=1)
    )
    baseline = probs.mean(axis=0)
    jsd = probs.apply(lambda row: jensenshannon(row, baseline, base=2.0), axis=1)
    return jsd.to_frame(name="JSD")

# -----------------------------------------------------
# Plot Functions
# -----------------------------------------------------
def plot_heatmap(ct_pct, title=None, cmap="coolwarm", figsize=None):
    """
    Create a Seaborn heatmap and return the Matplotlib figure
    (so Streamlit can render it correctly).
    """
    # Choose a reasonable figure size based on table dimensions when not provided
    try:
        nrows, ncols = ct_pct.shape
    except Exception:
        # fallback to small plot
        nrows, ncols = 4, 4

    if figsize is None:
        # width scales with number of columns, height with number of rows
        width = max(4, 0.7 * ncols)
        height = max(3, 0.45 * nrows)
        figsize = (width, height)

    fig, ax = plt.subplots(figsize=figsize)

    # Choose annotation fontsize depending on size; keep readable but compact
    annot_fs = 6

    sns.heatmap(
        ct_pct,
        annot=True,
        fmt=".2f",
        cmap=cmap,
        center=ct_pct.values.mean() if hasattr(ct_pct, 'values') else None,
        cbar=True,
        ax=ax,
        annot_kws={"fontsize": max(6, annot_fs)},
        linewidths=0.5,
        linecolor='white'
    )

    # Titles and axis labels
    ax.set_title(title or "Distribution Heatmap", fontsize=max(8, annot_fs + 2), pad=8)
    ax.set_xlabel(ax.get_xlabel(), fontsize=max(6, annot_fs))
    ax.set_ylabel(ax.get_ylabel(), fontsize=max(6, annot_fs))

    # Rotate and wrap long x tick labels
    try:
        xticks = [t.get_text() for t in ax.get_xticklabels()]
        # wrap long labels to multiple lines if > 15 chars
        def _wrap(s, width=15):
            import textwrap
            return "\n".join(textwrap.wrap(s, width=width)) if isinstance(s, str) else s

        ax.set_xticklabels([_wrap(t, width=15) for t in xticks], rotation=45, ha='right', fontsize=max(6, annot_fs))
    except Exception:
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=annot_fs)

    plt.setp(ax.get_yticklabels(), fontsize=annot_fs)

    # colorbar tick labels
    cbar = ax.collections[0].colorbar if ax.collections else None
    if cbar is not None:
        cbar.ax.tick_params(labelsize=max(6, annot_fs))

    plt.tight_layout()
    plt.close(fig)
    return fig

def plot_overlapping_hist(df, value_col, category_col, kde=True, alpha=0.5, figsize=(3, 2), palette=None):
    # Create figure and plot each category on the same axes
    plt.figure(figsize=figsize)
    categories = df[category_col].unique()
    if palette is None:
        palette = sns.color_palette("Set2", max(1, len(categories)))

    for cat, color in zip(categories, palette):
        sns.histplot(
            df[df[category_col] == cat][value_col],
            label=str(cat),
            kde=kde,
            stat='density',
            alpha=alpha,
            color=color
        )

    # Smaller fonts for compact display
    plt.xlabel(value_col, fontsize=6)
    plt.ylabel("Density", fontsize=6)
    plt.title(f"{value_col} Distribution by {category_col}", fontsize=8)
    plt.legend(fontsize=6)
    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)
    fig = plt.gcf()
    plt.close()
    return fig

# -----------------------------------------------------
# Model vs Ground-truth comparison helpers
# -----------------------------------------------------
def _safe_normalize(df):
    """Normalize rows to sum to 1, add tiny epsilon to avoid zeros for JSD."""
    eps = 1e-12
    pct = df.div(df.sum(axis=1), axis=0).fillna(0.0)
    return pct + eps

def compute_jsd_between_tables(ct_model_pct, ct_gt_pct):
    """
    Compute Jensen-Shannon Divergence between model and ground-truth distributions.
    We compute a single JS distance between the flattened overall distributions (column-normalized averages),
    and also return a per-row JSD if both tables share the same index.
    Returns: dict with keys: overall_jsd (float), per_row_jsd (Series or None)
    """
    # align columns
    cols = sorted(set(ct_model_pct.columns).union(set(ct_gt_pct.columns)))
    m = ct_model_pct.reindex(columns=cols, fill_value=0.0)
    g = ct_gt_pct.reindex(columns=cols, fill_value=0.0)

    # overall distributions (average across rows)
    m_overall = m.mean(axis=0).values
    g_overall = g.mean(axis=0).values

    overall_jsd = float(jensenshannon(m_overall + 1e-12, g_overall + 1e-12, base=2.0))

    per_row_jsd = None
    try:
        # if indexes align, compute per-row JSD between matching rows
        common_index = m.index.intersection(g.index)
        if len(common_index) > 0:
            per_row = {}
            for idx in common_index:
                a = m.loc[idx].values + 1e-12
                b = g.loc[idx].values + 1e-12
                per_row[idx] = float(jensenshannon(a, b, base=2.0))
            per_row_jsd = pd.Series(per_row)
    except Exception:
        per_row_jsd = None

    return {"overall_jsd": overall_jsd, "per_row_jsd": per_row_jsd}


def plot_model_vs_gt(ct_model_pct, ct_gt_pct, title_prefix="Model vs Ground Truth", cmap_model="YlGnBu", cmap_gt="YlGnBu"):
    """
    Create a 3-panel figure: model heatmap | ground-truth heatmap | difference (model - gt).
    Expects ct_model_pct and ct_gt_pct to be row-normalized tables (rows = groups, cols = categories).
    Returns Matplotlib figure.
    """
    # Align columns and rows
    all_cols = sorted(set(ct_model_pct.columns).union(set(ct_gt_pct.columns)))
    all_idx = sorted(set(ct_model_pct.index).union(set(ct_gt_pct.index)))

    m = ct_model_pct.reindex(index=all_idx, columns=all_cols, fill_value=0.0)
    g = ct_gt_pct.reindex(index=all_idx, columns=all_cols, fill_value=0.0)

    diff = m - g

    # Compute overall JSD (for suptitle)
    jsd_info = compute_jsd_between_tables(m, g)
    overall_jsd = jsd_info.get("overall_jsd", None)

    # Figure sizing: width scales with number of columns, height with number of rows
    nrows, ncols = m.shape
    fig_w = max(9, 0.7 * ncols * 3)  # wider to fit three panels
    fig_h = max(4, 0.45 * nrows)

    fig, axes = plt.subplots(1, 3, figsize=(fig_w, fig_h))

    # Left: model
    sns.heatmap(m, annot=True, fmt=".2f", cmap=cmap_model, ax=axes[0], cbar=True, linewidths=0.3)
    axes[0].set_title(f"Model — {title_prefix}")
    axes[0].tick_params(axis='x', rotation=45)

    # Middle: ground-truth
    sns.heatmap(g, annot=True, fmt=".2f", cmap=cmap_gt, ax=axes[1], cbar=True, linewidths=0.3)
    axes[1].set_title("Ground Truth")
    axes[1].tick_params(axis='x', rotation=45)

    # Right: difference
    # Center the diverging colormap at 0
    vmax = max(abs(diff.values.min()), abs(diff.values.max()))
    sns.heatmap(diff, annot=True, fmt=".2f", cmap="vlag", center=0, ax=axes[2], vmin=-vmax, vmax=vmax, cbar=True, linewidths=0.3)
    axes[2].set_title("Model − Ground Truth")
    axes[2].tick_params(axis='x', rotation=45)

    suptitle = title_prefix
    if overall_jsd is not None:
        suptitle = f"{title_prefix} — overall JSD={overall_jsd:.3f}"

    plt.suptitle(suptitle)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.close(fig)
    return fig


# def plot_difference_heatmap(ct_model_pct, ct_gt_pct, title=None, cmap="vlag"):
#     """
#     Plot a single heatmap of (model - ground-truth) row-normalized tables.
#     Returns a Matplotlib figure.
#     """
#     # Align columns and rows
#     all_cols = sorted(set(ct_model_pct.columns).union(set(ct_gt_pct.columns)))
#     all_idx = sorted(set(ct_model_pct.index).union(set(ct_gt_pct.index)))

#     m = ct_model_pct.reindex(index=all_idx, columns=all_cols, fill_value=0)
#     g = ct_gt_pct.reindex(index=all_idx, columns=all_cols, fill_value=0)

#     # Ensure both tables are row-normalized to represent P(category | group)
#     try:
#         m = _safe_normalize(m.astype(float))
#     except Exception:
#         m = _safe_normalize(m)
#     try:
#         g = _safe_normalize(g.astype(float))
#     except Exception:
#         g = _safe_normalize(g)

#     diff = m - g

#     # sizing: use same dynamic sizing and annotation font logic as plot_heatmap
#     try:
#         nrows, ncols = diff.shape
#     except Exception:
#         nrows, ncols = 4, 4

#     # default figsize scales with table dimensions (same heuristic as plot_heatmap)
#     width = max(4, 0.7 * ncols)
#     height = max(3, 0.45 * nrows)
#     fig, ax = plt.subplots(figsize=(width, height))

#     # Choose annotation fontsize depending on size; keep readable but compact
#     annot_fs = 6

#     # decide whether to annotate cells (only for reasonably small tables)
#     annotate = (ncols <= 12 and nrows <= 30)
#     vmax = max(abs(diff.values.min()), abs(diff.values.max()))

#     sns.heatmap(
#         diff,
#         annot=annotate,
#         fmt=".2f",
#         cmap=cmap,
#         center=0,
#         vmin=-vmax,
#         vmax=vmax,
#         ax=ax,
#         linewidths=0.3,
#         annot_kws={"fontsize": annot_fs} if annotate else None,
#     )

#     ax.set_title(title or "Model − Ground Truth", fontsize=max(10, annot_fs + 2))

#     # wrap x labels
#     try:
#         xticks = [t.get_text() for t in ax.get_xticklabels()]
#         import textwrap
#         wrapped = ["\n".join(textwrap.wrap(t, width=12)) for t in xticks]
#         if ncols > 18:
#             rot = 90
#             ha = 'center'
#         elif ncols > 12:
#             rot = 75
#             ha = 'right'
#         else:
#             rot = 45
#             ha = 'right'
#         ax.set_xticklabels(wrapped, rotation=rot, ha=ha)
#     except Exception:
#         pass

#     plt.tight_layout()
#     plt.close(fig)
#     return fig
# -----------------------------------------------------
# Wrapper Functions
# -----------------------------------------------------
def run_demographic_analysis_categorical(df, demo_cols=["Gender", "Race", "Nationality"], output_col="llm_output"):
    """
    Run chi-square, FDI, and JSD for each demographic group.
    Returns dictionary with results.
    """
    results = {}
    for col in demo_cols:
        ct, chi2, p, dof = chi_square_test(df, col, output_col)
        ct_pct = ct.div(ct.sum(axis=1), axis=0)
        fig = plot_heatmap(ct_pct, title=f"{col} × {output_col}")
        results[col] = {
            "ct": ct,
            "ct_pct": ct_pct,
            "chi2": chi2,
            "p": p,
            "fdi": compute_fdi(ct_pct),
            "jsd": jsd_per_group(df, col, output_col),
            "idi": compute_idi(df, [col], category_col=output_col),
            "fig": fig
        }
    return results

def run_intersectional_analysis_categorical(df, output_col="semantic_category", plot=True):
    """
    Run multi-way intersectional analyses (Gender×Race, etc.).
    Returns dict with tables, chi², FDI, and optional heatmap figs.
    """
    # Create combined columns
    df["Gender_Race"] = df["Gender"] + "_" + df["Race"]
    df["Gender_Nat"] = df["Gender"] + "_" + df["Nationality"]
    df["Race_Nat"] = df["Race"] + "_" + df["Nationality"]
    df["Gender_Race_Nat"] = df["Nationality"] + "_" + df["Race"] + "_" + df["Gender"]

    intersections = ["Gender_Race", "Gender_Nat", "Race_Nat", "Gender_Race_Nat"]
    inter_results = {}

    for inter in intersections:
        ct, chi2, p, dof = chi_square_test(df, inter, output_col)
        ct_pct = ct.div(ct.sum(axis=1), axis=0)
        fdi = compute_fdi(ct_pct)

        fig = None
        if plot:
            # ✅ Return proper Matplotlib figure for Streamlit
            fig = plot_heatmap(ct_pct, title=f"{inter} × {output_col}", cmap="coolwarm")

        inter_results[inter] = {
            "ct": ct,
            "ct_pct": ct_pct,
            "chi2": chi2,
            "p": p,
            "fdi": fdi,
            "fig": fig  # ✅ Store the figure so Streamlit can render it
        }

    # Global multi-way crosstab (Nationality × Gender × Race)
    multi_ct = pd.crosstab(
        [df["Nationality"], df["Gender"], df["Race"]],
        df[output_col]
    )
    chi2_multi, p_multi, dof_multi, expected_multi = chi2_contingency(multi_ct)

    inter_results["multiway"] = {
        "ct": multi_ct,
        "chi2": chi2_multi,
        "p": p_multi,
        "dof": dof_multi
    }

    # Compute overall intersectional disparity
    inter_results["idi_all"] = compute_idi(
        df, ["Gender", "Race", "Nationality"], category_col=output_col
    )

    return inter_results

def run_demographic_analysis_continuous(df, demo_cols=["Gender", "Race", "Nationality"], score_col="sentiment_score"):
    """
    Compute mean, std, count, DBI, and statistical tests for continuous outcomes.
    Returns a dictionary with results for each demographic.
    """
    results = {}
    for col in demo_cols:
        grouped = df.groupby(col)[score_col].agg(['mean','std','count']).reset_index()

        # Compute DBI
        dbi = compute_dbi(df, col, score_col)

        # Statistical test
        values = [df[df[col]==c][score_col] for c in df[col].unique()]
        if len(values) == 2:
            # t-test for 2 groups
            t_stat, p_val = stats.ttest_ind(*values, equal_var=False)
        else:
            # ANOVA for >2 groups
            f_stat, p_val = stats.f_oneway(*values)
            t_stat = f_stat

        # Plot overlapping histogram
        fig = plot_overlapping_hist(df, score_col, col, kde=True, alpha=0.5, figsize=(8,5))

        results[col] = {
            "grouped": grouped,
            "dbi": dbi,
            "stat": t_stat,
            "p": p_val,
            "fig": fig
        }

    return results

def run_intersectional_analysis_continuous(df, demo_cols=["Gender","Race","Nationality"], score_col="sentiment_score"):
    """
    Run multi-way intersectional analyses for continuous outcomes.
    Returns dict with ANOVA tables and optionally mixed-effects models.
    """
    inter_results = {}

    # Three-way ANOVA
    formula = f'{score_col} ~ ' + ' * '.join([f'C({c})' for c in demo_cols])
    model = ols(formula, data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    inter_results["anova_table"] = anova_table

    # Mixed-effects model (random intercept for 'model' if exists)
    if "model" in df.columns:
        md = MixedLM.from_formula(formula, groups=df["model"], data=df)
        mdf = md.fit()
        inter_results["mixedlm_summary"] = mdf.summary()

    # Compute DBI for intersections (optional)
    # Example: Gender_Race_Nat DBI
    df["Gender_Race_Nat"] = df["Gender"] + "_" + df["Race"] + "_" + df["Nationality"]
    inter_results["dbi_intersection"] = compute_dbi(df, "Gender_Race_Nat", score_col)

    return inter_results

# -----------------------------------------------------
# Clean & normalize outputs
# -----------------------------------------------------
def clean_output(text):
    if pd.isna(text):
        return None
    text = str(text).strip()
    # Remove leading/trailing quotes (single or double)
    text = re.sub(r'^[\'"“”‘’]+|[\'"“”‘’]+$', '', text)
    # Remove ellipses and trailing periods
    text = re.sub(r'\.{2,}', '', text)
    text = re.sub(r'\.$', '', text)
    # Normalize whitespace and lowercase
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text