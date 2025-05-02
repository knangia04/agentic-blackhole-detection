from __future__ import annotations
from typing import Iterable
from gwpy.timeseries import TimeSeries


class DataQualityError(RuntimeError):
    pass


def download(
    detector: str,
    gps: int,
    window: int = 128,
    *,
    veto_flag: str = "CBC_CAT2",
    cache: bool = True,
) -> TimeSeries:
    start, end = gps - window, gps + window

    try:
        ts = TimeSeries.fetch_open_data(
            detector.upper(), start, end, cache=cache, include_quality=True
        )
    except TypeError:
        print("⚠️  include_quality not supported — skipping DQ flags.")
        ts = TimeSeries.fetch_open_data(detector.upper(), start, end, cache=cache)

    _check_sample_rate(ts, (4096.0, 16384.0))
    _check_quality_flag(ts, veto_flag)
    _check_continuity(ts)

    return ts


def _check_sample_rate(ts: TimeSeries, expected: Iterable[float]) -> None:
    fs = 1.0 / ts.dt.value
    if fs not in expected:
        raise DataQualityError(f"Unexpected sample rate: {fs:.1f} Hz")


def _check_quality_flag(ts: TimeSeries, flag: str) -> None:
    if not hasattr(ts, "quality"):
        print("⚠️  No quality flags available; skipping veto check.")
        return

    q = ts.quality
    key = flag.lower()
    if key not in q:
        print(f"⚠️  Flag '{flag}' not found; skipping veto check.")
        return

    if not q[key].active.contains((ts.t0, ts.t0 + ts.duration)):
        raise DataQualityError(f"Flag '{flag}' active in segment")


def _check_continuity(ts: TimeSeries) -> None:
    times = ts.times.value
    dt = ts.dt.value
    if ((times[1:] - times[:-1]) != dt).any():
        raise DataQualityError("Nonuniform sample spacing — drop-out detected")