from pathlib import Path

import pandas as pd
import streamlit as st
from omegaconf import OmegaConf
from pycaret import classification


# Load hydra
@st.cache_resource
def load_hydra_config():
    current_script_dir = Path(__file__).resolve().parent
    project_root = current_script_dir.parent.parent
    conf_dir = project_root / "conf"

    if not conf_dir.exists():
        return None, None

    cfg = OmegaConf.load(conf_dir / "health_prediction_config.yaml")
    return cfg, project_root


# Load model
@st.cache_resource
def get_models(folder_path: Path):
    if not folder_path.exists():
        return None

    models = {}

    for entry in folder_path.iterdir():
        if entry.suffix != ".pkl":
            continue

        model_name = entry.stem.replace("_", " ").replace("-", "'")
        models[model_name] = classification.load_model(entry.with_suffix(""))

    return models


# Load dataset
@st.cache_data
def get_data(dataset_path: Path):
    if not dataset_path.exists():
        return None

    return pd.read_csv(dataset_path)

def preprocess_health_data(input_df):
    input_df = input_df.copy()

    input_df["Gender"] = input_df["Gender"].replace({"Male": 0, "Female": 1})

    input_df[["Cholesterol", "Glucose"]] = input_df[["Cholesterol", "Glucose"]].replace({"Normal": 0, "High": 1})

    yes_no_columns = [
        "Smoking",
        "Alcohol Consumption",
        "Exercise",
        "Family History",
    ]
    input_df[yes_no_columns] = input_df[yes_no_columns].replace({False: 0, True: 1})

    # One-hot encode every blood-pressure category consistently.
    input_df["Blood Pressure_Low"] = (input_df["Blood Pressure"] == "Low").astype(int)

    input_df["Blood Pressure_Normal"] = (input_df["Blood Pressure"] == "Normal").astype(int)

    # High is the reference category: Low=0 and Normal=0 means High.
    input_df = input_df.drop(columns=["Blood Pressure"])

    return input_df


# Load hydra config and project root
cfg, project_root = load_hydra_config()

# Page UI
st.title("Healthcare Disease Predictor")
st.write("This application predicts the whether or not the patient has a certain disease based on age, bmi, pre-existing conditions and lifestyle habits.")
st.write("DISCLAIMER: This is not meant to be taken as medical advice.")

if cfg is None:
    st.error("Hydra Configuration file not found at `conf/AI_Jobs_config.yaml`!")
    st.stop()

# Convert relative paths from YAML to absolute paths using the project root
abs_model_path = project_root / cfg.model_path
abs_dataset_path = project_root / cfg.bronze_dataset_path

# Load assets using the absolute paths
models = get_models(abs_model_path)
data = get_data(abs_dataset_path)

if models is None:
    st.error(f"Model folder not found at `{abs_model_path}`! Please check your Hydra config path.")
    st.stop()

if data is None:
    st.error(f"Dataset not found at `{abs_dataset_path}`! Please check your Hydra config path.")
    st.stop()

# Use tabs instead of sidebar radio for a cleaner multipage layout
tab1, tab2 = st.tabs(["Single Input", "Batch Upload (CSV)"])

# Tab 1 - single input prediction
with tab1:
    st.write("Fill in the details below to generate a health prediction.")

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
            st.slider(label, min_val, max_val, step=step, key=f"{key}_s", on_change=update_num, format=fmt)

        with c_num:
            st.number_input(" ", step=step, key=f"{key}_n", on_change=update_slide, format=fmt, label_visibility="collapsed")

        # Show custom error message if a value was just clamped
        if clamped:
            st.error(f"Value out of range. It has been automatically changed to {clamp_val}.")

        return st.session_state[f"{key}_n"]

    col1, col2, col3 = st.columns(3)
    with col1:
        age = num_input_slider("Age", 18, 100, 1, "age")
        blood_pressure = st.selectbox("Blood Pressure", options=["High", "Normal", "Low"])
        smoking = st.checkbox("Smoking")
        family_history = st.checkbox("Family History")

    with col2:
        bmi = num_input_slider("BMI", 10.0, 50.0, 0.1, "bmi", "%.1f")
        cholesterol = st.selectbox("Cholesterol", options=data["Cholesterol"].unique())
        alcohol = st.checkbox("Alcohol Consumption")

    with col3:
        gender = st.selectbox("Gender", options=data["Gender"].unique())
        glucose = st.selectbox("Glucose", options=data["Glucose"].unique())
        exercise = st.checkbox("Exercise")

    # Button to trigger prediction
    if st.button("Predict Diseases", type="primary", key="single_predict"):
        with st.spinner("Predicting..."):
            input_data = {
                "Age": age,
                "Gender": gender,
                "Cholesterol": cholesterol,
                "Glucose": glucose,
                "Smoking": smoking,
                "Alcohol Consumption": alcohol,
                "Exercise": exercise,
                "BMI": bmi,
                "Family History": family_history,
                "Blood Pressure": blood_pressure,
            }

        # Convert and format dataframe
        input_df = preprocess_health_data(pd.DataFrame([input_data]))

        # Predictions
        def display_prediction_metric(name, model, container):
            prediction_df = classification.predict_model(model, data=input_df)

            prediction = prediction_df["prediction_label"].iloc[0]
            prediction_text = "Yes" if int(prediction) == 1 else "No"

            score = None
            if "prediction_score" in prediction_df.columns:
                score = float(prediction_df["prediction_score"].iloc[0])

            with container:
                st.metric(
                    label=name,
                    value=prediction_text,
                    delta=(f"Score: {score:.1%}" if score is not None else "Score unavailable"),
                )

        # Ensure Disease is first
        ordered_models = sorted(
            models.items(),
            key=lambda item: (item[0] != "Disease", item[0]),
        )

        disease_model = ordered_models[0]
        other_models = ordered_models[1:]

        # Disease on its own row
        st.subheader("Overall Disease")
        disease_container = st.container()
        display_prediction_metric(
            disease_model[0],
            disease_model[1],
            disease_container,
        )

        # Remaining models in rows of five
        st.subheader("Individual Conditions")

        for row_start in range(0, len(other_models), 5):
            row_models = other_models[row_start : row_start + 5]
            metric_columns = st.columns(5)

            for column, (name, model) in zip(metric_columns, row_models):
                display_prediction_metric(name, model, column)

# Tab 2 - batch prediction
with tab2:
    st.write("Upload a CSV file containing multiple patient information entries to generate bulk predictions.")
    st.info("**Note:** The CSV must contain the same columns as the training dataset. If any of the target columns are present, they will be automatically ignored/removed to prevent data leakage.")
    target_columns = [
        "Disease",
        "Heart Disease",
        "Diabetes",
        "Stroke",
        "Kidney Disease",
        "Cancer",
        "Alzheimer's Disease",
        "COPD",
        "Liver Disease",
        "Parkinson's Disease",
        "Tuberculosis",
    ]

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type="csv",
        key="batch_uploader",
    )

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            batch_df.columns = batch_df.columns.str.strip()

            # Remove target columns if they are included in the upload.
            batch_features = batch_df.drop(
                columns=target_columns,
                errors="ignore",
            )
            batch_features = preprocess_health_data(batch_features)

            st.subheader("Uploaded Data Preview")
            st.dataframe(batch_features.head(), width="stretch")

            if st.button("Generate Batch Predictions", type="primary"):
                with st.spinner("Processing batch..."):
                    results = batch_features.copy()

                    for name, model in models.items():
                        prediction_df = classification.predict_model(
                            model,
                            data=batch_features,
                        )

                        results[f"{name} Prediction"] = prediction_df["prediction_label"].replace({0: "No", 1: "Yes"}).values

                        if "prediction_score" in prediction_df.columns:
                            results[f"{name} Score"] = prediction_df["prediction_score"].values

                    st.subheader("Batch Prediction Results")
                    st.dataframe(results, width="stretch")

                    csv = results.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "Download Predictions",
                        data=csv,
                        file_name="health_predictions.csv",
                        mime="text/csv",
                    )

        except Exception as error:
            st.error(f"An error occurred: {error}")
