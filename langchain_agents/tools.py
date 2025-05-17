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


class ReportInput(BaseModel):
    gps_event: int
    delta_t: float = 0.05


@tool("generate_report")
def report_tool(gps_event: str):
    """Generate a PDF report given a GPS event time."""
    gps_time = int(gps_event.strip())
    from visualize import run_pipeline
    results, delta_t = run_pipeline(gps_time)
    generate_pdf_report(results, gps_time, delta_t)
    return "PDF report generated."