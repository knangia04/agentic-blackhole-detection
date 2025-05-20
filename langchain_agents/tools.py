# langchain_agents/tools.py

from langchain.tools import tool
from pydantic import BaseModel
from typing import Optional

from agents.fetch_validate import download
from preprocess import preprocess
from matched_filter import run_matched_filter
from agents.signal_detector import detect_signal
from report_generator import generate_pdf_report


class FetchInput(BaseModel):
    gps_time: int
    detector: str
    half_window: int = 256


@tool("fetch_data")
def fetch_data_tool(input: FetchInput):
    """Fetch raw strain data for a given detector and GPS time."""
    data = download(input.detector, input.gps_time, input.half_window)
    return f"Fetched {input.detector} data around GPS {input.gps_time}"


class PreprocessInput(BaseModel):
    gps_time: int
    detector: str
    crop_width: int = 4


@tool("preprocess_data")
def preprocess_tool(input: PreprocessInput):
    """Preprocess strain data: crop, whiten, and bandpass filter."""
    raw = download(input.detector, input.gps_time, 256)
    clean = preprocess(raw, gps_event=input.gps_time, crop_width=input.crop_width)
    return f"Preprocessed {input.detector} data"


class AnalyzeInput(BaseModel):
    gps_time: int
    detector: str
    crop_width: int = 4


@tool("analyze_signal")
def analyze_tool(input: AnalyzeInput):
    """Analyze the signal to extract peak SNR and time."""
    raw = download(input.detector, input.gps_time, 256)
    clean = preprocess(raw, gps_event=input.gps_time, crop_width=input.crop_width)
    from pycbc.types import TimeSeries as PyCBCTimeSeries
    strain_pycbc = PyCBCTimeSeries(clean.value, delta_t=1.0 / clean.sample_rate.value, epoch=clean.t0.value)
    snr = run_matched_filter(strain_pycbc, clean.sample_rate.value, gps_event=input.gps_time)
    detected, peak_snr, peak_time = detect_signal(snr, t0=clean.t0)
    return f"{input.detector}: Peak SNR = {peak_snr:.2f} at t = {peak_time:.4f} (Detected: {detected})"


from visualize import run_pipeline
from report_generator import generate_pdf_report
from pydantic import BaseModel

class ReportInput(BaseModel):
    gps_event: int

import json
from langchain.tools import tool

@tool("generate_report")
def generate_report_tool(input: str):
    """
    Run the full pipeline and generate a PDF report.
    Accepts JSON string: {"gps_event": int, "delta_t": float (optional)}.
    """
    try:
        parsed = json.loads(input)
        gps_event = int(parsed["gps_event"])
        delta_t = float(parsed.get("delta_t", 0.05))
    except Exception as e:
        return f"❌ Failed to parse input: {str(e)}"

    from visualize import run_pipeline
    from report_generator import generate_pdf_report

    results, delta_t = run_pipeline(gps_event)
    generate_pdf_report(results, gps_event, delta_t, output_file=f"output/{gps_event}_report.pdf")
    return f"✅ Report generated at output/{gps_event}_report.pdf"


