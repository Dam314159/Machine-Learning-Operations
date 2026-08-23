import os

import pandas as pd
import streamlit as st
from hydra import compose
from hydra.core.global_hydra import GlobalHydra
from hydra.initialize import initialize_config_dir
from pycaret.regression import load_model, predict_model


# Load hydra
@st.cache_resource
def load_hydra_config():
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_script_dir, "..", ".."))
    conf_dir = os.path.join(project_root, "conf")
    if not os.path.exists(conf_dir):
        return None, None

    GlobalHydra.instance().clear()
    try:
        with initialize_config_dir(config_dir=conf_dir, version_base=None):
            cfg = compose(config_name="AI_Jobs_config")
    finally:
        GlobalHydra.instance().clear()

    return cfg, project_root

# Load model
@st.cache_resource
def get_model(model_path):
    model_file = f"{model_path}.pkl"
    if not os.path.exists(model_file):
        return None
    return load_model(model_path)

# Load dataset for form values
@st.cache_data
def get_dropdown_options(dataset_path):
    if not os.path.exists(dataset_path):
        return None
    df = pd.read_csv(dataset_path, sep=None, engine='python')
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    return df

# Load hydra config and project root
cfg, project_root = load_hydra_config()

# Page UI
st.title("Global AI Jobs Salary Predictor")
st.markdown("This application predicts the expected **Salary (USD)** for AI and Data professionals based on various job, company, and economic factors.")

if cfg is None:
    st.error("Hydra Configuration file not found at `conf/AI_Jobs_config.yaml`!")
    st.stop()

# Convert relative paths from YAML to absolute paths using the project root
abs_model_path = os.path.join(project_root, cfg.model_path)
abs_dataset_path = os.path.join(project_root, cfg.dataset_path)

# Load assets using the absolute paths
model = get_model(abs_model_path)
df_original = get_dropdown_options(abs_dataset_path)

if model is None:
    st.error(f"Model file not found at `{abs_model_path}.pkl`! Please check your Hydra config path.")
    st.stop()

if df_original is None:
    st.error(f"Dataset not found at `{abs_dataset_path}`! Please check your Hydra config path.")
    st.stop()

# Use tabs instead of sidebar radio for a cleaner multipage layout
tab1, tab2 = st.tabs(["Single Input", "Batch Upload (CSV)"])

# Tab 1 - single input prediction
with tab1:
    st.write("Fill in the job details below to generate a real-time salary prediction.")

    # Helper function to sync inputs with custom validation
    def num_input_slider(label, min_val, max_val, step, key, fmt="%d"):
        # Initialize state if missing
        if f"{key}_s" not in st.session_state:
            st.session_state[f"{key}_s"] = min_val
        if f"{key}_n" not in st.session_state:
            st.session_state[f"{key}_n"] = min_val

        # Pre-render clamping: Check if the user typed an out-of-bounds value in the previous run
        current_val = st.session_state[f"{key}_n"]
        clamped = False
        clamp_val = current_val
        
        if current_val > max_val:
            clamp_val = max_val
            clamped = True
        elif current_val < min_val:
            clamp_val = min_val
            clamped = True
            
        # If it was out of bounds, force the UI state to the clamped value
        if clamped:
            st.session_state[f"{key}_n"] = clamp_val
            st.session_state[f"{key}_s"] = clamp_val

        # Callbacks to keep slider and number input synced
        def update_num():
            st.session_state[f"{key}_n"] = st.session_state[f"{key}_s"]
        def update_slide():
            st.session_state[f"{key}_s"] = st.session_state[f"{key}_n"]

        c_slide, c_num = st.columns([0.65, 0.35])
        with c_slide:
            st.slider(label, min_val, max_val, st.session_state[f"{key}_s"], step=step, key=f"{key}_s", on_change=update_num, format=fmt)
        with c_num:
            st.number_input(" ", step=step, key=f"{key}_n", on_change=update_slide, format=fmt, label_visibility="collapsed")
        
        # Show custom error message if a value was just clamped
        if clamped:
            st.error(f"Value out of range. It has been automatically changed to {clamp_val}.")
            
        return st.session_state[f"{key}_n"]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        country = st.selectbox("Country", options=df_original['country'].unique())
        job_role = st.selectbox("Job Role", options=df_original['job_role'].unique())
        ai_spec = st.selectbox("AI Specialization", options=df_original['ai_specialization'].unique())
        exp_level = st.selectbox("Experience Level", options=['Entry', 'Mid', 'Senior', 'Lead'])
        exp_years = num_input_slider("Years of Experience", 0, 80, 1, "exp_years")
        education = st.selectbox("Education Required", options=df_original['education_required'].unique())
        industry = st.selectbox("Industry", options=df_original['industry'].unique())
        company_size = st.selectbox("Company Size", options=['Startup', 'Small', 'Medium', 'Large', 'Enterprise'])
    with col2:
        interview_rounds = num_input_slider("Interview Rounds", 0, 15, 1, "interview_rounds")
        year = num_input_slider("Year", 2020, 2030, 1, "year")
        work_mode = st.selectbox("Work Mode", options=['Remote', 'Hybrid', 'Onsite'])
        weekly_hours = num_input_slider("Weekly Hours", 0.0, 168.0, 0.1, "weekly_hours", fmt="%.1f")
        company_rating = num_input_slider("Company Rating", 0.00, 5.00, 0.01, "company_rating", fmt="%.2f") 
        job_openings = num_input_slider("Job Openings", 0, 100, 1, "job_openings")
        hiring_difficulty = num_input_slider("Hiring Difficulty Score", 0.00, 100.00, 0.01, "hiring_diff", fmt="%.2f")
        layoff_risk = num_input_slider("Layoff Risk", 0.00, 1.00, 0.01, "layoff_risk", fmt="%.2f")
    with col3:
        ai_adoption = num_input_slider("AI Adoption Score", 0, 100, 1, "ai_adoption")
        company_funding = num_input_slider("Company Funding (Billion USD)", 0.00, 10.00, 0.01, "company_funding", fmt="%.2f")
        economic_index = num_input_slider("Economic Index", 0.00, 100.00, 0.01, "economic_index", fmt="%.2f")
        ai_maturity = num_input_slider("AI Maturity Years", 0, 30, 1, "ai_maturity")
        offer_acceptance = num_input_slider("Offer Acceptance Rate", 0.00, 100.00, 0.01, "offer_acceptance", fmt="%.2f")
        tax_rate = num_input_slider("Tax Rate Percent", 0.0, 100.0, 0.1, "tax_rate", fmt="%.1f")
        vacation_days = num_input_slider("Vacation Days", 0, 180, 1, "vacation_days")
        skill_demand = num_input_slider("Skill Demand Score", 0, 100, 1, "skill_demand")
    with col4:
        automation_risk = num_input_slider("Automation Risk", 0, 100, 1, "automation_risk")
        job_security = num_input_slider("Job Security Score", 0, 100, 1, "job_security")
        career_growth = num_input_slider("Career Growth Score", 0, 100, 1, "career_growth")
        work_life_balance = num_input_slider("Work-Life Balance Score", 0, 100, 1, "work_life_balance")
        promotion_speed = num_input_slider("Promotion Speed", 0, 100, 1, "promotion_speed")
        salary_percentile = num_input_slider("Salary Percentile", 0, 100, 1, "salary_percentile")
        cost_of_living = num_input_slider("Cost of Living Index", 0.00, 10.00, 0.01, "cost_of_living", fmt="%.1f")
        employee_satisfaction = num_input_slider("Employee Satisfaction", 0, 100, 1, "employee_satisfaction")

    # Button to trigger prediction
    if st.button("Predict Salary", type="primary", key="single_predict"):
        with st.spinner("Calculating..."):
            input_data = {
                'country': country,
                'job_role': job_role,
                'ai_specialization': ai_spec,
                'experience_level': exp_level,
                'experience_years': exp_years,
                'education_required': education,
                'industry': industry,
                'company_size': company_size,
                'interview_rounds': interview_rounds,
                'year': year,
                'work_mode': work_mode,
                'weekly_hours': weekly_hours,
                'company_rating': company_rating,
                'job_openings': job_openings,
                'hiring_difficulty_score': hiring_difficulty,
                'layoff_risk': layoff_risk,
                'ai_adoption_score': ai_adoption,
                'company_funding_billion': company_funding,
                'economic_index': economic_index,
                'ai_maturity_years': ai_maturity,
                'offer_acceptance_rate': offer_acceptance,
                'tax_rate_percent': tax_rate,
                'vacation_days': vacation_days,
                'skill_demand_score': skill_demand,
                'automation_risk': automation_risk,
                'job_security_score': job_security,
                'career_growth_score': career_growth,
                'work_life_balance_score': work_life_balance,
                'promotion_speed': promotion_speed,
                'salary_percentile': salary_percentile,
                'cost_of_living_index': cost_of_living,
                'employee_satisfaction': employee_satisfaction
            }
            
            # Convert to dataframe
            input_df = pd.DataFrame([input_data])
            
            # Predict
            prediction_df = predict_model(model, data=input_df)
            predicted_salary = prediction_df['prediction_label'].iloc[0]
            
            # Display result
            st.success("Prediction Successful!")
            st.markdown(f"""
            <div style="padding:20px;border-radius:10px;background-color:#f0f2f6;text-align:center;">
                <h3 style="color:#1f77b4;">Estimated Annual Salary</h3>
                <h1 style="font-size:48px;color:#0a0a0a;">${predicted_salary:,.2f} USD</h1>
            </div>
            """, unsafe_allow_html=True)

# Tab 2 - batch prediction
with tab2:
    st.write("Upload a CSV file containing multiple job entries to generate bulk predictions.")
    st.info("**Note:** The CSV must contain the same columns as the training dataset. If the `salary_usd` or `bonus_usd` columns are present, they will be automatically ignored/removed to prevent data leakage.")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="batch_uploader")

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file, sep=None, engine='python')
            batch_df.columns = batch_df.columns.str.strip()
            st.subheader("Uploaded Data Preview")
            st.dataframe(batch_df.head(5), use_container_width=True)
            # Clean batch data (drop target and leakage features if they exist)
            cols_to_drop = ['salary_usd', 'bonus_usd', 'id']
            for col in cols_to_drop:
                if col in batch_df.columns:
                    batch_df = batch_df.drop(col, axis=1)
            
            # Predict
            if st.button("Generate Batch Predictions", type="primary", key="batch_predict"):
                with st.spinner("Processing batch..."):
                    predictions = predict_model(model, data=batch_df)
                    st.subheader("Predictions Result")
                    # Format the prediction column for display
                    predictions['Predicted_Salary_USD'] = predictions['prediction_label'].apply(lambda x: f"${x:,.2f}")
                    # Show relevant output
                    display_cols = predictions.columns.tolist()
                    # Hide raw prediction_label
                    if 'prediction_label' in display_cols:
                        display_cols.remove('prediction_label')
                    st.dataframe(predictions[display_cols], use_container_width=True)
                    # Provide download button for results
                    csv = predictions.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Predictions as CSV",
                        data=csv,
                        file_name='salary_predictions.csv',
                        mime='text/csv'
                    )
                    st.success("Batch prediction completed successfully!")

        except Exception as e:
            st.error(f"An error occurred while processing the file: {e}")