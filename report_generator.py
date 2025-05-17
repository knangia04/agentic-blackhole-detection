# report_generator.py
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def generate_pdf_report(results: dict, gps_event: int, delta_t=None, output_file="output/report.pdf"):
    os.makedirs("output", exist_ok=True)

    with PdfPages(output_file) as pdf:
        plt.rcParams["font.family"] = "DejaVu Sans" 
        # Page 1: Summary
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis('off')
        lines = [
            "Gravitational Wave Detection Report",
            f"GPS Event: {gps_event}",
            "",
        ]
        for det, res in results.items():
            lines.append(f"--- {det} ---")
            lines.append(f"Detected: {'PASS' if res['detected'] else 'FAIL'}")
            lines.append(f"Peak SNR: {res['peak_snr']:.2f}")
            lines.append(f"Peak Time: {res['peak_time']:.4f} s")
            lines.append("")

        if delta_t is not None:
            lines.append(f"Coincidence Δt: {delta_t:.4f} s")
            lines.append("Coincidence Check: PASS" if delta_t <= 0.10 else "FAIL: Too far apart")
        else:
            lines.append("Coincidence Δt: Not available")

        ax.text(0.1, 0.95, "\n".join(lines), va="top", fontsize=12)
        pdf.savefig(fig)
        plt.close(fig)

        # Page 2+: SNR plots
        for det, res in results.items():
            snr_series = res.get("snr_series")
            if snr_series is not None:
                fig, ax = plt.subplots()
                ax.plot(snr_series.sample_times, abs(snr_series))
                ax.axvline(res['peak_time'], color="r", linestyle="--", label="Peak")
                ax.set_title(f"{det} – SNR Time Series")
                ax.set_xlabel("Time (s)")
                ax.set_ylabel("SNR")
                ax.legend()
                pdf.savefig(fig)
                plt.close(fig)

    print(f"[✓] PDF report saved to {output_file}")