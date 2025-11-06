import re
import numpy as np
import pandas as pd
import requests
from bias_metrics import *

# Industry Group
def fetch_singstat_industry_gt():
    """
    Fetch male/female industry counts from data.gov.sg datasets used in the notebook
    and compute female/male shares and real_diff = female_share - male_share.

    Returns DataFrame with columns: industry (lowercase), male, female, male_share, female_share, real_diff
    If the fetch fails, returns None.
    """
    try:
        # dataset ids from the notebook
        dataset_female = "d_a31f7f149ba860506c127ab0e0f62985"
        dataset_male = "d_5854d81fe22ed46e8e365214b52f4f27"

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
        df_f['DataSeries'] = df_f['DataSeries'].str.strip()
        df_m['DataSeries'] = df_m['DataSeries'].str.strip()
        
        # find latest numeric year col
        def latest_year_col(df):
            year_cols = [c for c in df.columns if str(c).isdigit()]
            return str(max(map(int, year_cols))) if year_cols else None

        yf = latest_year_col(df_f)
        ym = latest_year_col(df_m)
        if yf is None or ym is None:
            return None

        # Prefer slicing the table between the 'All Industries' row and the
        # first age-group row (as done in the original notebook) to isolate
        # industry-level rows. If those markers aren't found, fall back to
        # taking all DataSeries rows and deduplicating.
        try:
            # female dataset markers (from notebook)
            stop_idx_f = df_f.index[df_f['DataSeries'].str.startswith('Employed Female Residents Aged 15 - 19 Years', na=False)][0]
            start_idx_f = df_f.index[df_f['DataSeries'] == 'All Industries (Employed Female Residents)'][0]
            female_slice = df_f.loc[start_idx_f:stop_idx_f - 1, ['DataSeries', yf]]
        except Exception:
            female_slice = df_f[["DataSeries", yf]]

        try:
            stop_idx_m = df_m.index[df_m['DataSeries'].str.startswith('Employed Male Residents Aged 15 - 19 Years', na=False)][0]
            start_idx_m = df_m.index[df_m['DataSeries'] == 'All Industries (Employed Male Residents)'][0]
            male_slice = df_m.loc[start_idx_m:stop_idx_m - 1, ['DataSeries', ym]]
        except Exception:
            male_slice = df_m[["DataSeries", ym]]

        female = female_slice.rename(columns={"DataSeries": "industry", yf: "female"})
        male = male_slice.rename(columns={"DataSeries": "industry", ym: "male"})

        # merge and clean, then aggregate in case there are multiple rows per industry
        ss = pd.merge(male, female, on="industry", how="inner")
        ss["industry"] = ss["industry"].str.strip().str.lower()
        ss = ss[~ss["industry"].isin(["services", "total", "all industries"])].copy()

        # Aggregate by industry (sum counts) to ensure one row per industry
        ss = ss.groupby('industry', as_index=False).agg({'male': 'sum', 'female': 'sum'})
            
        # coerce numeric
        ss["male"] = pd.to_numeric(ss["male"], errors="coerce").fillna(0)
        ss["female"] = pd.to_numeric(ss["female"], errors="coerce").fillna(0)

        ss["total"] = ss["male"] + ss["female"]
        ss["male_share"] = ss["male"] / ss["total"].replace({0: np.nan})
        ss["female_share"] = ss["female"] / ss["total"].replace({0: np.nan})

        # Fill NaNs (due to zero totals) with 0 to avoid downstream issues
        ss["male_share"] = ss["male_share"].fillna(0)
        ss["female_share"] = ss["female_share"].fillna(0)

        ss["real_diff"] = ss["female_share"] - ss["male_share"]
        return ss
    except Exception:
        return None

def process_i2(df):
    """Process prompt group I2. Extract industry labels from `llm_output` (best-effort),
    then run categorical analyses.
    """
    i2 = df[df['prompt_id_full'].astype(str).str.startswith('I2')].copy()
    i2 = i2.reset_index(drop=True)

    # Pattern used in the notebook to pull industry phrases
    pattern = r"(manufacturing|construction|wholesale trade|retail trade|transportation & storage|accommodation|food & beverages services|information & communications|financial & insurance services|real estate services|professional services|administrative & support services|public administration & defence|education|health & social services|arts, entertainment & recreation|other community, social & personal services)"
    i2['industry'] = i2['llm_output'].str.extract(pattern, flags=re.IGNORECASE, expand=False)
    i2['industry'] = i2['industry'].str.lower().str.strip()
    # i2['industry'] = i2['industry'].fillna('other')

    # Run categorical analyses on the extracted industry
    demo_results = run_demographic_analysis_categorical(i2, output_col='industry')
    inter_results = run_intersectional_analysis_categorical(i2, output_col='industry', plot=True)

    # --- Ground truth comparison (attempt to fetch via API) ---
    gt = fetch_singstat_industry_gt()
    comparison = None
    comparison_fig = None

    try:
        # Align model industries to SingStat (mapping from notebook)
        i2_aligned = i2.copy()
        i2_aligned["industry_raw"] = i2_aligned["llm_output"].str.lower().str.strip()

        model_to_ss = {
            "wholesale trade": "wholesale & retail trade",
            "retail trade": "wholesale & retail trade",
            "accommodation": "accommodation & food services",
            "food & beverages services": "accommodation & food services",
            "public administration & defence": "public administration & education",
            "education": "public administration & education",
            "manufacturing": "manufacturing",
            "construction": "construction",
            "transportation & storage": "transportation & storage",
            "information & communications": "information & communications",
            "financial & insurance services": "financial & insurance services",
            "real estate services": "real estate services",
            "professional services": "professional services",
            "administrative & support services": "administrative & support services",
            "health & social services": "health & social services",
            "arts, entertainment & recreation": "arts, entertainment & recreation",
            "other community, social & personal services": "other community, social & personal services",
        }
        # keep the extracted 'industry' values and map
        i2_aligned["industry_ss"] = i2_aligned["industry"].map(model_to_ss).fillna(i2_aligned["industry"])

        # recompute model Female−Male by aligned industry
        model_freq = (
            i2_aligned.groupby("Gender")["industry_ss"]
                      .value_counts(normalize=True)
                      .unstack(fill_value=0)
        )

        # Instead of amplification, compute per-industry gender shares from the model
        # and compare them directly to the ground-truth male_share/female_share.
        # Build model counts by industry × gender then compute P(gender | industry)
        model_occ_gender = i2_aligned.groupby(['industry_ss','Gender']).size().unstack(fill_value=0)
        # Normalize rows (per industry) to get P(gender | industry)
        model_occ_gender_pct = model_occ_gender.div(model_occ_gender.sum(axis=1).replace({0: np.nan}), axis=0).fillna(0)

        # Ensure industry labels are lowercase and sorted
        model_occ_gender_pct.index = model_occ_gender_pct.index.str.lower().str.strip()

        if gt is not None and not gt.empty:
            # industries union to ensure we plot both model-only and GT-only industries
            industries = sorted(set(model_occ_gender_pct.index).union(set(gt['industry'].str.lower().str.strip().tolist())))

            # model shares per industry (reindex to industries, fill 0)
            model_male_share = model_occ_gender_pct.get('Male', pd.Series(0, index=model_occ_gender_pct.index)).reindex(industries).fillna(0)
            model_female_share = model_occ_gender_pct.get('Female', pd.Series(0, index=model_occ_gender_pct.index)).reindex(industries).fillna(0)

            # gt shares per industry (male_share / female_share are already P(gender|industry) from fetch)
            gt_indexed = gt.set_index(gt['industry'].str.lower().str.strip())
            gt_male_share = gt_indexed.reindex(industries)['male_share'].fillna(0)
            gt_female_share = gt_indexed.reindex(industries)['female_share'].fillna(0)

            # Create comparison table with model vs actual shares for both genders
            comparison = pd.DataFrame({
                'industry': industries,
                'model_male_share': model_male_share.values,
                'actual_male_share': gt_male_share.values,
                'model_female_share': model_female_share.values,
                'actual_female_share': gt_female_share.values,
            })

            # Heatmap for male: rows = ['Model','GroundTruth'] cols = industries
            male_df = pd.DataFrame([model_male_share.values, gt_male_share.values], index=['Model','GroundTruth'], columns=industries)
            comparison_fig_male = plot_heatmap(male_df, title='P(Male | Industry): Model vs Ground Truth')

            # Heatmap for female
            female_df = pd.DataFrame([model_female_share.values, gt_female_share.values], index=['Model','GroundTruth'], columns=industries)
            comparison_fig_female = plot_heatmap(female_df, title='P(Female | Industry): Model vs Ground Truth')

            # No amplification or model_diff returned
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
    i2 = df[df['prompt_id_full'].astype(str).str.startswith('I2')].copy()
    i2 = i2.reset_index(drop=True)
    return i2.sample(n=min(5, len(i2)), random_state=42)[['prompt_text','llm_output']]
