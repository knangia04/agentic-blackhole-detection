from gwpy.timeseries import TimeSeries
from matplotlib import pyplot as plt
import h5py

# File path to H1 data
h1_file = "data/H-H1_LOSC_4_V1-1126256640-4096.hdf5"


try:
    strain = TimeSeries.read(h1_file, path="strain/Strain", format='hdf5.gwosc')
except Exception as e:
    print(f"First attempt failed: {e}")
    # Alternative approach using h5py directly if the above fails
    try:
        with h5py.File(h1_file, 'r') as f:
            data = f['strain/Strain'][()]
            t0 = f['strain/Strain'].attrs['GPSstart']
            dt = f['strain/Strain'].attrs['dt']
            strain = TimeSeries(data, t0=t0, dt=dt, name='H1 Strain')
    except Exception as e2:
        print(f"Second attempt failed: {e2}")
        # Try with default format
        strain = TimeSeries.read(h1_file, path="strain/Strain")

# Focus on 4 seconds around GW150914 (GPS 1126259462)
strain_trimmed = strain.crop(1126259460, 1126259464)

# Plot
plot = strain_trimmed.plot()
plot.gca().set_title("H1 Strain – GW150914")
plot.gca().set_xlabel("Time (s)")
plot.gca().set_ylabel("Strain")
plt.show()