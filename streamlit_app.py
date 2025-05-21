import os
import sys
import re
import streamlit as st

# Dynamically add root project path to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import orchestration logic
from llm.orchestrator import run_orchestration

# Streamlit page setup
st.set_page_config(page_title="Gravitational Wave Agent", page_icon="🌌")
st.title("🔭 Gravitational Wave Detection Agent")

# --- Mode selector
mode = st.radio("Choose mode:", ["🧠 Prompt (Natural Language)", "⚙️ Manual Parameters"], horizontal=True)

# --- PDF download helper
def offer_pdf_download(response_text):
    # Match both formats: "output/1126259462_report.pdf" and just "1126259462_report.pdf"
    matches = re.findall(r'(?:output/)?(\d+)_report\.pdf', response_text)
    for match in matches:
        pdf_path = f"output/{match}_report.pdf"
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label=f"📄 Download Report {match}",
                    data=f,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf"
                )

# --- 🧠 Prompt Mode
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
                    st.markdown(response)
                    offer_pdf_download(response)  # ✅ now works correctly!
                except Exception as e:
                    st.error(f"❌ Agent error: {e}")

# --- ⚙️ Manual Mode
else:
    st.markdown("Manually specify parameters for gravitational wave analysis:")

    gps_event = st.text_input("GPS Event Time", placeholder="e.g. 1126259462")
    detector_input = st.multiselect("Detectors", ["H1", "L1"], default=["H1", "L1"])
    mass1 = st.number_input("Mass 1 (M☉)", value=35.6)
    mass2 = st.number_input("Mass 2 (M☉)", value=29.1)
    distance = st.number_input("Distance (Mpc)", value=410.0)

    run_manual = st.button("🚀 Run Agent with These Parameters")

    if run_manual:
        if not gps_event.strip().isdigit():
            st.error("Please enter a valid GPS time.")
        else:
            gps = int(gps_event.strip())
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
                    st.markdown(response)
                    offer_pdf_download(response)  # ✅ also fixed for manual mode
                except Exception as e:
                    st.error(f"❌ Agent error: {e}")
