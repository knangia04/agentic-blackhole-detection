"""
Cross-detector coincidence validation for GW150914 with visualization.

- Downloads H1 and L1 data
- Applies same preprocessing
- Crops ±2s around GPS event
- Runs matched filter
- Compares and visualizes SNR and strain waveforms
"""

from agents.fetch_validate import download
from preprocess import preprocess
from matched_filter import run_matched_filter
from pycbc.types import TimeSeries
import matplotlib.pyplot as plt

# Parameters
gps_event = 1126259462
half_window = 128
crop_width = 2
detectors = ["H1", "L1"]
colors = {"H1": "tab:blue", "L1": "tab:orange"}

results = {}
strain_zoom_dict = {}
snr_dict = {}

for det in detectors:
    print(f"\n--- Processing {det} ---")
    strain = download(det, gps_event, window=half_window)
    strain_clean = preprocess(strain)
    strain_zoom = strain_clean.crop(gps_event - crop_width, gps_event + crop_width)

    strain_zoom_dict[det] = strain_zoom

    sr = strain_zoom.sample_rate.value
    strain_pyc = TimeSeries(strain_zoom.value, delta_t=1.0 / sr)

    snr_series = run_matched_filter(strain_pyc, sr)
    snr_dict[det] = snr_series

    peak_idx = abs(snr_series).numpy().argmax()
    peak_time = snr_series.sample_times[peak_idx]
    peak_snr = abs(snr_series[peak_idx])

    results[det] = {
        "snr": peak_snr,
        "time": peak_time
    }

# Δt between peaks
delta_t = abs(results["H1"]["time"] - results["L1"]["time"])

# ────────────── 📈 VISUALIZATION ────────────── #

# 1. Overlaid whitened strain plots
plt.figure(figsize=(10, 4))
for det in detectors:
    strain = strain_zoom_dict[det]
    plt.plot(strain.times.value, strain.value, label=f"{det}", alpha=0.8, color=colors[det])
plt.title("Preprocessed Strain (H1 vs L1)")
plt.xlabel("Time (s)")
plt.ylabel("Strain (whitened, filtered)")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# 2. Overlaid SNR plots
plt.figure(figsize=(10, 4))
for det in detectors:
    snr = snr_dict[det]
    plt.plot(snr.sample_times, abs(snr), label=f"{det}", alpha=0.8, color=colors[det])
plt.title("Matched Filter SNR (H1 vs L1)")
plt.xlabel("Time (s)")
plt.ylabel("SNR")
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()

# 3. Print timing info
print("\n--- Coincidence Summary ---")
print(f"H1: Peak SNR = {results['H1']['snr']:.2f} at {results['H1']['time']:.4f} s")
print(f"L1: Peak SNR = {results['L1']['snr']:.2f} at {results['L1']['time']:.4f} s")
print(f"Δt (H1–L1): {delta_t * 1e3:.2f} ms")

if delta_t <= 0.010:
    print("✅ Coincident signal within 10 ms: likely astrophysical.")
else:
    print("❌ Timing mismatch exceeds 10 ms: possibly noise or glitch.")


from gwpy.timeseries import TimeSeries

def plot_spectrogram(strain, detector, gps_event, crop_width):
    """
    Plots Q-transform spectrogram using GWpy.
    """
    qscan = strain.q_transform(outseg=(gps_event - crop_width, gps_event + crop_width))
    plot = qscan.plot()
    ax = plot.gca()
    ax.set_title(f"{detector} Spectrogram – GW150914")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    ax.set_yscale('log')
    ax.grid(True)
    plt.show()

for det in detectors:
    print(f"\n--- Spectrogram for {det} ---")
    plot_spectrogram(strain_zoom_dict[det], det, gps_event, crop_width)
