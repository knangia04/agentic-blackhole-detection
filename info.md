# Step 1 Preprocessing 

Bandpass filter: Keep 30–500 Hz to eliminate low-frequency seismic and high-frequency quantum noise.

Whitening: Flatten the noise spectrum to equalize SNR across frequencies.

Notch filters: Remove narrow-band instrumental noise (e.g., 60 Hz power line).

Windowing: Apply Tukey window to suppress edge artifacts in FFT.

Data quality vetoes: Remove segments with known glitches using LIGO-provided flags.

# Step 2 