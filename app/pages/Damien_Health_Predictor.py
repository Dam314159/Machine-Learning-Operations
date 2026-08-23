import json
from pathlib import Path

import pandas as pd
import streamlit as st
from omegaconf import OmegaConf
from pycaret import classification


@st.cache_resource
def load_hydra_config():
    project_root = Path(__file__).resolve().parent.parent.parent
    conf_path = project_root / "conf" / "health_prediction_config.yaml"

    if not conf_path.exists():
        return None, None

    return OmegaConf.load(conf_path), project_root


@st.cache_resource
def get_models(folder_path: Path):
    if not folder_path.exists():
        return None

    with open(folder_path / "model_metrics.json", "r") as f:
        metrics = json.load(f)

    return {entry.stem.replace("_", " ").replace("-", "'"): classification.load_model(entry.with_suffix("")) for entry in folder_path.glob("*.pkl")}, metrics


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
    input_df[yes_no_columns] = input_df[yes_no_columns].replace({"Yes": 1, "No": 0, True: 1, False: 0})

    if "Blood Pressure" in input_df.columns:
        input_df["Blood Pressure_Low"] = (input_df["Blood Pressure"] == "Low").astype(int)
        input_df["Blood Pressure_Normal"] = (input_df["Blood Pressure"] == "Normal").astype(int)
        input_df = input_df.drop(columns=["Blood Pressure"])

    return input_df


cfg, project_root = load_hydra_config()

st.title("Healthcare Disease Predictor")
st.write("This application predicts whether or not the patient has a certain disease based on age, BMI, pre-existing conditions, and lifestyle habits.")
st.write("DISCLAIMER: This is not meant to be taken as medical advice.")

if cfg is None:
    st.error("Hydra configuration file not found.")
    st.stop()

model_folder = project_root / cfg.model_path
dataset_path = project_root / cfg.bronze_dataset_path
models, metrics = get_models(model_folder)
data = get_data(dataset_path)

if models is None:
    st.error(f"Model folder not found at `{model_folder}`.")
    st.stop()

if data is None:
    st.error(f"Dataset not found at `{dataset_path}`.")
    st.stop()

st.subheader("Model Performance (AUC)")
ordered_metrics = sorted(
    metrics.items(),
    key=lambda item: (item[0] != "Disease", item[0]),
)

st.metric(
    label=ordered_metrics[0][0],
    value=f"{ordered_metrics[0][1]:.1%}",
)

for row_start in range(1, len(ordered_metrics), 5):
    metric_columns = st.columns(5)
    for column, (name, auc) in zip(metric_columns, ordered_metrics[row_start : row_start + 5]):
        with column:
            st.metric(label=name, value=f"{auc:.1%}")


tab1, tab2 = st.tabs(["Single Input", "Batch Upload (CSV)"])

with tab1:
    st.write("Fill in the details below to generate a health prediction.")

    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", min_value=18, max_value=100, value=18)
        blood_pressure = st.selectbox("Blood Pressure", options=["High", "Normal", "Low"])
        smoking = st.checkbox("Smoking")
        family_history = st.checkbox("Family History")

    with col2:
        bmi = st.number_input("BMI", min_value=10.0, max_value=50.0, value=10.0, step=0.1)
        cholesterol = st.selectbox("Cholesterol", options=data["Cholesterol"].unique())
        alcohol = st.checkbox("Alcohol Consumption")

    with col3:
        gender = st.selectbox("Gender", options=data["Gender"].unique())
        glucose = st.selectbox("Glucose", options=data["Glucose"].unique())
        exercise = st.checkbox("Exercise")

    if st.button("Predict Diseases", type="primary", key="single_predict"):
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
        input_df = preprocess_health_data(pd.DataFrame([input_data]))

        ordered_models = sorted(
            models.items(),
            key=lambda item: (item[0] != "Disease", item[0]),
        )

        def display_prediction_metric(name, model, container):
            prediction_df = classification.predict_model(model, data=input_df)
            prediction = prediction_df["prediction_label"].iloc[0]
            prediction_text = "Yes" if int(prediction) == 1 else "No"
            score = prediction_df.get("prediction_score")

            with container:
                st.metric(
                    label=name,
                    value=prediction_text,
                    delta=(f"Score: {float(score.iloc[0]):.1%}" if score is not None else "Score unavailable"),
                )

        st.subheader("Overall Disease")
        display_prediction_metric(
            ordered_models[0][0],
            ordered_models[0][1],
            st.container(),
        )

        st.subheader("Individual Conditions")
        for row_start in range(1, len(ordered_models), 5):
            metric_columns = st.columns(5)
            for column, (name, model) in zip(metric_columns, ordered_models[row_start : row_start + 5]):
                display_prediction_metric(name, model, column)

with tab2:
    st.write("Upload a CSV file containing multiple patient records.")
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
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="batch_uploader")

    if uploaded_file is not None:
        try:
            batch_df = pd.read_csv(uploaded_file)
            batch_df.columns = batch_df.columns.str.strip()
            batch_features = batch_df.drop(columns=target_columns, errors="ignore")
            batch_features = preprocess_health_data(batch_features)

            st.subheader("Uploaded Data Preview")
            st.dataframe(batch_features.head(), width="stretch")

            if st.button("Generate Batch Predictions", type="primary"):
                with st.spinner("Processing batch..."):
                    results = batch_df.copy()
                    for name, model in models.items():
                        prediction_df = classification.predict_model(model, data=batch_features)
                        results[f"{name} Prediction"] = prediction_df["prediction_label"].map({0: "No", 1: "Yes"}).to_numpy()
                        if "prediction_score" in prediction_df.columns:
                            results[f"{name} Score"] = prediction_df["prediction_score"].to_numpy()

                    st.subheader("Batch Prediction Results")
                    st.dataframe(results, width="stretch")
                    st.download_button(
                        "Download Predictions",
                        data=results.to_csv(index=False).encode("utf-8"),
                        file_name="health_predictions.csv",
                        mime="text/csv",
                    )
        except Exception as error:
            st.error(f"An error occurred: {error}")
