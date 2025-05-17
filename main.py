import matplotlib.pyplot as plt
from gwpy.timeseries import TimeSeries
from gwpy.plot import Plot
from preprocess import preprocess_data
from matched_filter import matched_filter_analysis
import os

# Paths to H1 and L1 data files
DATA_PATH = './data/'
H1_FILE = os.path.join(DATA_PATH, 'H-H1_LOSC_4_V1-1126256640-4096.hdf5')
L1_FILE = os.path.join(DATA_PATH, 'L-L1_LOSC_4_V1-1126256640-4096.hdf5')

def load_data(file_path):
    """Load strain data from HDF5 files."""
    print(f"Loading data from {file_path}...")
    strain = TimeSeries.read(file_path, channel='H1:STRAIN' if 'H1' in file_path else 'L1:STRAIN')
    return strain

def visualize_data(h1_data, l1_data, title='Gravitational Wave Strain Data'):
    """Visualize the strain data from H1 and L1."""
    plt.figure(figsize=(10, 4))
    plt.plot(h1_data.times, h1_data, label='H1 Detector', alpha=0.7)
    plt.plot(l1_data.times, l1_data, label='L1 Detector', alpha=0.7)
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Strain')
    plt.legend()
    plt.grid(True)
    output_path = './graphs/'
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    plt.savefig(os.path.join(output_path, f'{title.replace(" ", "_")}.png'))

def main():
    # Load the data
    h1_data = load_data(H1_FILE)
    l1_data = load_data(L1_FILE)
    
    # Preprocess the data
    print("Preprocessing data...")
    h1_cleaned = preprocess_data(h1_data)
    l1_cleaned = preprocess_data(l1_data)

    # Visualize the preprocessed data
    visualize_data(h1_cleaned, l1_cleaned, title='Preprocessed Gravitational Wave Data')

    # Detection Analysis
    print("Running matched filter analysis...")
    matched_filter_analysis(h1_cleaned, l1_cleaned)

if __name__ == "__main__":
    main()