# app.py
import streamlit as st
import pandas as pd
from bias_metrics import *

st.set_page_config(page_title="LLM Bias Dashboard", layout="wide")
st.title("📊 LLM Bias Analysis Dashboard")

uploaded_file = st.file_uploader("Upload consolidated_prompts.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df["llm_output"] = df["llm_output"].apply(clean_output)

    # Select prompt domain: extract unique prefix before the first dash from `prompt_id_full`
    # e.g. 'I1-Singaporean-...' -> 'I1'
    if "prompt_id_full" in df.columns:
        prompt_groups = (
            df["prompt_id_full"].astype(str)
              .str.split("-", n=1)
              .str[0]
              .dropna()
              .unique()
              .tolist()
        )
        # Keep consistent ordering
        prompt_groups = sorted([g for g in prompt_groups if g != ""])
        if not prompt_groups:
            prompt_groups = ["D1"]
    else:
        prompt_groups = ["D1"]

    domain = st.selectbox("Select Prompt Group", prompt_groups, index=0)

    if st.button("Run Analysis"):
        # Dynamically call the appropriate processing function based on the selected domain.
        # Naming convention: domain 'D1' -> function `process_d1` in module `d1_processing.py`.
        func_name = f"process_{domain.lower()}"

        # 1) If function is already imported (e.g., process_d1), call it directly.
        if func_name in globals() and callable(globals()[func_name]):
            outputs = globals()[func_name](df)
        else:
            # 2) Try to import <domain>_processing and call process_<domain>
            module_name = f"{domain.lower()}_processing"
            try:
                mod = __import__(module_name)
            except ModuleNotFoundError:
                st.warning(f"No processing module found for {domain} (expected {module_name}.py).")
                st.stop()

            if not hasattr(mod, func_name) or not callable(getattr(mod, func_name)):
                st.warning(f"Module {module_name} does not define {func_name}().")
                st.stop()

            process_func = getattr(mod, func_name)
            outputs = process_func(df)

        st.success("✅ Analysis complete!")
        # --- Ground-truth comparison (if available) ---
        gt = outputs.get("ground_truth")
        comparison_fig_male = outputs.get("comparison_fig_male")
        comparison_fig_female = outputs.get("comparison_fig_female")

        show_gt = False
        if gt is not None:
            try:
                # pandas DataFrame has .empty
                show_gt = not getattr(gt, "empty", False)
            except Exception:
                show_gt = True
                
        # --- Sample Prompts and Outputs ---
        with st.expander("Show Sample Prompts and Outputs"):
            module_name = f"{domain.lower()}_processing"
            try:
                mod = __import__(module_name)
            except ModuleNotFoundError:
                st.warning(f"No processing module found for {domain} (expected {module_name}.py).")
                st.stop()
            sample_df = mod.sample(df)
            st.dataframe(sample_df, hide_index=True)

        # --- Ground-truth comparison section (show after Summary Statistics) ---
        try:
            if show_gt:
                st.subheader("📉 Ground-truth comparison (Model vs Ground Truth)")

                if comparison_fig_male is not None:
                    st.markdown("**P(Male | Occupation): Model vs Ground Truth**")
                    st.pyplot(comparison_fig_male, use_container_width=False)

                if comparison_fig_female is not None:
                    st.markdown("**P(Female | Occupation): Model vs Ground Truth**")
                    st.pyplot(comparison_fig_female, use_container_width=False)

                # optional comparison table
                comp_tbl = outputs.get('comparison')
                if comp_tbl is not None:
                    st.markdown("**Comparison table (model vs actual shares)**")
                    st.dataframe(comp_tbl)
        except Exception:
            st.write("Ground-truth comparison could not be rendered.")
            
        # --- Summary Section ---
        st.subheader("📈 Summary Statistics")

        # --- Create Tabs for Demographic + Intersectional Analyses ---
        demo_keys = list(outputs["demographic"].keys())
        tabs = st.tabs(demo_keys + ["Intersectional Biases"])

        is_continuous = outputs["is_continuous"]

        # --- Demographic-level tabs ---
        for i, (demo, res) in enumerate(outputs["demographic"].items()):
            with tabs[i]:
                st.markdown(f"### {demo}")
                col1, col2 = st.columns(2)

                if is_continuous:
                    # Continuous metrics
                    with col1:
                        st.metric("DBI (z)", f"{res['dbi'].values.mean():.3f}")
                        st.metric("Stat", f"{res['stat']:.3f}")
                        st.metric("p-value", f"{res['p']:.4f}")
                    with col2:
                        st.dataframe(res["grouped"])
                    st.write("**Distribution**")
                    st.pyplot(res["fig"], use_container_width=False)
                else:
                    # Categorical metrics
                    with col1:
                        st.metric("Chi²", f"{res['chi2']:.3f}")
                        st.metric("p-value", f"{res['p']:.4f}")
                    with col2:
                        st.write("**FDI (Fairness Deviation Index)**")
                        st.dataframe(res["fdi"])
                    st.write("**Distribution Heatmap**")
                    if "fig" in res and res["fig"] is not None:
                        st.pyplot(res["fig"], use_container_width=False)
                    else:
                        st.dataframe(res["ct_pct"])
                    st.write("**Jensen–Shannon Divergence (JSD)**")
                    st.dataframe(res["jsd"])
        
        # --- Intersectional-level results ---
        with tabs[-1]:
            st.markdown("### 🔀 Intersectional Biases")
            inter = outputs["intersectional"]

            if is_continuous:
                # Continuous: show ANOVA table + intersectional DBI
                st.subheader("Three-way ANOVA")
                st.dataframe(inter["anova_table"])
                if "mixedlm_summary" in inter:
                    st.text(inter["mixedlm_summary"])

                st.subheader("Intersectional DBI")
                st.dataframe(inter["dbi_intersection"])
            else:
                # Loop through each intersection
                for inter_name, res in inter.items():
                    if inter_name in ["multiway", "idi_all"]:
                        continue
                    st.markdown(f"#### {inter_name}")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Chi²", f"{res['chi2']:.3f}")
                        st.metric("p-value", f"{res['p']:.6f}")
                    with col2:
                        st.write("**FDI (Fairness Deviation Index)**")
                        st.dataframe(res["fdi"])

                    st.write("**Distribution Heatmap**")
                    if "fig" in res and res["fig"] is not None:
                        st.pyplot(res["fig"], use_container_width=False)
                    else:
                        st.dataframe(res["ct_pct"])

                # --- Multi-way Crosstab ---
                st.markdown("### 🌐 Multi-way Crosstab (Nationality × Gender × Race)")
                st.dataframe(inter["multiway"]["ct"])
                st.write(
                    f"**Chi²:** {inter['multiway']['chi2']:.3f}, "
                    f"**p:** {inter['multiway']['p']:.6f}, "
                    f"**DOF:** {inter['multiway']['dof']}"
                )

                # --- Intersectional Disparity Index ---
                st.markdown("### ⚖️ Intersectional Disparity Index (IDI)")
                st.dataframe(inter["idi_all"])