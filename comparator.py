# ==========================================
# THUMBNAILIQ - Thumbnail Comparator
# ==========================================
# This file compares two thumbnails across all metrics and produces
# a winner prediction, confidence score, and human-readable explanation.

# Step 1: Import the analyzer functions for all 8 metrics
from analyzer import (
    calculate_brightness,
    calculate_contrast,
    calculate_sharpness,
    calculate_colorfulness,
    calculate_face_score,
    calculate_text_score,
    calculate_clutter_score,
    calculate_focus_score,
)

# ==========================================
# CONFIGURATION: Metric Weights
# ==========================================
# These weights determine how much each metric contributes to the overall score.
# All weights MUST sum to 1.0 — adjust them to re-tune the prediction model.
#
# Current rationale:
#   - Face and colorfulness are the biggest CTR drivers (YouTube research)
#   - Focus and sharpness matter for first impressions
#   - Brightness/contrast are important but secondary
#   - Text and clutter are useful but context-dependent
WEIGHTS = {
    "sharpness":    0.12,   # Sharp images look professional
    "contrast":     0.10,   # Contrast separates subject from background
    "brightness":   0.10,   # Brightness affects mood and visibility
    "colorfulness": 0.18,   # Vibrant colors catch the eye in feeds
    "face":         0.20,   # Human faces drive emotional engagement
    "text":         0.10,   # Well-placed text adds context
    "clutter":      0.10,   # Clean compositions read faster
    "focus":        0.10,   # Clear focal point guides the viewer's eye
}

# Sanity check: weights must sum to 1.0
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "WEIGHTS must sum to 1.0"

# Gap threshold: if the score difference is less than this, it's a Tie
TIE_THRESHOLD = 3.0

# Metric display names (for human-readable output)
METRIC_LABELS = {
    "sharpness":    "Sharpness",
    "contrast":     "Contrast",
    "brightness":   "Brightness",
    "colorfulness": "Colorfulness",
    "face":         "Face Presence",
    "text":         "Text Quality",
    "clutter":      "Clean Composition",
    "focus":        "Focus / Saliency",
}

# Metric descriptions used in explanations
METRIC_DESCRIPTIONS = {
    "sharpness":    "crisp image detail",
    "contrast":     "tonal range",
    "brightness":   "overall exposure",
    "colorfulness": "vibrant colors",
    "face":         "visible face presence",
    "text":         "text overlay quality",
    "clutter":      "clean, uncluttered layout",
    "focus":        "a clear focal point",
}

# Improvement tips for the weakest metrics
IMPROVEMENT_TIPS = {
    "sharpness":    "Try re-exporting at higher resolution or apply a slight unsharp mask to boost edge crispness.",
    "contrast":     "Increase the contrast in your image editor (Levels or Curves) to make subjects pop against the background.",
    "brightness":   "Adjust brightness toward 50-70% — brighten dark thumbnails or reduce over-exposed highlights.",
    "colorfulness": "Use more saturated colors or add a vibrant color accent (e.g., bold text box, brighter clothing).",
    "face":         "Include a clear, expressive face at medium size (5-40% of frame) to boost emotional engagement.",
    "text":         "Add a short, bold text overlay (2-4 words) with high contrast against the background.",
    "clutter":      "Simplify the composition — remove background elements and keep 1-2 main subjects.",
    "focus":        "Place your main subject at a rule-of-thirds intersection to guide the viewer's eye naturally.",
}


# ==========================================
# HELPER: Compute all 8 metric scores
# ==========================================

def _compute_all_metrics(image):
    """
    Run all 8 metric functions on a single PIL Image and return a score dict.

    Each metric call is wrapped in a try/except so one failure never
    blocks the rest of the comparison.

    Args:
        image (PIL.Image): The thumbnail to analyze.

    Returns:
        dict: {metric_key: score (0-100)} for all 8 metrics.
    """
    # Map metric keys to their corresponding analyzer functions
    metric_functions = {
        "sharpness":    calculate_sharpness,
        "contrast":     calculate_contrast,
        "brightness":   calculate_brightness,
        "colorfulness": calculate_colorfulness,
        "face":         calculate_face_score,
        "text":         calculate_text_score,
        "clutter":      calculate_clutter_score,
        "focus":        calculate_focus_score,
    }

    scores = {}
    for key, func in metric_functions.items():
        try:
            scores[key] = func(image)
        except Exception:
            # Neutral fallback keeps the comparison meaningful even on failures
            scores[key] = 50.0

    return scores


# ==========================================
# HELPER: Weighted overall score
# ==========================================

def _weighted_score(metric_scores):
    """
    Calculate the weighted overall score from individual metric scores.

    Args:
        metric_scores (dict): {metric_key: score} for all metrics.

    Returns:
        float: Weighted total score (0-100), rounded to 2 decimal places.
    """
    total = sum(WEIGHTS[key] * metric_scores[key] for key in WEIGHTS)
    return round(total, 2)


# ==========================================
# HELPER: Build plain-English explanation
# ==========================================

def _build_explanation(winner, scores_a, scores_b, top_deciding_metrics):
    """
    Generate a plain-English explanation of why one thumbnail won.

    Args:
        winner (str): "A", "B", or "Tie".
        scores_a (dict): Metric scores for Thumbnail A.
        scores_b (dict): Metric scores for Thumbnail B.
        top_deciding_metrics (list): The 3 metrics with the biggest weighted gap.

    Returns:
        str: Human-readable explanation sentence.
    """
    if winner == "Tie":
        return (
            "Both thumbnails are very closely matched overall. "
            "Minor differences in individual metrics cancel each other out — "
            "consider A/B testing them with real audiences to break the tie."
        )

    loser = "B" if winner == "A" else "A"
    winner_scores = scores_a if winner == "A" else scores_b
    loser_scores = scores_b if winner == "A" else scores_a

    # Describe the top 3 deciding factors
    deciding_parts = []
    for metric in top_deciding_metrics:
        label = METRIC_DESCRIPTIONS[metric]
        w_score = winner_scores[metric]
        l_score = loser_scores[metric]
        gap = abs(w_score - l_score)
        if gap >= 15:
            qualifier = "significantly stronger"
        elif gap >= 7:
            qualifier = "noticeably better"
        else:
            qualifier = "slightly higher scoring"
        deciding_parts.append(f"{qualifier} {label}")

    deciding_str = ", ".join(deciding_parts)

    explanation = (
        f"Thumbnail {winner} wins mainly because of {deciding_str}. "
        f"Thumbnail {loser} would benefit from improvements in those areas."
    )

    return explanation


# ==========================================
# HELPER: Generate improvement suggestions
# ==========================================

def _build_improvement_suggestions(winner, scores_a, scores_b):
    """
    Generate 1-2 concrete improvement tips for the losing thumbnail
    based on its lowest weighted metric scores.

    Args:
        winner (str): "A", "B", or "Tie".
        scores_a (dict): Metric scores for Thumbnail A.
        scores_b (dict): Metric scores for Thumbnail B.

    Returns:
        list[str]: 1-2 improvement suggestion strings for the loser,
                   or an empty list on a Tie.
    """
    if winner == "Tie":
        return []

    # The loser is the thumbnail we want to improve
    loser_scores = scores_b if winner == "A" else scores_a

    # Rank metrics by their weighted impact (weight * (100 - score) = room for improvement)
    improvement_potential = {
        key: WEIGHTS[key] * (100.0 - loser_scores[key])
        for key in WEIGHTS
    }

    # Sort from highest potential improvement to lowest
    ranked = sorted(improvement_potential.items(), key=lambda x: x[1], reverse=True)

    # Pick the top 2 metrics with the most room to grow
    suggestions = []
    for metric_key, _ in ranked[:2]:
        suggestions.append(f"💡 {IMPROVEMENT_TIPS[metric_key]}")

    return suggestions


# ==========================================
# MAIN: compare_thumbnails
# ==========================================

def compare_thumbnails(img_a, img_b):
    """
    Compare two PIL Images across all 8 metrics and predict the better thumbnail.

    This is the main entry point for the comparison feature.

    Args:
        img_a (PIL.Image): The first thumbnail (Thumbnail A).
        img_b (PIL.Image): The second thumbnail (Thumbnail B).

    Returns:
        dict with the following keys:
            scores_a         (dict)  -- per-metric scores for Thumbnail A
            scores_b         (dict)  -- per-metric scores for Thumbnail B
            overall_a        (float) -- weighted overall score for A
            overall_b        (float) -- weighted overall score for B
            winner           (str)   -- "A", "B", or "Tie"
            confidence       (float) -- confidence % based on score gap (0-100)
            top_metrics      (list)  -- top 3 metrics that decided the result
            explanation      (str)   -- plain-English explanation of the outcome
            suggestions      (list)  -- 1-2 improvement tips for the losing thumbnail
            metric_labels    (dict)  -- human-readable label for each metric key
    """
    # Step 1: Compute all 8 metric scores for both thumbnails
    scores_a = _compute_all_metrics(img_a)
    scores_b = _compute_all_metrics(img_b)

    # Step 2: Calculate weighted overall scores
    overall_a = _weighted_score(scores_a)
    overall_b = _weighted_score(scores_b)

    # Step 3: Determine winner
    score_gap = overall_a - overall_b
    if abs(score_gap) < TIE_THRESHOLD:
        winner = "Tie"
    elif score_gap > 0:
        winner = "A"
    else:
        winner = "B"

    # Step 4: Calculate confidence based on the size of the score gap
    # 0 gap = 50% confidence (coin flip), 20+ gap = ~100% confidence
    raw_confidence = min(abs(score_gap) / 20.0, 1.0)
    # Map to 50%-100% range (even a weak winner has at least 50% confidence)
    confidence = round(50.0 + raw_confidence * 50.0, 1)

    # Step 5: Find the top 3 metrics that contributed most to the decision
    # For each metric, weighted gap = weight * |score_A - score_B|
    metric_gaps = {
        key: WEIGHTS[key] * abs(scores_a[key] - scores_b[key])
        for key in WEIGHTS
    }
    top_metrics = sorted(metric_gaps, key=metric_gaps.get, reverse=True)[:3]

    # Step 6: Build plain-English explanation
    explanation = _build_explanation(winner, scores_a, scores_b, top_metrics)

    # Step 7: Generate improvement suggestions for the loser
    suggestions = _build_improvement_suggestions(winner, scores_a, scores_b)

    # Step 8: Return the full result dictionary
    return {
        "scores_a":      scores_a,
        "scores_b":      scores_b,
        "overall_a":     overall_a,
        "overall_b":     overall_b,
        "winner":        winner,
        "confidence":    confidence,
        "top_metrics":   top_metrics,
        "explanation":   explanation,
        "suggestions":   suggestions,
        "metric_labels": METRIC_LABELS,
    }
