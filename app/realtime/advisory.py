"""
Smart Marine Advisory Engine
Generates professional fishing and navigation guidance
"""

from typing import Dict

def generate_marine_advisory(weather_risk: str, fish_level: float, 
                            distance: float, wave_height: float = 1.5,
                            wind_speed: float = 12.0) -> Dict:
    """
    Generate comprehensive marine advisory for fishing operations.
    
    Args:
        weather_risk: Risk level (Safe/Moderate/Dangerous)
        fish_level: Predicted fish quantity
        distance: Distance to fishing zone in km
        wave_height: Current wave height in meters
        wind_speed: Current wind speed in m/s
        
    Returns:
        Dictionary with advisory components
    """
    
    # Sailing Safety Assessment
    if weather_risk == "Safe":
        safety_msg = "✅ Excellent sailing conditions. Sea state is favorable for all vessel types."
    elif weather_risk == "Moderate":
        safety_msg = "⚠️ Moderate sea conditions. Experienced operators only. Monitor weather closely."
    else:
        safety_msg = "🚨 Hazardous conditions. Navigation not recommended. Seek shelter."
    
    # Fishing Opportunity Quality
    if fish_level > 250:
        fishing_msg = "🎯 Exceptional fishing opportunity. High fish aggregation detected."
    elif fish_level >= 150:
        fishing_msg = "📊 Good fishing potential. Moderate fish population expected."
    else:
        fishing_msg = "⚠️ Limited fishing opportunity. Consider alternative locations."
    
    # Distance Assessment
    if distance < 30:
        distance_msg = "📍 Target zone is nearby. Short trip duration."
    elif distance < 80:
        distance_msg = "🚤 Moderate distance to target. Plan adequate fuel reserves."
    else:
        distance_msg = "⛵ Extended voyage required. Ensure full preparation and supplies."
    
    # Risk Explanation
    risk_factors = []
    if wind_speed > 20:
        risk_factors.append("High wind speeds detected")
    if wave_height > 3.0:
        risk_factors.append("Elevated wave heights")
    if weather_risk == "Dangerous":
        risk_factors.append("Severe weather conditions")
    
    if risk_factors:
        risk_explanation = "Risk factors: " + ", ".join(risk_factors)
    else:
        risk_explanation = "No significant risk factors identified"
    
    # Recommended Action
    if weather_risk == "Safe" and fish_level > 150:
        action = "🟢 PROCEED - Conditions favorable for fishing operations"
    elif weather_risk == "Moderate" and fish_level > 100:
        action = "🟡 CAUTION - Proceed with enhanced safety measures"
    elif weather_risk == "Dangerous":
        action = "🔴 ABORT - Do not proceed. Conditions unsafe"
    else:
        action = "🟡 EVALUATE - Assess risk vs. reward carefully"
    
    return {
        "safety_assessment": safety_msg,
        "fishing_opportunity": fishing_msg,
        "distance_assessment": distance_msg,
        "risk_explanation": risk_explanation,
        "recommended_action": action,
        "overall_rating": _calculate_overall_rating(weather_risk, fish_level, distance)
    }


def _calculate_overall_rating(weather_risk: str, fish_level: float, distance: float) -> str:
    """Calculate overall trip rating."""
    score = 0
    
    # Weather component
    if weather_risk == "Safe":
        score += 40
    elif weather_risk == "Moderate":
        score += 20
    
    # Fish component
    if fish_level > 250:
        score += 40
    elif fish_level >= 150:
        score += 25
    elif fish_level >= 100:
        score += 10
    
    # Distance component
    if distance < 50:
        score += 20
    elif distance < 100:
        score += 10
    
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"
