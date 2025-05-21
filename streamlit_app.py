import os
import sys
import re
import streamlit as st

# Add root path for imports
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Local imports
from llm.orchestrator import run_orchestration
from agents.gw_metadata import resolve_event_metadata

# Page settings
st.set_page_config(page_title="Gravitational Wave Agent", page_icon="🌌")
st.title("🔭 Gravitational Wave Detection Agent")

# Session state init
if "generated_reports" not in st.session_state:
    st.session_state.generated_reports = []

# 📄 PDF download handler
def offer_pdf_download(response_text):
    matches = re.findall(r'(?:output/)?(\d+)_report\.pdf', response_text)
    for match in matches:
        pdf_path = f"output/{match}_report.pdf"
        if os.path.exists(pdf_path) and pdf_path not in st.session_state.generated_reports:
            st.session_state.generated_reports.append(pdf_path)

# 📥 Render download buttons
def render_download_buttons():
    if st.session_state.generated_reports:
        st.markdown("### 📥 Download Your Reports:")
        for i, pdf_path in enumerate(st.session_state.generated_reports):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label=f"📄 {os.path.basename(pdf_path)}",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    key=f"{os.path.basename(pdf_path)}_{i}"
                )

# 🔄 Mode selector
mode = st.radio("Choose mode:", ["🧠 Prompt (Natural Language)", "⚙️ Manual Parameters"], horizontal=True)

# 🧠 Prompt mode
if mode == "🧠 Prompt (Natural Language)":
    user_query = st.text_area("Ask your question:", placeholder="e.g. Generate a report for GW150914")

    if st.button("🚀 Run Agent"):
        if not user_query.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking..."):
                try:
                    response = run_orchestration(user_query)
                    st.success("✅ Agent completed the task!")
                    st.session_state.response_text = response
                    offer_pdf_download(response)
                except Exception as e:
                    st.error(f"❌ Agent error: {e}")

    if "response_text" in st.session_state:
        st.markdown(st.session_state.response_text)
        render_download_buttons()

# ⚙️ Manual mode – only allow known event names
else:
    st.markdown("Manually specify parameters for gravitational wave analysis:")

    event_input = st.text_input("Known Event Name", placeholder="e.g. GW150914")
    detector_input = st.multiselect("Detectors", ["H1", "L1"], default=["H1", "L1"])
    mass1_input = st.number_input("Mass 1 (M☉)", value=35.6)
    mass2_input = st.number_input("Mass 2 (M☉)", value=29.1)
    distance_input = st.number_input("Distance (Mpc)", value=410.0)

    if st.button("🚀 Run Agent with These Parameters"):
        if not event_input.strip():
            st.error("Please enter a valid known GW event name.")
        else:
            try:
                metadata = resolve_event_metadata(event_input.strip().upper())
                gps = metadata["gps_event"]
                mass1 = metadata.get("mass1", mass1_input)
                mass2 = metadata.get("mass2", mass2_input)
                distance = metadata.get("distance", distance_input)
            except Exception:
                st.error("Could not resolve known event. Try one like GW150914, GW170814, etc.")
                st.stop()

            detectors = " and ".join(detector_input)
            query = (
                f"Generate a gravitational wave report for GPS event {gps}, "
                f"using detectors {detectors}, with black hole masses {mass1} and {mass2} solar masses "
                f"at a distance of {distance} Mpc."
            )

            with st.spinner("Running agent..."):
                try:
                    response = run_orchestration(query)
                    st.success("✅ Agent completed the task!")
                    st.session_state.response_text = response
                    offer_pdf_download(response)
                except Exception as e:
                    st.error(f"❌ Agent error: {e}")

    if "response_text" in st.session_state:
        st.markdown(st.session_state.response_text)
        render_download_buttons()
