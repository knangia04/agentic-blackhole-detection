from gwpy.timeseries import TimeSeries
from matplotlib import pyplot as plt

# File path to the L1 strain data HDF5 file
filename = "data/data/L-L1_LOSC_4_V1-1126256640-4096.hdf5"

# Load strain data from the file
l1_strain = TimeSeries.read(filename, channel="L1:LOSC-STRAIN")

# Trim around the GW150914 event (GPS 1126259462.4)
# Show 4 seconds of data centered on the event
l1_trimmed = l1_strain.crop(1126259460, 1126259464)

# Plot the time series
plot = l1_trimmed.plot()
ax = plot.gca()
ax.set_title("L1 Strain Data – GW150914")
ax.set_xlabel("Time (s)")
ax.set_ylabel("Strain")

plt.tight_layout()
plt.show()
