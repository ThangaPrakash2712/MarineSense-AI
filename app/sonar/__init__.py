"""
Sonar Detection Module for MarineSense AI
"""

from .sonar_module import (
    SonarFrame,
    SonarReading,
    simulate_sonar_input,
    process_sonar_data,
    generate_alert,
    run_sonar_scan,
)

from .detect_sonar import (
    detect_fish_with_model,
    update_route_decision,
    fuse_sonar_with_ai,
    run_detection_loop,
    summarise_session,
)

__all__ = [
    # sonar_module
    "SonarFrame",
    "SonarReading",
    "simulate_sonar_input",
    "process_sonar_data",
    "generate_alert",
    "run_sonar_scan",
    # detect_sonar
    "detect_fish_with_model",
    "update_route_decision",
    "fuse_sonar_with_ai",
    "run_detection_loop",
    "summarise_session",
]
