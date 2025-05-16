def final_strength_score(password, common_passwords_list):
    scores = {}
    scores["length"] = length_score(password)
    scores["variety"] = variety_score(password)
    scores["entropy"] = entropy_score(password)     # Scaled 0–10
    scores["pattern"] = repetition_and_pattern_score(password)
    scores["common"] = common_password_score(password, common_passwords_list)  # 0 if in list, else 10

    # Apply weights (as fractions of 1.0)
    weighted_total = (
        scores["length"] * 0.25 +
        scores["variety"] * 0.20 +
        scores["entropy"] * 0.25 +
        scores["pattern"] * 0.15 +
        scores["common"] * 0.15
    )

    return round(weighted_total, 2), scores 