# Agentic Black Hole Detection

**Team Members:**  
Sidharth Anand (Sanand12)  
Krish Nangia (Knang2)

**Date:** 4/22/2025  
**Course:** ECE 498 Section BH3  
**Topic:** 4: Agentic Black Hole Detection  
**Repository:** [https://github.com/SidharthAnand04/agentic-blackhole-detection](https://github.com/SidharthAnand04/agentic-blackhole-detection)

## Project Overview 
This project develops an autonomous, agent-based system for detecting black hole mergers from gravitational wave data. Modular subagents handle preprocessing, detection, and parameter estimation, orchestrated by a large language model for adaptive workflow control. Leveraging GWTC and GWOSC datasets, the system integrates matched filtering and neural networks to enable scalable, real-time gravitational wave analysis.

## Methodology 
We use raw strain data from the GWOSC Observing Runs (O1–O3), applying preprocessing steps such as calibration, noise subtraction, and filtering via GWpy and PyCBC. Cleaned data is transformed into spectrograms and wavelets for analysis.

Signal detection combines matched filtering with CNN models trained on simulated mergers. Both modeled and unmodeled techniques (e.g., Coherent WaveBurst) identify candidate events based on signal-to-noise ratio.

Parameter estimation uses Bilby with MCMC or Nested Sampling to infer mass, spin, and distance. Triangulation generates sky localization maps.

Each task, data preprocessing, detection, validation, estimation, and reporting, is assigned to a modular subagent. An LLM-based Orchestrator Agent (via LangChain or AutoGen) sequences these tasks and handles reasoning.

Outputs include plots, parameter summaries, and localization maps, delivered through a Streamlit or Gradio interface. The system runs in a Dockerized HPC environment for scalability and reproducibility.

## Literature Survey
- **Shi et al. (2023)** introduce CBS-GPT, a transformer-based model for synthesizing gravitational waveforms from compact binary systems. Its high accuracy and generalization make it ideal for augmenting waveform datasets in detection pipelines.  
  [https://arxiv.org/abs/2310.2017](https://arxiv.org/abs/2310.2017)

- **Chatterjee et al. (2024)** adapt OpenAI's Whisper model for gravitational wave detection, demonstrating that audio-pretrained transformers can classify astrophysical signals and reject noise artifacts. This supports our use of transfer learning in the detection stack.  
  [https://arxiv.org/abs/2412.20789](https://arxiv.org/abs/2412.20789)

- **Ruiz (2023)** explores CNNs, both human-designed and GPT-generated, for GW signal classification. The findings support generative model use in automated architecture design.  
  [https://diposit.ub.edu/dspace/handle/2445/201012](https://diposit.ub.edu/dspace/handle/2445/201012)

- **Marx et al. (2024)** present a real-time machine learning pipeline for detecting compact binary coalescences, replacing traditional filtering with neural networks to reduce latency. Their approach informs our system's real-time design.  
  [https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.042010](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.111.042010)

- **Zhao et al. (2023)** review AI applications in GW research, highlighting advances in signal detection, parameter estimation, and waveform modeling. Their synthesis contextualizes our approach within broader AI developments.  
  [https://arxiv.org/abs/2311.15585](https://arxiv.org/abs/2311.15585)

## Data Sources

### Gravitational-Wave Transient Catalog (GWTC)
The GWTC provides detailed data on gravitational wave events detected by LIGO, Virgo, and KAGRA. It includes event metadata, parameter estimation samples, and sky localization maps, making it ideal for analyzing confirmed black hole mergers. The catalog is continuously updated with data from multiple observing runs.  
[https://gwosc.org/eventapi/html/GWTC/](https://gwosc.org/eventapi/html/GWTC/)

### GWOSC Observing Run Data (O1, O2, O3)
This dataset contains raw and processed strain data recorded during LIGO and Virgo's observational runs. It includes quality flags, hardware injection signals, and full time-series data, enabling end-to-end signal processing and validation of detection pipelines. The dataset is ideal for training and evaluating machine learning models on real detector noise and events.  
[https://gwosc.org/data/](https://gwosc.org/data/)

## Appendix A. Agent Architecture

### Agentic Architecture for Gravitational Wave Detection

#### 1. Introduction
This document outlines a technical and practical approach for designing an agent-based system for detecting black hole mergers through gravitational wave (GW) data. It integrates raw GW data processing, detection algorithms, and large language model (LLM) based orchestration into a cohesive autonomous pipeline.

#### 2. Gravitational Wave Detection Pipeline

##### 2.1 Data Acquisition
- Collect raw strain data from detectors like LIGO, Virgo, or KAGRA.
- Use high-frequency sampled data (typically 16 kHz).
- Data includes substantial noise sources: seismic, thermal, quantum.

##### 2.2 Preprocessing
- Calibration of raw data into meaningful strain data.
- Apply noise subtraction techniques and bandpass filters.
- Use quality flags to exclude noisy data segments.
- Generate spectrograms and apply wavelet transforms.

##### 2.3 Signal Detection
- Apply matched filtering with template banks of theoretical waveforms.
- Use ML/CNN models trained on simulated signals.
- Evaluate signal-to-noise ratio (SNR) and significance.
- Use unmodeled detection methods (e.g., Coherent WaveBurst).

##### 2.4 Parameter Estimation
- Estimate parameters (mass, spin, distance) via Bayesian inference.
- Use MCMC or Nested Sampling algorithms.
- Perform sky localization with triangulation and probability maps.

##### 2.5 Post-Processing and Visualization
- Run consistency checks and null tests.
- Generate strain vs. time plots, spectrograms, and sky localization maps.
- Use tools such as Matplotlib, GWsky, and Bilby for analysis.

#### 3. Agent-Based System with LLM Integration
- Utilize LLMs (e.g., GPT, Claude, LLaMA) to orchestrate modules.
- Design modular subagents: DataPreprocessor, SignalDetector, EventValidator, ParameterEstimator, ReportGenerator.
- Use LangChain or AutoGen for implementation.

#### 4. System Architecture
User Input → Orchestrator Agent → DataPreprocessor → SignalDetector → EventValidator → ParameterEstimator → ReportGenerator → User Output

#### 5. Tools and Frameworks
- GWpy, PyCBC, Bilby, Matplotlib for data analysis.
- LangChain, AutoGen, CrewAI for orchestration.
- HPC/Docker environments for execution.
- Streamlit/Gradio for user interface.

#### 6. Example Workflow
1. User submits LIGO segment for analysis.
2. DataPreprocessor cleans and filters the signal.
3. SignalDetector identifies potential events.
4. EventValidator filters out false positives.
5. ParameterEstimator calculates physical parameters.
6. ReportGenerator outputs visuals and summaries.