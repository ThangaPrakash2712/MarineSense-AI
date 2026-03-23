"""
sonar_module.py
---------------
Sonar Simulation Engine for MarineSense AI.

Simulates underwater sonar behavior using structured probabilistic data
(no hardware required). Produces depth, echo intensity, and fish density
readings that mirror real sonar physics.

Architecture:
    simulate_sonar_input()  →  raw sonar frame dict
    process_sonar_data()    →  cleaned + normalized readings
    generate_alert()        →  human-readable alert string
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
# Data Structures
# ─────────────────────────────────────────────

@dataclass
class SonarFrame:
    """One sonar scan snapshot."""
    depth_m: float          # Depth of strongest echo (meters)
    echo_intensity: float   # Raw echo strength 0–1
    fish_density: float     # Estimated fish density 0–1
    water_temp_c: float     # Ambient water temperature
    salinity_psu: float     # Salinity reading
    noise_level: float      # Background acoustic noise 0–1
    timestamp: float        # Unix-style step counter


@dataclass
class SonarReading:
    """Processed sonar output after noise filtering."""
    fish_detected: bool
    estimated_count: int
    depth_m: float
    confidence: float       # 0–100
    density_label: str      # "None" | "Low" | "Medium" | "High"
    raw_frame: SonarFrame = field(repr=False)


# ─────────────────────────────────────────────
# Environmental Context
# ─────────────────────────────────────────────

# Depth zones where fish are most likely (meters)
FISH_DEPTH_ZONES = {
    "surface":    (5,  30),
    "mid_water":  (30, 80),
    "deep":       (80, 200),
}

# Density thresholds (fish_density score)
DENSITY_THRESHOLDS = {
    "High":   0.65,
    "Medium": 0.35,
    "Low":    0.10,
}


# ─────────────────────────────────────────────
# Core Functions
# ─────────────────────────────────────────────

def simulate_sonar_input(
    step: int,
    base_sst: float = 27.0,
    base_chlorophyll: float = 0.8,
    zone_confidence: float = 70.0,
    seed: Optional[int] = None,
) -> SonarFrame:
    """
    Simulate one sonar scan frame.

    Uses ocean environmental context (SST, chlorophyll, AI zone confidence)
    to bias the probability of fish presence — higher chlorophyll and
    higher AI confidence increase the likelihood of a strong echo.

    Args:
        step:             Scan step index (used for temporal variation).
        base_sst:         Sea surface temperature from AI features.
        base_chlorophyll: Chlorophyll concentration from AI features.
        zone_confidence:  AI model confidence score (0–100).
        seed:             Optional RNG seed for reproducibility.

    Returns:
        SonarFrame with raw simulated readings.
    """
    rng = np.random.default_rng(seed if seed is not None else step * 7)

    # ── Fish presence probability ──────────────────────────────────────
    # Chlorophyll drives food availability → fish aggregation
    chloro_factor = min(base_chlorophyll / 2.0, 1.0)          # 0–1
    # SST in optimal range (24–30°C) boosts probability
    sst_factor = max(0.0, 1.0 - abs(base_sst - 27.0) / 10.0)  # 0–1
    # AI zone confidence contributes directly
    ai_factor = zone_confidence / 100.0                         # 0–1

    fish_probability = 0.3 * chloro_factor + 0.3 * sst_factor + 0.4 * ai_factor

    # ── Depth selection ────────────────────────────────────────────────
    # Warmer SST → fish stay shallower
    if base_sst > 28:
        zone = rng.choice(["surface", "mid_water"], p=[0.6, 0.4])
    else:
        zone = rng.choice(["surface", "mid_water", "deep"], p=[0.3, 0.5, 0.2])

    depth_range = FISH_DEPTH_ZONES[zone]
    depth = rng.uniform(*depth_range)

    # ── Echo intensity ─────────────────────────────────────────────────
    # Stronger echo when fish are present; attenuates with depth
    depth_attenuation = max(0.3, 1.0 - depth / 250.0)
    base_echo = fish_probability * depth_attenuation
    echo = float(np.clip(base_echo + rng.normal(0, 0.08), 0.0, 1.0))

    # ── Fish density ───────────────────────────────────────────────────
    # Temporal oscillation simulates school movement
    oscillation = 0.1 * np.sin(step * 0.4)
    density = float(np.clip(fish_probability + oscillation + rng.normal(0, 0.06), 0.0, 1.0))

    # ── Acoustic noise ─────────────────────────────────────────────────
    noise = float(rng.uniform(0.05, 0.25))

    return SonarFrame(
        depth_m=round(depth, 1),
        echo_intensity=round(echo, 3),
        fish_density=round(density, 3),
        water_temp_c=round(base_sst + rng.normal(0, 0.3), 2),
        salinity_psu=round(rng.uniform(33.5, 35.5), 2),
        noise_level=round(noise, 3),
        timestamp=float(step),
    )


def process_sonar_data(frame: SonarFrame) -> SonarReading:
    """
    Apply noise filtering and threshold logic to a raw SonarFrame.

    Noise-corrected echo = echo_intensity - noise_level
    Fish are confirmed when corrected echo exceeds detection threshold.

    Args:
        frame: Raw SonarFrame from simulate_sonar_input().

    Returns:
        SonarReading with detection decision and confidence.
    """
    DETECTION_THRESHOLD = 0.28   # Minimum corrected echo to confirm fish

    # ── Noise-corrected echo ───────────────────────────────────────────
    corrected_echo = max(0.0, frame.echo_intensity - frame.noise_level * 0.5)

    # ── Detection decision ─────────────────────────────────────────────
    fish_detected = corrected_echo >= DETECTION_THRESHOLD

    # ── Confidence (0–100) ─────────────────────────────────────────────
    # Scales with corrected echo; penalised by noise
    raw_confidence = (corrected_echo / 1.0) * 100
    noise_penalty = frame.noise_level * 15
    confidence = float(np.clip(raw_confidence - noise_penalty, 0.0, 98.0))

    # ── Density label ──────────────────────────────────────────────────
    if frame.fish_density >= DENSITY_THRESHOLDS["High"]:
        density_label = "High"
    elif frame.fish_density >= DENSITY_THRESHOLDS["Medium"]:
        density_label = "Medium"
    elif frame.fish_density >= DENSITY_THRESHOLDS["Low"]:
        density_label = "Low"
    else:
        density_label = "None"

    # ── Estimated count ────────────────────────────────────────────────
    # Rough heuristic: density × depth-adjusted volume
    if fish_detected:
        volume_factor = max(1.0, (200 - frame.depth_m) / 20.0)
        estimated_count = int(frame.fish_density * volume_factor * 80)
    else:
        estimated_count = 0

    return SonarReading(
        fish_detected=fish_detected,
        estimated_count=estimated_count,
        depth_m=frame.depth_m,
        confidence=round(confidence, 1),
        density_label=density_label,
        raw_frame=frame,
    )


def generate_alert(reading: SonarReading) -> str:
    """
    Generate a concise human-readable alert from a SonarReading.

    Args:
        reading: Processed SonarReading.

    Returns:
        Alert string for display in dashboard.
    """
    if not reading.fish_detected:
        return "No fish detected — continue on current route."

    if reading.density_label == "High":
        return (
            f"HIGH DENSITY fish zone detected at {reading.depth_m:.0f} m depth. "
            f"Est. {reading.estimated_count} fish. Confidence: {reading.confidence:.0f}%."
        )
    elif reading.density_label == "Medium":
        return (
            f"Fish detected at {reading.depth_m:.0f} m depth. "
            f"Est. {reading.estimated_count} fish. Confidence: {reading.confidence:.0f}%."
        )
    else:
        return (
            f"Sparse fish signal at {reading.depth_m:.0f} m depth. "
            f"Confidence: {reading.confidence:.0f}%. Continue scanning."
        )


def run_sonar_scan(
    step: int,
    base_sst: float,
    base_chlorophyll: float,
    zone_confidence: float,
) -> SonarReading:
    """
    Convenience wrapper: simulate → process in one call.

    Args:
        step:             Current scan step.
        base_sst:         SST from AI features.
        base_chlorophyll: Chlorophyll from AI features.
        zone_confidence:  AI confidence score.

    Returns:
        Processed SonarReading.
    """
    frame = simulate_sonar_input(step, base_sst, base_chlorophyll, zone_confidence)
    return process_sonar_data(frame)
