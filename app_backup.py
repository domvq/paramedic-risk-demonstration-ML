import streamlit as st
import pandas as pd
import joblib

MODEL_PATH = "model.joblib"

st.set_page_config(
    page_title="Paramedic AI",
    page_icon="🚑",
    layout="centered"
)

st.title("🚑 Paramedic AI")
st.caption("Clinical deterioration risk demonstration")

st.warning("DEMO ONLY — NOT FOR CLINICAL DECISION MAKING")

st.header("Patient Vital Signs")

age = st.number_input("Age", min_value=0, max_value=120, value=60)
heart_rate = st.number_input("Heart Rate (bpm)", min_value=20.0, max_value=250.0, value=80.0)
systolic_bp = st.number_input("Systolic BP (mmHg)", min_value=40.0, max_value=300.0, value=120.0)
diastolic_bp = st.number_input("Diastolic BP (mmHg)", min_value=20.0, max_value=200.0, value=70.0)
respiratory_rate = st.number_input("Respiratory Rate", min_value=0.0, max_value=100.0, value=16.0)
spo2 = st.number_input("SpO₂ (%)", min_value=50.0, max_value=100.0, value=98.0)
temperature = st.number_input("Temperature (°F)", min_value=80.0, max_value=110.0, value=98.6)

if st.button("Assess Risk", type="primary"):

    try:
        model = joblib.load(MODEL_PATH)

        data = pd.DataFrame([{
            "age": age,
            "heart_rate": heart_rate,
            "systolic_bp": systolic_bp,
            "diastolic_bp": diastolic_bp,
            "respiratory_rate": respiratory_rate,
            "spo2": spo2,
            "temperature": temperature,
        }])

        probability = model.predict_proba(data)[0][1]

        st.subheader("Risk Estimate")
        st.metric("Estimated probability", f"{probability:.1%}")

        if probability >= 0.50:
            st.error("HIGHER RISK")
        else:
            st.success("LOWER RISK")

        st.caption(
            "This is a machine-learning demonstration using a small "
            "MIMIC-IV demo dataset. It must not be used for patient care."
        )

    except Exception as e:
        st.error(f"Prediction error: {e}")