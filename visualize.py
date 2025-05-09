"""
Quick–look plot of the GW150914 signal.

This script visualizes gravitational wave data from two detectors (H1 and L1),
performs matched filtering, runs detection, and checks for temporal coincidence.
"""

from matplotlib import pyplot as plt
from agents.fetch_validate import download
from matched_filter import run_matched_filter
from preprocess import preprocess
from agents.signal_detector import detect_signal
from gwpy.timeseries import TimeSeries as GWpyTimeSeries
from pycbc.types import TimeSeries as PyCBCTimeSeries


# ───────── USER PARAMS ───────── #
gps_event = 1126259462          # GW150914
detectors = ["H1", "L1"]        # Run coincidence check across these
half_window = 256               # total segment = 2 × this
crop_width = 2                  # seconds plotted around the event
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
    else:
        plt.show()


def plot_processed_strain(strain, detector_name, event_name="GW150914", save_path=None):
    plot = strain.plot()
    ax = plot.gca()
    ax.set_title(f"{detector_name} strain – {event_name} (preprocessed)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Strain (whitened, filtered)")
    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def convert_gwpy_to_pycbc(gwpy_timeseries):
    return PyCBCTimeSeries(
        gwpy_timeseries.value,
        delta_t=1.0 / gwpy_timeseries.sample_rate.value
    )


def analyze_detector(detector, gps_time):
    print(f"\n===== {detector} Analysis =====")

    # Fetch and visualize raw data
    strain = fetch_data(detector, gps_time, half_window)
    perform_raw_analysis(strain, gps_time, crop_width, detector)

    # Preprocess and analyze
    strain_clean = preprocess(strain, gps_event=gps_time, crop_width=crop_width)
    plot_processed_strain(strain_clean, detector)

    # Convert to PyCBC and run matched filter
    strain_pycbc = convert_gwpy_to_pycbc(strain_clean)
    snr = run_matched_filter(strain_pycbc, strain_clean.sample_rate.value)

    # Run detection logic using that SNR
    detected, peak_snr, peak_time = detect_signal(snr, snr_threshold=snr_threshold)

    print(f"Detection: {'✅' if detected else '❌'} | Peak SNR: {peak_snr:.2f} at t = {peak_time:.4f}s")

    return {
        "detected": detected,
        "peak_snr": peak_snr,
        "peak_time": peak_time
    }


def perform_raw_analysis(strain, gps_time, crop_width, detector_name):
    strain_zoom = crop_data(strain, gps_time, crop_width)
    plot_raw_strain(strain_zoom, detector_name)


def main():
    print(f"Running analysis for GPS {gps_event} on detectors: {', '.join(detectors)}")

    results = {}
    for det in detectors:
        results[det] = analyze_detector(det, gps_event)

    print("\n===== Coincidence Check =====")
    if all(results[det]["detected"] for det in detectors):
        times = [results[det]["peak_time"] for det in detectors]
        delta_t = abs(times[0] - times[1])
        if delta_t <= coincidence_window:
            print(f"✅ Coincident detection! Δt = {delta_t:.4f} s")
        else:
            print(f"❌ Peak times too far apart: Δt = {delta_t:.4f} s")
    else:
        print("❌ One or both detectors failed to detect signal")


if __name__ == "__main__":
    main()
