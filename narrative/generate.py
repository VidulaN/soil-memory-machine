def generate_narrative(features, prediction, probabilities):
    """
    Takes model inputs and outputs and returns a plain English narrative.
    features: dict of feature values
    prediction: 0 or 1
    probabilities: [prob_no_drought, prob_drought]
    """

    drought_prob = round(probabilities[1] * 100)
    precip_30 = features["precip_30day"]
    precip_7  = features["precip_7day"]
    temp_max  = features["temp_max"]
    temp_7    = features["temp_7day"]
    evap      = features["evapotranspiration"]

    # ── Rainfall narrative ────────────────────────────────────────────────────
    if precip_30 < 0.5:
        rain_sentence = f"Rainfall over the past 30 days has been critically low, averaging just {precip_30:.1f}mm per day."
    elif precip_30 < 1.5:
        rain_sentence = f"Rainfall has been below normal over the past month, averaging {precip_30:.1f}mm per day."
    else:
        rain_sentence = f"Rainfall has been relatively stable over the past month, averaging {precip_30:.1f}mm per day."

    # ── Recent rain trend ─────────────────────────────────────────────────────
    if precip_7 < precip_30 * 0.5:
        trend_sentence = "The past week has been notably drier than the month average — conditions are worsening."
    elif precip_7 > precip_30 * 1.5:
        trend_sentence = "The past week has seen more rain than usual — a potentially positive sign."
    else:
        trend_sentence = "Recent rainfall is consistent with the monthly pattern."

    # ── Temperature narrative ─────────────────────────────────────────────────
    if temp_max > 36:
        temp_sentence = f"Temperatures are high, reaching {temp_max:.1f}°C, which is accelerating moisture loss from the soil."
    elif temp_max > 32:
        temp_sentence = f"Temperatures are elevated at {temp_max:.1f}°C, putting additional stress on crops."
    else:
        temp_sentence = f"Temperatures are within a normal range at {temp_max:.1f}°C."

    # ── Risk conclusion ───────────────────────────────────────────────────────
    if prediction == 1:
        if drought_prob > 85:
            conclusion = f"The soil memory model rates drought risk as HIGH ({drought_prob}%). Conditions closely match historical drought patterns. Immediate action is advised."
        else:
            conclusion = f"The soil memory model rates drought risk as MODERATE-HIGH ({drought_prob}%). Monitor conditions closely over the coming week."
    else:
        if drought_prob < 15:
            conclusion = f"The soil memory model rates drought risk as LOW ({drought_prob}%). Current conditions do not suggest immediate concern."
        else:
            conclusion = f"The soil memory model rates drought risk as LOW-MODERATE ({drought_prob}%). Conditions are stable but worth watching."

    # ── Driver explanation ────────────────────────────────────────────────────
    driver_sentence = "This assessment is primarily driven by 30-day and 7-day rainfall patterns, combined with recent temperature trends."

    narrative = f"""
{rain_sentence} {trend_sentence}

{temp_sentence}

{conclusion}

{driver_sentence}
    """.strip()

    return narrative


# ── Test it standalone ────────────────────────────────────────────────────────
if __name__ == "__main__":
    test_features = {
        "precip_30day": 0.4,
        "precip_7day": 0.1,
        "temp_max": 35.2,
        "temp_7day": 34.8,
        "evapotranspiration": 6.1,
        "precipitation": 0.0
    }
    result = generate_narrative(test_features, prediction=1, probabilities=[0.12, 0.88])
    print(result)