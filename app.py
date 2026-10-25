# ==========================================
# THUMBNAILIQ - YouTube Thumbnail Comparator
# ==========================================
# This program uses Streamlit to build a web app that analyzes and compares
# YouTube thumbnails using computer vision metrics.

# STEP 1: Import necessary libraries
import hashlib
import io

import pandas as pd
import streamlit as st

# 'PIL' (Pillow) is used for opening and handling image files.
# ImageOps fixes phone photos that are rotated through EXIF data.
from PIL import Image, ImageOps, UnidentifiedImageError

# Import all metric functions from analyzer.py
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

# Import the comparison engine from comparator.py
from comparator import compare_thumbnails, METRIC_LABELS

# Import the design system (CSS + HTML helpers)
from styles import (
    load_css,
    render_html,
    hero_html,
    col_header_html,
    placeholder_html,
    metrics_card_html,
    winner_badge_html,
    verdict_card_html,
    metrics_table_html,
    explanation_card_html,
    suggestions_card_html,
    tie_suggestions_html,
    disclaimer_html,
)


# STEP 2: Settings and constants
TARGET_SIZE = (1280, 720)   # Every image is resized to this before analysis (fair comparison)
MAX_FILE_MB = 10            # Reject very large uploads

# One place that lists every metric: {metric key: function}
# The keys must match the keys in METRIC_LABELS (comparator.py).
METRIC_FUNCTIONS = {
    "brightness":   calculate_brightness,
    "contrast":     calculate_contrast,
    "sharpness":    calculate_sharpness,
    "colorfulness": calculate_colorfulness,
    "face":         calculate_face_score,
    "text":         calculate_text_score,
    "clutter":      calculate_clutter_score,
    "focus":        calculate_focus_score,
}


# STEP 3: Configure the web page
st.set_page_config(
    page_title="ThumbnailIQ",
    page_icon="🖼️",
    layout="wide"  # "wide" layout gives more horizontal space for side-by-side view
)

# Inject design-system CSS (call once, immediately after set_page_config)
load_css()


# STEP 4: Image helper functions
def decode_image(file_bytes):
    """
    Turn raw uploaded bytes into an RGB PIL image.
    - Fixes EXIF rotation (phone photos)
    - Converts PNGs with transparency (RGBA) to plain RGB
    """
    image = Image.open(io.BytesIO(file_bytes))
    image = ImageOps.exif_transpose(image)
    return image.convert("RGB")


def prepare_for_analysis(image):
    """Resize to a fixed size so every metric is computed on the same scale."""
    return image.resize(TARGET_SIZE, Image.LANCZOS)


# STEP 5: Metric computation (cached)
def compute_metrics(image):
    """
    Run all analysis functions on one PIL image.
    Each metric is wrapped separately so one failure doesn't stop the rest.
    Failures are printed to the terminal instead of being hidden silently.

    Returns:
        dict: {metric_name: score or None}
    """
    metrics = {}
    for name, func in METRIC_FUNCTIONS.items():
        try:
            metrics[name] = func(image)
        except Exception as e:
            print(f"[ThumbnailIQ] metric '{name}' failed: {e}")
            metrics[name] = None
    return metrics


# st.cache_data remembers results by the file's bytes, so reruns
# (button clicks, widget changes) do NOT recompute everything.
@st.cache_data(show_spinner=False)
def cached_metrics(file_bytes):
    image = prepare_for_analysis(decode_image(file_bytes))
    return compute_metrics(image)


@st.cache_data(show_spinner=False)
def cached_compare(bytes_a, bytes_b):
    image_a = prepare_for_analysis(decode_image(bytes_a))
    image_b = prepare_for_analysis(decode_image(bytes_b))
    return compare_thumbnails(image_a, image_b)


# STEP 6: Column rendering
def render_thumbnail_column(name, key):
    """
    Draw one column: header, uploader, preview and metric bars.

    Returns:
        (file_bytes or None, metrics or None, badge_slot)
        badge_slot is an empty placeholder under the header; the winner
        badge is filled in later, so it appears above the matching thumbnail.
    """
    render_html(col_header_html(name))
    badge_slot = st.empty()

    uploaded = st.file_uploader(
        f"Upload Thumbnail {name}",
        type=["png", "jpg", "jpeg"],
        key=key,
        label_visibility="collapsed",
    )

    if uploaded is None:
        render_html(placeholder_html(name))
        return None, None, badge_slot

    # Validate the file before doing any work
    file_bytes = uploaded.getvalue()
    if len(file_bytes) > MAX_FILE_MB * 1024 * 1024:
        st.error(f"File is larger than {MAX_FILE_MB} MB. Please upload a smaller image.")
        return None, None, badge_slot

    try:
        image = decode_image(file_bytes)
    except (UnidentifiedImageError, OSError, ValueError):
        st.error("Could not read this image. Please upload a valid PNG or JPG file.")
        return None, None, badge_slot

    st.image(image, caption=f"Thumbnail {name} Preview", width="stretch")

    with st.spinner(f"Analyzing Thumbnail {name}…"):
        metrics = cached_metrics(file_bytes)

    render_html(metrics_card_html(metrics, METRIC_LABELS, name))

    return file_bytes, metrics, badge_slot


# STEP 7: Results display
def show_results(result, badge_slot_a, badge_slot_b):
    """Render the full comparison result."""
    winner      = result.get("winner", "Tie")
    overall_a   = result.get("overall_a", 0)
    overall_b   = result.get("overall_b", 0)
    confidence  = result.get("confidence", 0)
    scores_a    = result.get("scores_a", {})
    scores_b    = result.get("scores_b", {})
    top3        = result.get("top_metrics", []) or []
    explanation = result.get("explanation", "")
    suggestions = result.get("suggestions", []) or []
    labels      = result.get("metric_labels", METRIC_LABELS)

    # ---- Winner badge above the matching thumbnail ----
    with badge_slot_a:
        render_html(winner_badge_html(winner, "A"))
    with badge_slot_b:
        render_html(winner_badge_html(winner, "B"))

    # ---- Verdict card ----
    render_html(verdict_card_html(winner, overall_a, overall_b, confidence))

    st.divider()

    # ---- Side-by-side metrics table ----
    render_html('<div class="tiq-section-head">Metric-by-Metric Comparison</div>')
    render_html(
        '<p style="font-size:12px;color:#8A8F9C;margin-bottom:16px;">'
        'Dots mark the top deciding metrics. Winning values are highlighted.</p>'
    )
    render_html(metrics_table_html(scores_a, scores_b, labels, top3))

    st.divider()

    # ---- Grouped bar chart ----
    render_html('<div class="tiq-section-head">Metric Scores Chart</div>')

    metric_names = [labels[k] for k in labels]
    # "or 0" turns a missing OR None score into 0 so the chart never crashes
    vals_a = [scores_a.get(k) or 0 for k in labels]
    vals_b = [scores_b.get(k) or 0 for k in labels]

    try:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Thumbnail A",
            x=metric_names,
            y=vals_a,
            marker_color="#2F5BFF",
            marker_line_width=0,
            text=[f"{v:.1f}" for v in vals_a],
            textposition="outside",
            textfont=dict(family="Inter", size=11, color="#5B6070"),
        ))
        fig.add_trace(go.Bar(
            name="Thumbnail B",
            x=metric_names,
            y=vals_b,
            marker_color="#FF6A3D",
            marker_line_width=0,
            text=[f"{v:.1f}" for v in vals_b],
            textposition="outside",
            textfont=dict(family="Inter", size=11, color="#5B6070"),
        ))
        fig.update_layout(
            barmode="group",
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            font=dict(family="Inter", size=12, color="#5B6070"),
            yaxis=dict(
                range=[0, 115],
                title="Score (0–100)",
                showgrid=True,
                gridcolor="#E7E5E0",
                zeroline=False,
                tickfont=dict(size=11),
            ),
            xaxis=dict(
                title=None,
                showgrid=False,
                tickfont=dict(size=11),
            ),
            legend=dict(
                orientation="h",
                y=1.12,
                x=0,
                bgcolor="rgba(0,0,0,0)",
                font=dict(size=12),
            ),
            margin=dict(t=48, b=32, l=8, r=8),
            height=420,
            bargap=0.22,
            bargroupgap=0.08,
        )
        st.plotly_chart(fig, width="stretch")

    except ImportError:
        st.warning("Install `plotly` (pip install plotly) to see the chart. Showing a simple version instead.")
        chart_df = pd.DataFrame(
            {"Thumbnail A": vals_a, "Thumbnail B": vals_b},
            index=metric_names,
        )
        st.bar_chart(chart_df)

    st.divider()

    # ---- Explanation ----
    render_html('<div class="tiq-section-head">Analysis</div>')
    render_html(explanation_card_html(explanation, top3, labels))

    st.divider()

    # ---- Improvement suggestions (only when there is a clear loser) ----
    if winner != "Tie" and suggestions:
        loser_label = "Thumbnail B" if winner == "A" else "Thumbnail A"
        render_html(suggestions_card_html(suggestions, loser_label))
    else:
        render_html(tie_suggestions_html())

    # ---- Disclaimer ----
    render_html(disclaimer_html())


# STEP 8: Main page
render_html(hero_html())
st.divider()

col1, col2 = st.columns(2)

with col1:
    data_1, metrics_1, badge_slot_1 = render_thumbnail_column("A", "thumb1")

with col2:
    data_2, metrics_2, badge_slot_2 = render_thumbnail_column("B", "thumb2")


# STEP 9: Compare & Predict (only when BOTH images are valid)
if data_1 is not None and data_2 is not None:
    st.divider()
    render_html('<div class="tiq-section-head">Compare &amp; Predict</div>')

    # A signature of the current pair of images. If the user uploads a new
    # image, the signature changes and the old result is hidden automatically.
    current_sig = (
        hashlib.md5(data_1).hexdigest(),
        hashlib.md5(data_2).hexdigest(),
    )

    if st.button("Compare & Predict Winner", type="primary"):
        st.session_state["compared_sig"] = current_sig

    # Show the result whenever it was requested for THESE two images.
    # Because of session_state, it stays visible across reruns.
    if st.session_state.get("compared_sig") == current_sig:
        result = None
        try:
            with st.spinner("Running full comparison. Face and text detection may take a moment…"):
                result = cached_compare(data_1, data_2)
        except Exception as e:
            st.error(f"Comparison failed: {e}")

        if result is not None:
            show_results(result, badge_slot_1, badge_slot_2)