"""
detect_sonar.py
---------------
Decision Engine: fuses sonar readings with AI predictions to
dynamically update route recommendations and confidence scores.

Functions:
    detect_fish_with_model()   →  run sonar + optional YOLO stub
    update_route_decision()    →  decide whether to reroute
    fuse_sonar_with_ai()       →  combine sonar + AI confidence
    run_detection_loop()       →  multi-step scan session
"""

import time
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from sonar.sonar_module import (
    SonarReading,
    run_sonar_scan,
    generate_alert,
)

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# YOLO Stub
# ─────────────────────────────────────────────

def _yolo_stub_detect(echo_intensity: float, fish_density: float) -> Dict:
    """
    Lightweight YOLO-compatible stub.

    In production replace this body with:
        results = yolo_model(sonar_image_tensor)
        return parse_yolo_results(results)

    The stub mirrors the output schema so the rest of the pipeline
    works identically whether real YOLO or the stub is active.
    """
    # Simulate bounding-box confidence from echo + density
    box_conf = float(np.clip((echo_intensity + fish_density) / 2.0, 0.0, 1.0))
    detected = box_conf > 0.30

    return {
        "yolo_detected": detected,
        "box_confidence": round(box_conf * 100, 1),
        "class_label": "fish_school" if detected else "background",
        "num_boxes": int(detected) * max(1, int(box_conf * 5)),
    }


# ─────────────────────────────────────────────
# Core Detection
# ─────────────────────────────────────────────

def detect_fish_with_model(
    step: int,
    base_sst: float,
    base_chlorophyll: float,
    zone_confidence: float,
    use_yolo: bool = False,
) -> Dict:
    """
    Run one sonar scan and optionally pass through YOLO stub.

    Args:
        step:             Scan step index.
        base_sst:         SST from AI features.
        base_chlorophyll: Chlorophyll from AI features.
        zone_confidence:  AI model confidence (0–100).
        use_yolo:         Whether to run YOLO stub on top of sonar.

    Returns:
        Detection result dict with all relevant fields.
    """
    reading: SonarReading = run_sonar_scan(
        step, base_sst, base_chlorophyll, zone_confidence
    )

    result = {
        "step": step,
        "fish_detected": reading.fish_detected,
        "estimated_count": reading.estimated_count,
        "depth_m": reading.depth_m,
        "confidence": reading.confidence,
        "density_label": reading.density_label,
        "echo_intensity": reading.raw_frame.echo_intensity,
        "fish_density": reading.raw_frame.fish_density,
        "noise_level": reading.raw_frame.noise_level,
        "water_temp_c": reading.raw_frame.water_temp_c,
        "alert": generate_alert(reading),
        "yolo": None,
    }

    if use_yolo:
        result["yolo"] = _yolo_stub_detect(
            reading.raw_frame.echo_intensity,
            reading.raw_frame.fish_density,
        )
        # Upgrade detection if YOLO also fires
        if result["yolo"]["yolo_detected"]:
            result["fish_detected"] = True
            result["confidence"] = min(
                98.0,
                (result["confidence"] + result["yolo"]["box_confidence"]) / 2.0,
            )

    return result


# ─────────────────────────────────────────────
# Route Decision Engine
# ─────────────────────────────────────────────

def update_route_decision(
    detection: Dict,
    current_lat: float,
    current_lon: float,
    predicted_lat: float,
    predicted_lon: float,
    distance_to_target_km: float,
) -> Dict:
    """
    Decide whether to reroute based on sonar detection vs AI prediction.

    Logic:
        EARLY DETECTION  → fish found before reaching predicted zone
                           → reroute to current position
        CONFIRMATION     → fish found at / near predicted zone
                           → boost confidence, stay on route
        NO DETECTION     → continue on current route

    Args:
        detection:              Output of detect_fish_with_model().
        current_lat/lon:        Boat's current GPS position.
        predicted_lat/lon:      AI-predicted best fishing zone.
        distance_to_target_km:  Remaining distance to predicted zone.

    Returns:
        Route decision dict.
    """
    EARLY_DETECTION_THRESHOLD_KM = 15.0   # Reroute if fish found this far early
    CONFIRMATION_RADIUS_KM = 10.0          # "At target" if within this radius

    if not detection["fish_detected"]:
        return {
            "action": "CONTINUE",
            "reason": "No fish detected. Maintaining current route.",
            "new_lat": predicted_lat,
            "new_lon": predicted_lon,
            "confidence_boost": 0.0,
        }

    # Distance from current position to predicted zone
    from math import radians, sin, cos, sqrt, atan2
    def _haversine(la1, lo1, la2, lo2):
        R = 6371.0
        dlat = radians(la2 - la1)
        dlon = radians(lo2 - lo1)
        a = sin(dlat/2)**2 + cos(radians(la1)) * cos(radians(la2)) * sin(dlon/2)**2
        return R * 2 * atan2(sqrt(a), sqrt(1 - a))

    dist_to_predicted = _haversine(current_lat, current_lon, predicted_lat, predicted_lon)

    # ── Confirmation at target ─────────────────────────────────────────
    if dist_to_predicted <= CONFIRMATION_RADIUS_KM:
        boost = min(10.0, detection["confidence"] * 0.1)
        return {
            "action": "CONFIRM",
            "reason": f"Sonar confirms fish at predicted zone. Confidence boosted by {boost:.1f}%.",
            "new_lat": predicted_lat,
            "new_lon": predicted_lon,
            "confidence_boost": boost,
        }

    # ── Early detection → reroute ──────────────────────────────────────
    if distance_to_target_km > EARLY_DETECTION_THRESHOLD_KM:
        return {
            "action": "REROUTE",
            "reason": (
                f"Fish detected early at {detection['depth_m']:.0f} m depth "
                f"({detection['density_label']} density). Updating route."
            ),
            "new_lat": current_lat,
            "new_lon": current_lon,
            "confidence_boost": 5.0,
        }

    # ── Fish detected but close to target — stay course ───────────────
    return {
        "action": "CONTINUE",
        "reason": "Fish signal detected. Approaching predicted zone — maintaining route.",
        "new_lat": predicted_lat,
        "new_lon": predicted_lon,
        "confidence_boost": 3.0,
    }


# ─────────────────────────────────────────────
# Confidence Fusion
# ─────────────────────────────────────────────

def fuse_sonar_with_ai(
    ai_confidence: float,
    sonar_confidence: float,
    fish_detected: bool,
    density_label: str,
) -> Tuple[float, str]:
    """
    Combine AI prediction confidence with sonar detection confidence.

    Weights:
        AI model:  60%
        Sonar:     40%
    Bonus applied for High/Medium density detections.

    Args:
        ai_confidence:    AI model confidence score (0–100).
        sonar_confidence: Sonar detection confidence (0–100).
        fish_detected:    Whether sonar detected fish.
        density_label:    "None" | "Low" | "Medium" | "High"

    Returns:
        (fused_confidence, status_label) tuple.
    """
    if not fish_detected:
        # Sonar found nothing — slight downward pressure on AI confidence
        fused = ai_confidence * 0.92
        label = "AI Prediction Only"
    else:
        fused = 0.60 * ai_confidence + 0.40 * sonar_confidence
        # Density bonus
        bonus = {"High": 8.0, "Medium": 4.0, "Low": 1.0, "None": 0.0}
        fused = min(98.0, fused + bonus.get(density_label, 0.0))
        label = f"AI + Sonar ({density_label} density)"

    return round(fused, 1), label


# ─────────────────────────────────────────────
# Multi-Step Detection Loop
# ─────────────────────────────────────────────

def run_detection_loop(
    num_steps: int,
    base_sst: float,
    base_chlorophyll: float,
    zone_confidence: float,
    use_yolo: bool = False,
    delay_s: float = 0.0,
) -> List[Dict]:
    """
    Run a multi-step sonar scan session and return all results.

    Args:
        num_steps:        Number of scan steps to simulate.
        base_sst:         SST from AI features.
        base_chlorophyll: Chlorophyll from AI features.
        zone_confidence:  AI confidence score.
        use_yolo:         Whether to include YOLO stub.
        delay_s:          Optional sleep between steps (for real-time feel).

    Returns:
        List of detection result dicts, one per step.
    """
    results = []
    for step in range(num_steps):
        detection = detect_fish_with_model(
            step, base_sst, base_chlorophyll, zone_confidence, use_yolo
        )
        results.append(detection)
        logger.debug(
            "Step %d | detected=%s | depth=%.1f m | conf=%.1f%%",
            step, detection["fish_detected"], detection["depth_m"], detection["confidence"],
        )
        if delay_s > 0:
            time.sleep(delay_s)

    return results


# ─────────────────────────────────────────────
# Session Summary
# ─────────────────────────────────────────────

def summarise_session(results: List[Dict]) -> Dict:
    """
    Aggregate a detection loop session into summary statistics.

    Args:
        results: List returned by run_detection_loop().

    Returns:
        Summary dict with detection rate, peak confidence, etc.
    """
    if not results:
        return {}

    detected = [r for r in results if r["fish_detected"]]
    detection_rate = len(detected) / len(results) * 100

    confidences = [r["confidence"] for r in results]
    depths = [r["depth_m"] for r in results]
    counts = [r["estimated_count"] for r in results]

    density_counts = {"High": 0, "Medium": 0, "Low": 0, "None": 0}
    for r in results:
        density_counts[r["density_label"]] = density_counts.get(r["density_label"], 0) + 1

    return {
        "total_steps": len(results),
        "detection_rate_pct": round(detection_rate, 1),
        "peak_confidence": round(max(confidences), 1),
        "avg_confidence": round(float(np.mean(confidences)), 1),
        "avg_depth_m": round(float(np.mean(depths)), 1),
        "peak_count": max(counts),
        "density_distribution": density_counts,
        "dominant_density": max(density_counts, key=density_counts.get),
    }
