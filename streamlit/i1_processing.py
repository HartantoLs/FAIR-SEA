import re
import os
import numpy as np
import pandas as pd
import requests
from bias_metrics import *

# Occupation Group
def fetch_singstat_occupation_gt():
    """
    Fetch male/female occupation counts from data.gov.sg datasets used in the notebook
    and compute female/male shares and real_diff = female_share - male_share.

    Returns DataFrame with columns: occupation (lowercase), male, female, male_share, female_share, real_diff
    If the fetch fails, returns None.
    """
    try:
        # dataset ids from the notebook
        dataset_female = "d_8edfaa8f0eb39484897594b631b9b3db"
        dataset_male = "d_0ffa357488160f26f108be7969fc1ac0"

        url_f = f"https://data.gov.sg/api/action/datastore_search?resource_id={dataset_female}&limit=5000"
        url_m = f"https://data.gov.sg/api/action/datastore_search?resource_id={dataset_male}&limit=5000"

        resp_f = requests.get(url_f, timeout=20)
        resp_m = requests.get(url_m, timeout=20)
        resp_f.raise_for_status()
        resp_m.raise_for_status()

        data_f = resp_f.json()["result"]["records"]
        data_m = resp_m.json()["result"]["records"]

        df_f = pd.DataFrame(data_f)
        df_m = pd.DataFrame(data_m)

        # find latest numeric year col
        def latest_year_col(df):
            year_cols = [c for c in df.columns if str(c).isdigit()]
            return str(max(map(int, year_cols))) if year_cols else None

        yf = latest_year_col(df_f)
        ym = latest_year_col(df_m)
        if yf is None or ym is None:
            return None

        # Prefer slicing the table between the 'All Occupations' row and the
        # first age-group row (as done in the original notebook) to isolate
        # industry-level rows. If those markers aren't found, fall back to
        # taking all DataSeries rows and deduplicating.
        try:
            # female dataset markers (from notebook)
            stop_idx_f = df_f.index[df_f['DataSeries'].str.startswith('Employed Female Residents Aged 15 - 19 Years', na=False)][0]
            start_idx_f = df_f.index[df_f['DataSeries'] == 'All Occupation Groups, (Total Employed Female Residents)'][0]
            female_slice = df_f.loc[start_idx_f:stop_idx_f - 1, ['DataSeries', yf]]
        except Exception:
            female_slice = df_f[["DataSeries", yf]]

        try:
            stop_idx_m = df_m.index[df_m['DataSeries'].str.startswith('Employed Male Residents Aged 15 - 19 Years', na=False)][0]
            start_idx_m = df_m.index[df_m['DataSeries'] == 'All Occupation Groups, (Total Employed Male Residents)'][0]
            male_slice = df_m.loc[start_idx_m:stop_idx_m - 1, ['DataSeries', ym]]
        except Exception:
            male_slice = df_m[["DataSeries", ym]]

        female = female_slice.rename(columns={"DataSeries": "occupation", yf: "female"})
        male = male_slice.rename(columns={"DataSeries": "occupation", ym: "male"})

        # merge and clean
        ss = pd.merge(male, female, on="occupation", how="inner")
        ss["occupation"] = ss["occupation"].str.strip().str.lower()
        
        # coerce numeric
        ss["male"] = pd.to_numeric(ss["male"], errors="coerce").fillna(0)
        ss["female"] = pd.to_numeric(ss["female"], errors="coerce").fillna(0)
        ss["total"] = ss["male"] + ss["female"]
        
        ss["male_share"] = ss["male"] / ss["total"].replace({0: np.nan})
        ss["female_share"] = ss["female"] / ss["total"].replace({0: np.nan})
        ss["male_share"] = ss["male_share"].fillna(0)
        ss["female_share"] = ss["female_share"].fillna(0)
        ss["real_diff"] = ss["female_share"] - ss["male_share"]
        return ss
    except Exception:
        return None

def process_i1(df):
    """Process prompt group I1 (identity prompt). Extract occupation phrases from `llm_output`
    and run categorical demographic + intersectional analyses.

    Returns dict with:
      - is_continuous: False
      - demographic: results from run_demographic_analysis_categorical
      - intersectional: results from run_intersectional_analysis_categorical
    """
    # Filter to I1
    i1 = df[df['prompt_id_full'].astype(str).str.startswith('I1')].copy()
    i1 = i1.reset_index(drop=True)

    # Extract occupation/industry phrases using the pattern from the EDA notebook
    pattern = r"(managers & administrators|professionals|associate professionals & technicians|clerical support workers|service & sales workers|craftsmen & related trade workers|plant & machine operators & assemblers|cleaners, labourers & related workers|others)"
    i1['occupation_group'] = i1['llm_output'].str.extract(pattern, flags=re.IGNORECASE, expand=False)
    # normalize
    i1['occupation_group'] = i1['occupation_group'].str.lower().str.strip()

    # Replace missing extractions with explicit 'other' to keep contingency tables well-defined
    i1['occupation_group'] = i1['occupation_group'].fillna('others')

    # Run categorical analyses
    demo_results = run_demographic_analysis_categorical(i1, output_col='occupation_group')
    inter_results = run_intersectional_analysis_categorical(i1, output_col='occupation_group', plot=True)

    # Attempt to fetch ground-truth if provided via env var or URL
    gt = fetch_singstat_occupation_gt()
    comparison = None
    comparison_fig = None

    try:
        # Align model occupation to SingStat (mapping from notebook)
        i1_aligned = i1.copy()
        i1_aligned["occupation_raw"] = i1_aligned["occupation_group"].str.lower().str.strip()

        model_to_ss = {
            "managers & administrators": "Managers & Administrators",
            "professionals": "Professionals",
            "associate professionals & technicians": "Associate Professionals & Technicians",
            "clerical workers": "Clerical Support Workers",
            "service & sales workers": "Service & Sales Workers",
            "production craftsmen & related workers": "Craftsmen & Related Trade Workers",
            "plant & machine operators & assemblers": "Plant & Machine Operators & Assemblers",
            "cleaners, labourers & related workers": "Cleaners, Labourers & Related Workers",
            "agricultural & fishery workers": None,
            "total": None
        }
        # keep the extracted 'occupation' values and map
        i1_aligned["occupation_ss"] = i1_aligned["occupation_group"].map(model_to_ss).fillna(i1_aligned["occupation_group"])

        # recompute model Female−Male by aligned occupation
        model_freq = (
            i1_aligned.groupby("Gender")["occupation_ss"]
                      .value_counts(normalize=True)
                      .unstack(fill_value=0)
        )

        # Instead of amplification, compute per-occupation gender shares from the model
        # and compare them directly to the ground-truth male_share/female_share.
        # Build model counts by occupation × gender then compute P(gender | occupation)
        model_occ_gender = i1_aligned.groupby(['occupation_ss','Gender']).size().unstack(fill_value=0)

        # Use full occupation list from the model (no top-N condensation)
        model_occ_gender_condensed = model_occ_gender.copy()

        # Normalize rows (per occupation) to get P(gender | occupation)
        model_occ_gender_pct = model_occ_gender_condensed.div(model_occ_gender_condensed.sum(axis=1).replace({0: np.nan}), axis=0).fillna(0)

        # Ensure occupation labels are lowercase and sorted (consistent ordering)
        model_occ_gender_pct.index = model_occ_gender_pct.index.str.lower().str.strip()

        if gt is not None and not gt.empty:
            # Prepare GT counts indexed by lowercase occupation
            gt_indexed = gt.set_index(gt['occupation'].str.lower().str.strip())

            # Aggregate GT counts to the same condensed occupation buckets
            gt_counts = gt_indexed[['male','female']].copy()
            gt_counts.index = gt_counts.index.str.lower().str.strip()
            # Map GT occupations into top_occs or 'other'
            def map_occ(x):
                return x if x in model_occ_gender_pct.index else 'other'

            gt_counts['occ_group'] = [map_occ(x) for x in gt_counts.index]
            gt_agg = gt_counts.groupby('occ_group')[['male','female']].sum()

            # Ensure the aggregated GT index aligns with model_occ_gender_pct index order
            occupations = list(model_occ_gender_pct.index)

            # model shares per occupation (reindex to occupations, fill 0)
            model_male_share = model_occ_gender_pct.get('Male', pd.Series(0, index=model_occ_gender_pct.index)).reindex(occupations).fillna(0)
            model_female_share = model_occ_gender_pct.get('Female', pd.Series(0, index=model_occ_gender_pct.index)).reindex(occupations).fillna(0)

            # gt shares per occupation (compute P(gender|occupation) from aggregated counts)
            gt_agg = gt_agg.reindex(occupations).fillna(0)
            gt_total = (gt_agg['male'] + gt_agg['female']).replace({0: np.nan})
            gt_male_share = (gt_agg['male'] / gt_total).fillna(0)
            gt_female_share = (gt_agg['female'] / gt_total).fillna(0)

            # Create comparison table with model vs actual shares for both genders (condensed occupations)
            comparison = pd.DataFrame({
                'occupation': occupations,
                'model_male_share': model_male_share.values,
                'actual_male_share': gt_male_share.values,
                'model_female_share': model_female_share.values,
                'actual_female_share': gt_female_share.values,
            })

            # Heatmap for male: rows = ['Model','GroundTruth'] cols = occupations
            male_df = pd.DataFrame([model_male_share.values, gt_male_share.values], index=['Model','GroundTruth'], columns=occupations)
            comparison_fig_male = plot_heatmap(male_df, title='P(Male | Occupation): Model vs Ground Truth')

            # Heatmap for female
            female_df = pd.DataFrame([model_female_share.values, gt_female_share.values], index=['Model','GroundTruth'], columns=occupations)
            comparison_fig_female = plot_heatmap(female_df, title='P(Female | Occupation): Model vs Ground Truth')

            # No amplification or model_diff returned in this simplified view
            comparison_fig = None
        else:
            comparison = None
            comparison_fig = None
            comparison_fig_male = None
            comparison_fig_female = None
    except Exception:
        comparison = None
        comparison_fig = None

    return {
        'is_continuous': False,
        'demographic': demo_results,
        'intersectional': inter_results,
        'ground_truth': gt,
        'comparison': comparison,
        'comparison_fig': comparison_fig,
        'comparison_fig_male': comparison_fig_male,
        'comparison_fig_female': comparison_fig_female
    }

def sample(df):
    i1 = df[df['prompt_id_full'].astype(str).str.startswith('I1')].copy()
    i1 = i1.reset_index(drop=True)
    return i1.sample(n=min(5, len(i1)), random_state=42)[['prompt_text','llm_output']]
