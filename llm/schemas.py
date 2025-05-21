from pydantic import BaseModel, Field


class DetectionInput(BaseModel):
    detector: str = Field(..., description="Detector name, e.g. 'H1', 'L1'")
    gps_time: int = Field(..., description="GPS time of the event")


class DetectionOutput(BaseModel):
    detected: bool = Field(..., description="Whether the signal was detected")
    peak_snr: float = Field(..., description="Peak SNR of matched filter")
    peak_time: float = Field(..., description="GPS time of peak SNR")


class CoincidenceOutput(BaseModel):
    coincident: bool = Field(..., description="Whether detectors are coincident within tolerance")
    delta_t: float = Field(..., description="Time difference between peak detections")


class ReportRequest(BaseModel):
    gps_time: int = Field(..., description="GPS event time")
    output_path: str = Field(..., description="Where to save PDF report")
