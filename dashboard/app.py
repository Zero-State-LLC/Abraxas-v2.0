import streamlit as st

from core.intelligence.intelligence_system import IntelligenceSystem

from workflows.la_ca_adaptive_pipeline import LACAAdaptivePipeline

st.set_page_config(page_title="Abraxas Intelligence Dashboard", layout="wide")
st.title("Abraxas v2.0 Intelligence Dashboard")

# Sidebar controls
st.sidebar.header("Configuration")
calibration_method = st.sidebar.selectbox(
    "Calibration Method",
    ["beta", "isotonic", "platt", "dirichlet"],
    index=0
)

# Initialize systems
@st.cache_resource
def get_system():
    return IntelligenceSystem(config={"calibration_method": calibration_method})

@st.cache_resource
def get_pipeline():
    return LACAAdaptivePipeline(config={"calibration_method": calibration_method})

system = get_system()
pipeline = get_pipeline()

# Main tabs
tab1, tab2, tab3 = st.tabs(["Process Signal", "Dashboard", "Reports"])

with tab1:
    st.header("Process New Signal")

    signal_type = st.selectbox("Signal Type", pipeline.SUPPORTED_CATEGORIES)
    value = st.number_input("Value", value=50.0)
    severity = st.slider("Severity", 0.0, 1.0, 0.6)
    velocity = st.slider("Velocity", -1.0, 1.0, 0.2)
    confidence = st.slider("Confidence", 0.0, 1.0, 0.6)

    target = st.number_input("Target (optional for Brier)", value=0.3, step=0.05)

    if st.button("Process Signal"):
        signal = {
            "value": value,
            "severity": severity,
            "velocity": velocity,
            "confidence": confidence
        }
        result = pipeline.process_by_type(signal_type, signal, target=target if target > 0 else None)
        st.json(result)

with tab2:
    st.header("System Dashboard")

    status = pipeline.get_status()
    st.metric("Signals Processed", status.get("signals_processed", 0))

    brier_trend = status.get("brier_trend", {})
    if brier_trend.get("mean_brier"):
        st.metric("Mean Brier Score", f"{brier_trend['mean_brier']:.4f}")
        st.metric("Latest Brier Score", f"{brier_trend['latest_brier']:.4f}")

    st.subheader("Recent Performance")
    perf = status.get("recent_performance", {})
    if perf.get("anomaly_rate") is not None:
        st.write(f"Anomaly Rate: {perf['anomaly_rate']:.2%}")

with tab3:
    st.header("Reports & Diagnostics")

    if st.button("Generate Latest Report"):
        if pipeline.signal_history:
            latest = pipeline.signal_history[-1]
            from core.intelligence.brier_visualization import generate_text_report
            report_text = generate_text_report(latest.get("result", {}))
            st.text(report_text)
        else:
            st.info("No signals processed yet.")

st.sidebar.markdown("---")
st.sidebar.info("Powered by Abraxas IntelligenceSystem v2.2.0")
