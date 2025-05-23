"""
Quick–look plot of the GW150914 signal.

This script visualizes gravitational wave data from two detectors (H1 and L1),
performs matched filtering, runs detection, and checks for temporal coincidence.
"""

from matplotlib import pyplot as plt
from agents.fetch_validate import download
from agents.matched_filter import run_matched_filter
from agents.preprocess import preprocess
from agents.signal_detector import detect_signal
from gwpy.timeseries import TimeSeries as GWpyTimeSeries
from pycbc.types import TimeSeries as PyCBCTimeSeries


# ───────── USER PARAMS ───────── #
# gps_event = 1126259462          # GW150914
detectors = ["H1", "L1"]        # Run coincidence check across these
half_window = 4               # total segment = 2 × this
crop_width = 4                 # seconds plotted around the event
snr_threshold = 8.0             # detection threshold
coincidence_window = 0.01       # seconds (10 ms)
# ─────────────────────────────── #


def fetch_data(detector, gps_time, window):
    return download(detector, gps_time, window=window)


def crop_data(strain, center_time, width):
    return strain.crop(center_time - width, center_time + width)


def plot_raw_strain(strain, detector_name, event_name="GW150914", save_path=None):
    plot = strain.plot()
    ax = plot.gca()
    ax.set_title(f"{detector_name} strain – {event_name}")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strain")
    if save_path:
        plt.savefig(save_path)
    # else:
    #     plt.show()


def plot_processed_strain(strain, detector_name, event_name="GW150914", save_path=None):
    plot = strain.plot()
    ax = plot.gca()
    ax.set_title(f"{detector_name} strain – {event_name} (preprocessed)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strain (whitened, filtered)")
    if save_path:
        plt.savefig(save_path)
    # else:
    #     plt.show()


def convert_gwpy_to_pycbc(gwpy_timeseries):
    return PyCBCTimeSeries(
        gwpy_timeseries.value,
        delta_t=1.0 / gwpy_timeseries.sample_rate.value,
        epoch=gwpy_timeseries.t0.value
    )

def analyze_detector(detector, gps_time, mass1, mass2, distance):
    # print(f"\n===== {detector} Analysis =====")
    # print(gps_time)

    strain = fetch_data(detector, gps_time, half_window)
    strain_clean = preprocess(strain, gps_event=gps_time, crop_width=crop_width)
    # print(f"H1 strain mean: {strain_clean.mean()}, std: {strain_clean.std()}")
    strain_pycbc = convert_gwpy_to_pycbc(strain_clean)

    snr = run_matched_filter(strain_pycbc, strain_clean.sample_rate.value, mass1, mass2, distance, gps_event=gps_time)

    detected, peak_snr, peak_time = detect_signal(snr, t0=strain_clean.t0, snr_threshold=snr_threshold)

    # print(f"Detection: {'Yes' if detected else 'No'} | Peak SNR: {peak_snr:.2f} at t = {peak_time:.4f}s")

    return {
        "detected": detected,
        "peak_snr": peak_snr,
        "peak_time": float(peak_time),
        "snr_series": snr 
    }


def perform_raw_analysis(strain, gps_time, crop_width, detector_name):
    strain_zoom = crop_data(strain, gps_time, crop_width)
    plot_raw_strain(strain_zoom, detector_name)

def run_pipeline(gps_event, mass1, mass2, distance, detectors=["H1", "L1"], crop_width=4, snr_threshold=8.0):
    results = {}
    for det in detectors:
        results[det] = analyze_detector(det, gps_event, mass1, mass2, distance)

    if all(det in results for det in ["H1", "L1"]):
        delta_t = abs(results["H1"]["peak_time"] - results["L1"]["peak_time"])
    else:
        delta_t = None

    return results, delta_t

