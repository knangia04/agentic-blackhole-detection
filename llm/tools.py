# langchain_agents/tools.py

import json
from typing import Union, Optional
from pydantic import BaseModel
from langchain.tools import StructuredTool

from agents.fetch_validate import download
from agents.preprocess import preprocess
from agents.matched_filter import run_matched_filter
from agents.signal_detector import detect_signal
from reports.report_generator import generate_pdf_report
from reports.visualize import run_pipeline
from agents.gw_metadata import resolve_event_metadata

# INPUT MODELS
class FetchInput(BaseModel):
    gps_event: float
    detector: str
    half_window: int = 256

class PreprocessInput(BaseModel):
    gps_event: float
    detector: str
    crop_width: int = 4

class AnalyzeInput(BaseModel):
    gps_event: float
    detector: str
    crop_width: int = 4
    mass1: Optional[float] = 30
    mass2: Optional[float] = 30
    distance: Optional[float] = 400

from typing import Union, Optional, List
from pydantic import BaseModel

class ReportInput(BaseModel):
    gps_event: Union[int, List[int]]
    mass1: Optional[float] = 30.0
    mass2: Optional[float] = 30.0
    distance: Optional[float] = 400.0



# TOOLS

def fetch_data_tool(input: Union[FetchInput, str, dict]):
    """Fetch raw strain data for a given detector and GPS time."""
    if isinstance(input, str):
        try:
            input_cleaned = input.split("#")[0].strip()
            input = json.loads(input_cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON input passed to tool: {input}\n{e}")
    if isinstance(input, dict):
        if "gps_time" in input and "gps_event" not in input:
            input["gps_event"] = input.pop("gps_time")
        input = FetchInput(**input)

    data = download(input.detector, input.gps_event, input.half_window)
    return f"\nFetched {input.detector} data around GPS {input.gps_event}\n"


def preprocess_tool(input: Union[PreprocessInput, str, dict]):
    """Preprocess strain data: crop, whiten, and bandpass filter."""
    if isinstance(input, str):
        try:
            input_cleaned = input.split("#")[0].strip()
            input = json.loads(input_cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON input passed to tool: {input}\n{e}")
    if isinstance(input, dict):
        if "gps_time" in input and "gps_event" not in input:
            input["gps_event"] = input.pop("gps_time")
        input = PreprocessInput(**input)

    raw = download(input.detector, input.gps_event, 256)
    clean = preprocess(raw, gps_event=input.gps_event, crop_width=input.crop_width)
    return f"\nPreprocessed {input.detector} data\n"


def analyze_tool(input: Union[AnalyzeInput, str, dict]):
    """Run matched filter and extract peak SNR and time."""
    if isinstance(input, str):
        try:
            input_cleaned = input.split("#")[0].strip()
            input = json.loads(input_cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Invalid JSON input passed to tool: {input}\n{e}")
    if isinstance(input, dict):
        if "gps_time" in input and "gps_event" not in input:
            input["gps_event"] = input.pop("gps_time")
        provided_fields = set(input.keys())
        parsed = AnalyzeInput(**input)
        mass1 = parsed.mass1

    mass2 = parsed.mass2
    distance = parsed.distance
    if not {"mass1", "mass2", "distance"}.issubset(provided_fields):
        metadata = resolve_event_metadata(str(parsed.gps_event))
        if metadata:
            mass1 = metadata["mass1"]
            mass2 = metadata["mass2"]
            distance = metadata["distance"]
            # print(f"[Metadata Injected] {gps_event}: m1={mass1}, m2={mass2}, d={distance}")
        else:
            print(f"[Warning] No metadata for {parsed.gps_event}. Using defaults.")

    results, _ = run_pipeline(parsed.gps_event, mass1, mass2, distance, detectors=[parsed.detector])
    det_result = results[parsed.detector]
    return f"\n{parsed.detector}: Peak SNR = {det_result['peak_snr']:.2f} at t = {det_result['peak_time']:.4f} (Detected: {det_result['detected']})\n"


def generate_report_tool(input: Union[str, dict]):
    """
    Run the full pipeline and generate a PDF report.
    Accepts input: {
        "gps_event": int or List[int],
        "mass1": float (optional),
        "mass2": float (optional),
        "distance": float (optional)
    }
    """
    if isinstance(input, str):
        try:
            input_cleaned = input.split("#")[0].strip()
            input = json.loads(input_cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON input passed to tool: {input}\n{e}")

    if isinstance(input, dict):
        if "gps_time" in input and "gps_event" not in input:
            input["gps_event"] = input.pop("gps_time")

        # Capture what the LLM actually sent
        provided_fields = set(input.keys())

        # Then parse via Pydantic
        parsed = ReportInput(**input)

    gps_events = parsed.gps_event if isinstance(parsed.gps_event, list) else [parsed.gps_event]

    # Only fallback to metadata if not explicitly provided
    mass1 = parsed.mass1
    mass2 = parsed.mass2
    distance = parsed.distance

    results_summary = []

    for gps_event in gps_events:
        if not {"mass1", "mass2", "distance"}.issubset(provided_fields):
            metadata = resolve_event_metadata(str(gps_event))
            if metadata:
                mass1 = metadata["mass1"]
                mass2 = metadata["mass2"]
                distance = metadata["distance"]
                # print(f"[Metadata Injected] {gps_event}: m1={mass1}, m2={mass2}, d={distance}")
            else:
                print(f"[Warning] No metadata for {gps_event}. Using defaults.")

        results, delta_t = run_pipeline(gps_event, mass1, mass2, distance)
        output_path = f"output/{gps_event}_report.pdf"
        generate_pdf_report(results, gps_event, delta_t, output_file=output_path)
        results_summary.append(f"{gps_event}_report.pdf")

    return f"\nReports generated: {', '.join(results_summary)}\n"
