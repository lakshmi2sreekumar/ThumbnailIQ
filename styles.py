"""
styles.py — ThumbnailIQ Design System
======================================
All CSS and HTML helper functions live here.
app.py calls load_css() once at the top; everything else is untouched logic.

DESIGN TOKENS (also mirrored in .streamlit/config.toml):
  Backgrounds  : --bg          #FAFAF8  |  --surface  #FFFFFF
  Borders      : --border      #E7E5E0
  Text         : --text-primary #16181D  |  --text-secondary #5B6070  |  --text-muted #8A8F9C
  Accent A     : --accent-a    #2F5BFF  (blue)
  Accent B     : --accent-b    #FF6A3D  (orange)
  Success      : --success     #12805C  |  --success-bg  #E7F5EF
  Warning      : --warning     #9A6700  |  --warning-bg  #FFF4D6
  Fonts        : "Manrope" (headings 600-800) + "Inter" (body/UI 400-600)
"""

import streamlit as st

# ---------------------------------------------------------------------------
# CSS string
# ---------------------------------------------------------------------------

_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@600;700;800&display=swap');

/* Design tokens */
:root {
  --bg:               #FAFAF8;
  --surface:          #FFFFFF;
  --border:           #E7E5E0;
  --shadow:           0 1px 4px rgba(0,0,0,.06), 0 0 0 1px var(--border);
  --shadow-md:        0 4px 16px rgba(0,0,0,.08), 0 0 0 1px var(--border);

  --text-primary:     #16181D;
  --text-secondary:   #5B6070;
  --text-muted:       #8A8F9C;

  --accent-a:         #2F5BFF;
  --accent-a-soft:    #EEF2FF;
  --accent-b:         #FF6A3D;
  --accent-b-soft:    #FFF2ED;

  --success:          #12805C;
  --success-bg:       #E7F5EF;
  --warning:          #9A6700;
  --warning-bg:       #FFF4D6;
  --neutral:          #5B6070;
  --neutral-bg:       #F0F0EE;

  --radius-sm:        6px;
  --radius-md:        10px;
  --radius-lg:        14px;
  --radius-xl:        20px;

  --font-head: 'Manrope', system-ui, sans-serif;
  --font-body: 'Inter', system-ui, sans-serif;
}

/* Global reset / base */
html, body, .stApp, [data-testid="stApp"], [class*="css"] {
  font-family: var(--font-body) !important;
  color: var(--text-primary);
  background-color: var(--bg) !important;
}

/* Hide Streamlit chrome */
#MainMenu,
footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"] {
  display: none !important;
}

/* Tighten Streamlit's default top padding */
[data-testid="stAppViewContainer"] > .main > .block-container {
  padding-top: 32px !important;
  padding-bottom: 64px !important;
  max-width: 1200px;
}

/* Typography overrides */
h1, h2, h3, h4 {
  font-family: var(--font-head) !important;
  letter-spacing: -0.02em;
  color: var(--text-primary) !important;
}

h2 { font-size: 22px !important; font-weight: 700 !important; }
h3 { font-size: 17px !important; font-weight: 600 !important; }

p, li, label {
  font-family: var(--font-body) !important;
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* Spans: same sizing/color as before, but NO forced font-family, so
   Streamlit's icon spans keep their icon font. Normal spans inherit Inter
   from the page container below. */
span {
  font-size: 15px;
  line-height: 1.6;
  color: var(--text-secondary);
}

/* Dividers */
hr { border: none; border-top: 1px solid var(--border); margin: 32px 0; }

/* st.file_uploader */
[data-testid="stFileUploader"] {
  background: var(--surface) !important;
  border: 2px dashed var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 20px !important;
  transition: border-color .2s;
}
[data-testid="stFileUploader"]:focus-within {
  border-color: var(--accent-a) !important;
  box-shadow: 0 0 0 3px rgba(47,91,255,.12) !important;
}
[data-testid="stFileUploaderDropzone"] {
  background: transparent !important;
  border: none !important;
}

/* Uploaded image rounded preview */
[data-testid="stImage"] img {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border) !important;
  box-shadow: var(--shadow) !important;
  width: 100% !important;
  object-fit: cover !important;
}

/* Buttons */
[data-testid="stButton"] > button {
  background: var(--text-primary) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: var(--radius-md) !important;
  padding: 10px 24px !important;
  font-family: var(--font-body) !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  transition: background .18s, box-shadow .18s, transform .12s !important;
  cursor: pointer !important;
}
[data-testid="stButton"] > button:hover {
  background: #2A2D35 !important;
  box-shadow: 0 4px 14px rgba(0,0,0,.18) !important;
  transform: translateY(-1px) !important;
}
[data-testid="stButton"] > button:active {
  transform: translateY(0) !important;
}
[data-testid="stButton"] > button:focus-visible {
  outline: 2px solid var(--accent-a) !important;
  outline-offset: 3px !important;
}

/* Hide native progress bars (replaced by custom HTML) */
[data-testid="stProgress"] { display: none !important; }

/* st.metric widget */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  padding: 20px 24px !important;
  box-shadow: var(--shadow) !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
  font-size: 12px !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
  font-family: var(--font-head) !important;
  font-size: 28px !important;
  font-weight: 800 !important;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
  border-radius: var(--radius-lg) !important;
  border: 1px solid var(--border) !important;
  overflow: hidden !important;
  box-shadow: var(--shadow) !important;
}

/* Alerts */
[data-testid="stAlert"] {
  border-radius: var(--radius-md) !important;
  border-left-width: 3px !important;
  font-size: 14px !important;
}

/* Caption */
[data-testid="stCaptionContainer"] {
  font-size: 13px !important;
  color: var(--text-muted) !important;
  line-height: 1.5;
}

/* ---- Custom component classes ---- */

/* Hero */
.tiq-hero {
  padding: 40px 0 32px;
}
.tiq-wordmark {
  font-family: var(--font-head);
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-primary);
  margin: 0 0 12px;
  line-height: 1;
}
.tiq-wordmark span {
  color: var(--accent-a);
  font-size: inherit;
  font-family: inherit;
  font-weight: inherit;
  letter-spacing: inherit;
}
.tiq-tagline {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 400;
  margin: 0;
}

/* Section label */
.tiq-section-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
  margin: 0 0 12px;
}

/* Column label chips */
.tiq-col-label-a, .tiq-col-label-b {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  font-family: var(--font-head);
  font-size: 14px;
  font-weight: 800;
  line-height: 1;
  margin-right: 8px;
  vertical-align: middle;
}
.tiq-col-label-a { background: var(--accent-a-soft); color: var(--accent-a); }
.tiq-col-label-b { background: var(--accent-b-soft); color: var(--accent-b); }

.tiq-col-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}
.tiq-col-header-text {
  font-family: var(--font-head);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

/* Card */
.tiq-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

/* Metric row */
.tiq-metric-row { margin-bottom: 16px; }
.tiq-metric-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 4px;
}
.tiq-metric-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}
.tiq-metric-right { display: flex; align-items: center; gap: 8px; }
.tiq-metric-score {
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--text-primary);
}
.tiq-metric-tag {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
}
.tiq-tag-high   { background: var(--success-bg); color: var(--success); }
.tiq-tag-medium { background: var(--warning-bg); color: var(--warning); }
.tiq-tag-low    { background: #FEE9E9; color: #C0392B; }
.tiq-tag-na     { background: var(--neutral-bg); color: var(--text-muted); }

/* Slim metric bar */
.tiq-bar-track {
  height: 6px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}
.tiq-bar-fill {
  height: 100%;
  border-radius: 99px;
  transition: width .4s ease;
}
.tiq-bar-a { background: var(--accent-a); }
.tiq-bar-b { background: var(--accent-b); }

/* Placeholder */
.tiq-placeholder {
  padding: 32px 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
  background: var(--surface);
  border: 2px dashed var(--border);
  border-radius: var(--radius-lg);
}
.tiq-placeholder-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 12px;
  opacity: .4;
}

/* Winner / badge pills */
.tiq-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  margin-bottom: 12px;
}
.tiq-badge-winner { background: var(--success-bg); color: var(--success); }
.tiq-badge-tie    { background: var(--neutral-bg);  color: var(--neutral); }

/* Verdict card */
.tiq-verdict-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 32px 40px;
  box-shadow: var(--shadow-md);
  margin-bottom: 32px;
}
.tiq-verdict-title {
  font-family: var(--font-head);
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0 0 16px;
}
.tiq-verdict-scores {
  display: flex;
  gap: 32px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.tiq-verdict-score-block { display: flex; flex-direction: column; gap: 2px; }
.tiq-verdict-score-label {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text-muted);
}
.tiq-verdict-score-value {
  font-family: var(--font-head);
  font-size: 40px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.03em;
  line-height: 1;
}
.tiq-score-a   { color: var(--accent-a); }
.tiq-score-b   { color: var(--accent-b); }
.tiq-score-tie { color: var(--text-secondary); }

/* Confidence bar */
.tiq-confidence-row { display: flex; align-items: center; gap: 12px; }
.tiq-confidence-track {
  flex: 1;
  height: 6px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}
.tiq-confidence-fill {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, #2F5BFF 0%, #12805C 100%);
  transition: width .6s ease;
}
.tiq-confidence-label {
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
  white-space: nowrap;
}

/* Metrics comparison table */
.tiq-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.tiq-table thead th {
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: var(--text-muted);
  padding: 8px 16px;
  border-bottom: 2px solid var(--border);
  text-align: left;
}
.tiq-table tbody tr {
  border-bottom: 1px solid var(--border);
  transition: background .15s;
}
.tiq-table tbody tr:last-child { border-bottom: none; }
.tiq-table tbody tr:hover { background: var(--bg); }
.tiq-table td {
  padding: 10px 16px;
  font-variant-numeric: tabular-nums;
  color: var(--text-secondary);
}
.tiq-table td.metric-name { font-weight: 500; color: var(--text-primary); }
.tiq-table td.win-a { color: var(--accent-a); font-weight: 600; }
.tiq-table td.win-b { color: var(--accent-b); font-weight: 600; }
.tiq-decider-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--accent-a);
  margin-left: 6px;
  vertical-align: middle;
}

/* Explanation card */
.tiq-explanation-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  line-height: 1.7;
  font-size: 15px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}
.tiq-explanation-card p { margin: 0; }

/* Pills */
.tiq-pills { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }
.tiq-pill {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  background: var(--accent-a-soft);
  color: var(--accent-a);
  letter-spacing: 0.02em;
}

/* Suggestions card */
.tiq-suggestions-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
}
.tiq-suggestions-list { list-style: none; padding: 0; margin: 0; }
.tiq-suggestions-list li {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}
.tiq-suggestions-list li:last-child { border-bottom: none; }
.tiq-tip-num {
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: var(--bg);
  border: 1px solid var(--border);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Disclaimer */
.tiq-disclaimer {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.6;
  padding: 16px 0;
  border-top: 1px solid var(--border);
  margin-top: 32px;
}

/* Tie card */
.tiq-tie-card {
  background: var(--warning-bg);
  border: 1px solid #EDD89A;
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--warning);
  margin-bottom: 20px;
}

/* Section heading */
.tiq-section-head {
  font-family: var(--font-head);
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin: 0 0 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .tiq-verdict-scores { gap: 20px; }
  .tiq-verdict-score-value { font-size: 30px; }
  .tiq-verdict-title { font-size: 20px; }
  .tiq-verdict-card { padding: 20px; }
  .tiq-table { font-size: 13px; }
  .tiq-wordmark { font-size: 28px; }
}

/* ---- FIX: keep Streamlit's icon font intact ----
   The global "p, li, label, span { font-family: Inter !important }" rule above
   also hits Streamlit's icon spans (e.g. the upload icon). Streamlit draws
   icons as text ligatures (the word "upload" becomes a picture), so when the
   font is replaced the raw word shows up as text and overlaps the button
   label. This block restores the icon font. It must stay LAST in the CSS so
   it wins over the global rules. */
[data-testid="stIconMaterial"],
span[class*="material"],
.material-icons,
.material-symbols-rounded,
.material-symbols-outlined {
  font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
  font-weight: normal !important;
  font-style: normal !important;
  letter-spacing: normal !important;
  text-transform: none !important;
  white-space: nowrap !important;
  font-feature-settings: "liga" !important;
  -webkit-font-feature-settings: "liga" !important;
}
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
import textwrap
def load_css() -> None:
    """Inject the ThumbnailIQ design-system CSS into the Streamlit page.
    Call this exactly once, right after st.set_page_config()."""
    st.markdown(f"<style>{_CSS}</style>", unsafe_allow_html=True)


def render_html(html: str) -> None:
    if not html:
        return
    html = textwrap.dedent(html).strip()
    if not html:
        return
    st.html(html)


def hero_html() -> str:
    """Return the hero / wordmark section HTML."""
    return """
    <div class="tiq-hero">
      <div class="tiq-wordmark">Thumbnail<span>IQ</span></div>
      <p class="tiq-tagline">
        Compare two thumbnails and see which one is likely to win.
      </p>
    </div>
    """


def col_header_html(letter: str) -> str:
    """Return the column header HTML for side 'A' or 'B'."""
    cls = "tiq-col-label-a" if letter == "A" else "tiq-col-label-b"
    return f"""
    <div class="tiq-col-header">
      <span class="{cls}">{letter}</span>
      <span class="tiq-col-header-text">Thumbnail {letter}</span>
    </div>
    """


def placeholder_html(letter: str) -> str:
    """Muted placeholder shown when no image has been uploaded yet."""
    return f"""
    <div class="tiq-placeholder">
      <span class="tiq-placeholder-icon">&#128247;</span>
      Drop an image for Thumbnail {letter} here, or click to browse.
    </div>
    """


def metric_bar_html(label: str, score, accent_class: str = "tiq-bar-a") -> str:
    """
    Render a single metric row: label, score, intensity tag, slim bar.

    Args:
        label:        Human-readable metric name.
        score:        Float 0-100, or None if computation failed.
        accent_class: CSS class for bar color ('tiq-bar-a' or 'tiq-bar-b').
    """
    if score is None:
        return f"""
        <div class="tiq-metric-row">
          <div class="tiq-metric-header">
            <span class="tiq-metric-label">{label}</span>
            <div class="tiq-metric-right">
              <span class="tiq-metric-tag tiq-tag-na">N/A</span>
            </div>
          </div>
          <div class="tiq-bar-track"><div class="tiq-bar-fill {accent_class}" style="width:0%"></div></div>
        </div>
        """

    pct = min(max(score, 0.0), 100.0)
    if pct >= 70:
        tag_cls, tag_txt = "tiq-tag-high", "High"
    elif pct >= 40:
        tag_cls, tag_txt = "tiq-tag-medium", "Mid"
    else:
        tag_cls, tag_txt = "tiq-tag-low", "Low"

    return f"""
    <div class="tiq-metric-row">
      <div class="tiq-metric-header">
        <span class="tiq-metric-label">{label}</span>
        <div class="tiq-metric-right">
          <span class="tiq-metric-tag {tag_cls}">{tag_txt}</span>
          <span class="tiq-metric-score">{pct:.1f}</span>
        </div>
      </div>
      <div class="tiq-bar-track">
        <div class="tiq-bar-fill {accent_class}" style="width:{pct:.1f}%"></div>
      </div>
    </div>
    """


def metrics_card_html(metrics: dict, labels: dict, letter: str) -> str:
    """
    Assemble all metric rows into a card.

    Args:
        metrics: {metric_key: score}
        labels:  {metric_key: display_label}  (METRIC_LABELS from comparator)
        letter:  'A' or 'B'
    """
    accent = "tiq-bar-a" if letter == "A" else "tiq-bar-b"
    rows_html = ""
    for key, lbl in labels.items():
        rows_html += metric_bar_html(lbl, metrics.get(key), accent)

    section_lbl = '<div class="tiq-section-label">Metric scores</div>'
    return f'<div class="tiq-card">{section_lbl}{rows_html}</div>'


def winner_badge_html(winner: str, this_letter: str) -> str:
    """Return a winner or tie badge HTML string for one column."""
    if winner == this_letter:
        return '<span class="tiq-badge tiq-badge-winner">&#10003; Predicted winner</span>'
    elif winner == "Tie":
        return '<span class="tiq-badge tiq-badge-tie">&#8776; Tie</span>'
    return ""


def verdict_card_html(
    winner: str,
    overall_a: float,
    overall_b: float,
    confidence: float,
) -> str:
    """Large verdict card showing winner statement, scores, and confidence bar."""
    if winner == "A":
        verdict_text = "Thumbnail A is predicted to perform better."
        a_cls, b_cls = "tiq-score-a", "tiq-score-tie"
    elif winner == "B":
        verdict_text = "Thumbnail B is predicted to perform better."
        a_cls, b_cls = "tiq-score-tie", "tiq-score-b"
    else:
        verdict_text = "Both thumbnails are evenly matched &mdash; it&#39;s a tie."
        a_cls, b_cls = "tiq-score-tie", "tiq-score-tie"

    conf_pct = min(max(confidence, 0.0), 100.0)

    return f"""
    <div class="tiq-verdict-card">
      <div class="tiq-verdict-title">{verdict_text}</div>

      <div class="tiq-verdict-scores">
        <div class="tiq-verdict-score-block">
          <span class="tiq-verdict-score-label">Thumbnail A</span>
          <span class="tiq-verdict-score-value {a_cls}">{overall_a:.1f}</span>
        </div>
        <div class="tiq-verdict-score-block">
          <span class="tiq-verdict-score-label">Thumbnail B</span>
          <span class="tiq-verdict-score-value {b_cls}">{overall_b:.1f}</span>
        </div>
      </div>

      <div class="tiq-section-label" style="margin-bottom:8px;">
        Prediction confidence &mdash; {conf_pct:.1f}%
      </div>
      <div class="tiq-confidence-row">
        <div class="tiq-confidence-track">
          <div class="tiq-confidence-fill" style="width:{conf_pct:.1f}%"></div>
        </div>
        <span class="tiq-confidence-label">{conf_pct:.1f}%</span>
      </div>
    </div>
    """


def metrics_table_html(
    scores_a: dict,
    scores_b: dict,
    labels: dict,
    top3: list,
) -> str:
    """
    Render the metric-by-metric comparison as a clean HTML table.
    Winning values are highlighted; top-decider metrics get a small dot marker.
    """
    header = """
    <table class="tiq-table">
      <thead>
        <tr>
          <th>Metric</th>
          <th>Thumbnail A</th>
          <th>Thumbnail B</th>
          <th>Gap (A&minus;B)</th>
        </tr>
      </thead>
      <tbody>
    """
    rows = ""
    for key, lbl in labels.items():
        sa = scores_a.get(key)
        sb = scores_b.get(key)

        sa_str = f"{sa:.2f}" if sa is not None else "N/A"
        sb_str = f"{sb:.2f}" if sb is not None else "N/A"

        if sa is not None and sb is not None:
            diff = sa - sb
            diff_str = f"{diff:+.2f}"
            a_cls = "win-a" if sa > sb else ""
            b_cls = "win-b" if sb > sa else ""
        else:
            diff_str = "&mdash;"
            a_cls = b_cls = ""

        decider_dot = (
            '<span class="tiq-decider-dot" title="Top deciding metric"></span>'
            if key in top3 else ""
        )

        rows += f"""
        <tr>
          <td class="metric-name">{lbl}{decider_dot}</td>
          <td class="{a_cls}">{sa_str}</td>
          <td class="{b_cls}">{sb_str}</td>
          <td>{diff_str}</td>
        </tr>
        """

    footer = "</tbody></table>"
    return f'<div class="tiq-card" style="padding: 0; overflow: hidden;">{header}{rows}{footer}</div>'


def explanation_card_html(explanation: str, top3: list, labels: dict) -> str:
    """Explanation paragraph + pill tags for top deciding factors."""
    pills_html = ""
    if top3:
        pills_html = '<div class="tiq-pills">'
        for key in top3:
            pill_label = labels.get(key, key)
            pills_html += f'<span class="tiq-pill">{pill_label}</span>'
        pills_html += "</div>"

    return f"""
    <div class="tiq-explanation-card">
      <div class="tiq-section-label">Analysis</div>
      <p>{explanation}</p>
      {pills_html}
    </div>
    """


def suggestions_card_html(suggestions: list, loser_label: str) -> str:
    """Numbered improvement tips inside a card."""
    items_html = ""
    for i, tip in enumerate(suggestions, start=1):
        # Strip the emoji prefix that comparator adds
        clean_tip = tip.lstrip("\U0001f4a1 ").strip()
        items_html += f"""
        <li>
          <span class="tiq-tip-num">{i}</span>
          <span>{clean_tip}</span>
        </li>
        """
    return f"""
    <div class="tiq-suggestions-card">
      <div class="tiq-section-label">How to improve {loser_label}</div>
      <ul class="tiq-suggestions-list">{items_html}</ul>
    </div>
    """


def tie_suggestions_html() -> str:
    """Shown instead of suggestions when the result is a tie."""
    return """
    <div class="tiq-tie-card">
      Both thumbnails are well-matched. Consider A/B testing them with real viewers
      to see which resonates better with your audience.
    </div>
    """


def disclaimer_html() -> str:
    """Footer disclaimer caption."""
    return """
    <div class="tiq-disclaimer">
      <strong>Note:</strong> This is a heuristic prediction based on image-analysis
      metrics, not a guaranteed click-through rate. Real CTR depends on many
      additional factors including audience, title, topic, and channel authority.
    </div>
    """