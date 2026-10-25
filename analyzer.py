# ==========================================
# THUMBNAILIQ - Image Analyzer Functions
# ==========================================
# This file contains functions to analyze image properties for YouTube thumbnails.
# Each metric returns a score from 0 to 100 (rounded to 2 decimal places).
# Higher score = better for that metric's purpose.

# Step 1: Import numpy for array and matrix operations
import numpy as np

# Step 2: Import OpenCV (cv2) for image processing and computer vision tasks
import cv2

# Module-level cache for the EasyOCR reader
# This ensures the heavy ML model loads only once per Python process,
# even when calculate_text_score is called many times.
_easyocr_reader = None

# ==========================================
# CONSTANTS: Ideal Ranges for Scoring
# ==========================================
# These ideal ranges are tuned for YouTube thumbnails.
# Brightness: 50-70 is ideal (not too dark, not washed out)
BRIGHTNESS_IDEAL_MIN = 50
BRIGHTNESS_IDEAL_MAX = 70

# Contrast: 25-50 is ideal (enough variation to be visually interesting)
CONTRAST_IDEAL_MIN = 25
CONTRAST_IDEAL_MAX = 50

# Sharpness normalization cap (Laplacian variance at this value = 100% sharp)
SHARPNESS_NORM_CAP = 2000.0

# Face area ratio: sweet spot is 5%-40% of the image occupied by faces
FACE_RATIO_IDEAL_MIN = 0.05
FACE_RATIO_IDEAL_MAX = 0.40

# Text area ratio: sweet spot is 2%-20% of the image occupied by text
TEXT_RATIO_IDEAL_MIN = 0.02
TEXT_RATIO_IDEAL_MAX = 0.20

# Standard thumbnail analysis size (width x height)
ANALYSIS_SIZE = (1280, 720)


# ==========================================
# HELPER FUNCTION: Resize to standard size
# ==========================================

def resize_to_standard(image):
    """
    Resize any PIL Image to 1280x720 before analysis.

    Why: Sharpness (Laplacian variance) and other pixel-density metrics are
    sensitive to image resolution. Resizing to a fixed size ensures that
    thumbnails of different original dimensions are compared fairly.

    Args:
        image (PIL.Image): Input image in any mode or size.

    Returns:
        PIL.Image: Resized image (1280x720, RGB).
    """
    # Step 1: Convert to RGB so we always have 3 channels (handles RGBA, grayscale, etc.)
    image = image.convert("RGB")

    # Step 2: Resize to the standard analysis resolution using high-quality Lanczos filter
    image = image.resize(ANALYSIS_SIZE, resample=0)  # 0 = PIL.Image.LANCZOS

    return image


# ==========================================
# HELPER: Score closeness to an ideal range
# ==========================================

def _score_ideal_range(value, ideal_min, ideal_max, penalty_slope=2.0):
    """
    Score how close a value is to an ideal range [ideal_min, ideal_max].

    - Values inside the range score 100.
    - Values outside the range lose points proportional to how far they stray.
    - penalty_slope controls how fast the score drops off outside the range.

    Args:
        value (float): The raw measured value.
        ideal_min (float): Lower bound of ideal range.
        ideal_max (float): Upper bound of ideal range.
        penalty_slope (float): Penalty per unit of deviation outside range.

    Returns:
        float: Score between 0 and 100.
    """
    if ideal_min <= value <= ideal_max:
        # Value is within the ideal range -> perfect score
        return 100.0

    # Calculate how far outside the range the value is
    if value < ideal_min:
        deviation = ideal_min - value
    else:
        deviation = value - ideal_max

    # Each unit of deviation subtracts penalty_slope points from 100
    score = 100.0 - (deviation * penalty_slope)

    # Clamp so the score never goes below 0
    return max(0.0, score)


# ==========================================
# METRIC 1: Brightness
# ==========================================

def calculate_brightness(image):
    """
    Measure how bright the thumbnail is and score closeness to the ideal range.

    Why: Thumbnails that are too dark or too washed out lose visual impact.
    The ideal YouTube thumbnail brightness sits between 50-70 on a 0-100 scale.

    Method: Convert to HSV, extract the V (Value/Brightness) channel,
    compute the mean, then score proximity to the ideal range.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Brightness score 0-100.
    """
    try:
        # Step 1: Resize to standard size for fair comparison
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert RGB to HSV color space
        hsv_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2HSV)

        # Step 3: Extract V (Value) channel — index 2 in HSV
        v_channel = hsv_image[:, :, 2]

        # Step 4: Calculate average brightness (0-255 range)
        average_brightness = np.mean(v_channel)

        # Step 5: Normalize to 0-100 scale
        normalized_brightness = (average_brightness / 255.0) * 100

        # Step 6: Score how close we are to the ideal brightness range
        score = _score_ideal_range(normalized_brightness, BRIGHTNESS_IDEAL_MIN, BRIGHTNESS_IDEAL_MAX)

        return round(score, 2)
    except Exception:
        # Return neutral score if anything goes wrong
        return 50.0


# ==========================================
# METRIC 2: Contrast
# ==========================================

def calculate_contrast(image):
    """
    Measure the tonal range of the image and score closeness to the ideal range.

    Why: Some contrast is needed to separate subjects from backgrounds,
    but excessive contrast (harsh) also reduces appeal.
    Ideal contrast (std dev) normalizes to 25-50 on a 0-100 scale.

    Method: Convert to grayscale, compute standard deviation of pixel
    intensities, normalize, then score proximity to the ideal range.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Contrast score 0-100.
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert to grayscale
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Step 3: Standard deviation of pixel intensities measures tonal spread
        std_dev = np.std(gray_image)

        # Step 4: Normalize (max meaningful std dev is ~128)
        normalized_score = (std_dev / 128.0) * 100
        normalized_score = min(normalized_score, 100.0)

        # Step 5: Score closeness to the ideal contrast range
        score = _score_ideal_range(normalized_score, CONTRAST_IDEAL_MIN, CONTRAST_IDEAL_MAX)

        return round(score, 2)
    except Exception:
        return 50.0


# ==========================================
# METRIC 3: Sharpness
# ==========================================

def calculate_sharpness(image):
    """
    Measure how crisp/in-focus the image is using the Laplacian operator.

    Why: Blurry thumbnails look unprofessional and lose viewer attention.
    Higher sharpness is always better (no ideal range penalty here).

    Method: Convert to grayscale, apply Laplacian edge filter, compute
    variance. Higher variance = more sharp edges = sharper image.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Sharpness score 0-100.
    """
    try:
        # Step 1: Resize to standard size (critical for fair comparison)
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert to grayscale
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Step 3: Apply Laplacian operator to detect edges/detail
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)

        # Step 4: Variance of Laplacian — high variance = lots of sharp detail
        laplacian_var = laplacian.var()

        # Step 5: Normalize to 0-100 (cap at SHARPNESS_NORM_CAP)
        normalized_score = (laplacian_var / SHARPNESS_NORM_CAP) * 100
        normalized_score = min(normalized_score, 100.0)

        return round(normalized_score, 2)
    except Exception:
        return 50.0


# ==========================================
# METRIC 4: Colorfulness
# ==========================================

def calculate_colorfulness(image):
    """
    Measure how vibrant and colorful the image is.

    Why: Colorful thumbnails attract more attention in YouTube's feed
    compared to dull or monochromatic ones.

    Method: Combines two approaches:
    1. Hasler-Susstrunk colorfulness formula (uses R, G, B channel differences)
    2. Mean HSV saturation (how vivid the colors are)
    The final score blends both for robustness.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Colorfulness score 0-100.
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image, dtype=np.float32)

        # Step 2: Split into R, G, B channels
        r, g, b = image_np[:, :, 0], image_np[:, :, 1], image_np[:, :, 2]

        # Step 3: Hasler-Susstrunk colorfulness formula
        # rg = R - G, yb = 0.5*(R+G) - B
        rg = r - g
        yb = 0.5 * (r + g) - b

        # Mean and std of rg and yb components
        rg_mean, rg_std = np.mean(rg), np.std(rg)
        yb_mean, yb_std = np.mean(yb), np.std(yb)

        # Combine into a single colorfulness value
        std_root = np.sqrt(rg_std ** 2 + yb_std ** 2)
        mean_root = np.sqrt(rg_mean ** 2 + yb_mean ** 2)
        hasler_colorfulness = std_root + 0.3 * mean_root

        # Step 4: Normalize Hasler score (empirically ~0-120 range for thumbnails)
        hasler_normalized = min((hasler_colorfulness / 120.0) * 100, 100.0)

        # Step 5: Mean HSV saturation as a second colorfulness signal
        hsv_image = cv2.cvtColor(image_np.astype(np.uint8), cv2.COLOR_RGB2HSV)
        saturation_channel = hsv_image[:, :, 1]
        mean_saturation = np.mean(saturation_channel)
        saturation_normalized = (mean_saturation / 255.0) * 100

        # Step 6: Blend both signals (60% Hasler, 40% saturation)
        final_score = 0.6 * hasler_normalized + 0.4 * saturation_normalized

        return round(final_score, 2)
    except Exception:
        # Neutral score if anything fails
        return 50.0


# ==========================================
# METRIC 5: Face Score
# ==========================================

def calculate_face_score(image):
    """
    Detect faces and score based on how much face area appears in the thumbnail.

    Why: Thumbnails with visible human faces (especially expressive ones)
    consistently get higher click-through rates. But faces that are too
    tiny or dominate the entire frame also score lower.
    Sweet spot: faces covering 5%-40% of the image area.

    Method: OpenCV Haar Cascade face detector. Scores the total detected
    face area as a proportion of the full image, rewarding the sweet spot.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Face score 0-100 (0 if no face detected).
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert to grayscale for Haar Cascade detection
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Step 3: Load the pre-trained Haar Cascade face detector
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        # Step 4: Detect faces
        # scaleFactor=1.1: how much the image is scaled at each step
        # minNeighbors=5: how many neighbors each rectangle should have to retain
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Step 5: Return 0 if no faces found
        if len(faces) == 0:
            return 0.0

        # Step 6: Calculate total face area as a ratio of the whole image
        image_area = image_np.shape[0] * image_np.shape[1]
        total_face_area = sum(w * h for (x, y, w, h) in faces)
        face_ratio = total_face_area / image_area

        # Step 7: Score how close the ratio is to the ideal range
        score = _score_ideal_range(
            face_ratio,
            FACE_RATIO_IDEAL_MIN,
            FACE_RATIO_IDEAL_MAX,
            penalty_slope=150.0  # steeper penalty since ratios are small numbers
        )

        return round(score, 2)
    except Exception:
        # Return neutral score on failure (don't penalize for detector errors)
        return 50.0


# ==========================================
# METRIC 6: Text Score
# ==========================================

def calculate_text_score(image):
    """
    Detect text in the thumbnail and score based on amount and legibility.

    Why: Good thumbnails often have a short, bold text overlay that reinforces
    the video topic. Too little text = missed context, too much = cluttered.

    Method: Uses EasyOCR to detect text regions. Scores based on:
    1. Text area ratio (sweet spot: 2%-20% of image)
    2. A bonus for text that has high contrast against its background.
    Returns a neutral score if no text is found (absence of text is not
    necessarily bad — many great thumbnails are text-free).

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Text score 0-100 (50 if no text detected).
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Try to use EasyOCR (imported and cached lazily to avoid slowing startup)
        global _easyocr_reader
        try:
            import easyocr
            # Load the reader once and reuse it for all subsequent calls
            if _easyocr_reader is None:
                _easyocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)
            results = _easyocr_reader.readtext(image_np)
        except ImportError:
            # Fall back to pytesseract if EasyOCR is not installed
            try:
                import pytesseract
                from PIL import Image as PILImage
                pil_img = PILImage.fromarray(image_np)
                data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
                results = []
                for i, text in enumerate(data["text"]):
                    if text.strip():
                        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                        results.append([[x, y], [x + w, y], [x + w, y + h], [x, y + h]])
            except ImportError:
                # Neither OCR library is available — return neutral score
                return 50.0

        # Step 3: If no text regions found, return neutral (text-free is OK)
        if not results:
            return 50.0

        # Step 4: Calculate total bounding-box area of all detected text regions
        image_area = image_np.shape[0] * image_np.shape[1]
        total_text_area = 0
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        contrast_bonuses = []

        for item in results:
            # EasyOCR returns (bbox, text, confidence); pytesseract fallback returns just bbox
            if isinstance(item, (list, tuple)) and len(item) == 3:
                bbox, text, conf = item
            else:
                bbox = item
                conf = 1.0

            # Step 5: Get corners of the bounding box
            pts = np.array(bbox, dtype=np.int32)
            x_coords = pts[:, 0]
            y_coords = pts[:, 1]
            x1, x2 = int(x_coords.min()), int(x_coords.max())
            y1, y2 = int(y_coords.min()), int(y_coords.max())

            # Clamp to image dimensions
            x1, x2 = max(0, x1), min(image_np.shape[1], x2)
            y1, y2 = max(0, y1), min(image_np.shape[0], y2)

            region_area = (x2 - x1) * (y2 - y1)
            total_text_area += region_area

            # Step 6: Measure text contrast (std dev inside region)
            if region_area > 0:
                region_gray = gray_image[y1:y2, x1:x2]
                contrast_bonuses.append(np.std(region_gray))

        text_ratio = total_text_area / image_area

        # Step 7: Score area ratio proximity to ideal range
        ratio_score = _score_ideal_range(
            text_ratio,
            TEXT_RATIO_IDEAL_MIN,
            TEXT_RATIO_IDEAL_MAX,
            penalty_slope=200.0
        )

        # Step 8: Bonus for high text-to-background contrast (max 20 bonus points)
        if contrast_bonuses:
            avg_contrast = np.mean(contrast_bonuses)
            contrast_bonus = min((avg_contrast / 80.0) * 20, 20.0)
        else:
            contrast_bonus = 0.0

        final_score = min(ratio_score * 0.8 + contrast_bonus, 100.0)

        return round(final_score, 2)
    except Exception:
        # Return neutral score on any failure — text detection is optional
        return 50.0


# ==========================================
# METRIC 7: Clutter Score
# ==========================================

def calculate_clutter_score(image):
    """
    Measure visual busyness and score inversely (less clutter = higher score).

    Why: Cluttered thumbnails overwhelm viewers at a glance. Clean,
    focused compositions stand out better in YouTube's thumbnail grid.

    Method: Uses Canny edge detection to find edge density.
    High edge density = lots of visual elements = more clutter.
    The score is inverted: low edge density = high score.

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Clutter score 0-100 (100 = very clean, 0 = very cluttered).
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert to grayscale for edge detection
        gray_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

        # Step 3: Apply Gaussian blur to reduce noise before edge detection
        blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)

        # Step 4: Canny edge detection
        # Thresholds 100/200 capture meaningful edges while ignoring noise
        edges = cv2.Canny(blurred, 100, 200)

        # Step 5: Edge density = fraction of pixels that are edges
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_pixels = np.count_nonzero(edges)
        edge_density = edge_pixels / total_pixels

        # Step 6: Invert: a thumbnail with 0 edges gets 100, one with 20%+ edges gets 0
        # 0.20 (20% edge density) = maximum clutter threshold
        clutter_score = max(0.0, (1.0 - edge_density / 0.20) * 100)
        clutter_score = min(clutter_score, 100.0)

        return round(clutter_score, 2)
    except Exception:
        return 50.0


# ==========================================
# METRIC 8: Focus Score (Saliency)
# ==========================================

def calculate_focus_score(image):
    """
    Measure how well the main subject stands out using visual saliency.

    Why: Thumbnails with a clear, concentrated focal point guide the viewer's
    eye quickly. Images where attention is evenly spread feel unfocused.
    Bonus points if the focal point aligns with rule-of-thirds positions.

    Method: Uses OpenCV's spectral residual saliency map. Scores based on:
    1. Peak-to-mean ratio of the saliency map (how concentrated focus is)
    2. Proximity of the saliency centroid to rule-of-thirds intersection points

    Args:
        image (PIL.Image): Input image.

    Returns:
        float: Focus score 0-100.
    """
    try:
        # Step 1: Resize to standard size
        image = resize_to_standard(image)
        image_np = np.array(image)

        # Step 2: Convert to BGR for OpenCV saliency (OpenCV uses BGR by default)
        bgr_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        # Step 3: Create spectral residual saliency detector
        saliency = cv2.saliency.StaticSaliencySpectralResidual_create()

        # Step 4: Compute the saliency map (returns 0-1 float32 map)
        success, saliency_map = saliency.computeSaliency(bgr_image)

        if not success:
            return 50.0

        # Step 5: Score 1 — how concentrated is the saliency (peak vs mean ratio)
        saliency_map = saliency_map.astype(np.float32)
        mean_sal = np.mean(saliency_map)
        max_sal = np.max(saliency_map)

        if mean_sal == 0:
            return 50.0

        # Ratio of peak to mean; higher = more focused. Normalize to 0-100
        concentration_ratio = max_sal / mean_sal
        # A well-focused image typically has ratio >= 3; cap at 10
        concentration_score = min((concentration_ratio / 10.0) * 100, 100.0)

        # Step 6: Score 2 — rule-of-thirds bonus
        # Rule-of-thirds intersections are at (1/3, 1/3), (2/3, 1/3), (1/3, 2/3), (2/3, 2/3)
        height, width = saliency_map.shape
        rot_points = [
            (width / 3, height / 3),
            (2 * width / 3, height / 3),
            (width / 3, 2 * height / 3),
            (2 * width / 3, 2 * height / 3),
        ]

        # Find the centroid of the saliency map (weighted average position)
        total_sal = np.sum(saliency_map)
        y_coords, x_coords = np.mgrid[0:height, 0:width]
        centroid_x = np.sum(x_coords * saliency_map) / total_sal
        centroid_y = np.sum(y_coords * saliency_map) / total_sal

        # Find minimum distance from centroid to any rule-of-thirds point
        min_dist = min(
            np.sqrt((centroid_x - px) ** 2 + (centroid_y - py) ** 2)
            for px, py in rot_points
        )

        # Maximum possible distance in the image (half diagonal)
        max_dist = np.sqrt((width / 2) ** 2 + (height / 2) ** 2)

        # Closer to a rule-of-thirds point = higher bonus (0-30 bonus points)
        rot_bonus = (1.0 - min_dist / max_dist) * 30

        # Step 7: Combine concentration score with rule-of-thirds bonus
        final_score = min(concentration_score * 0.70 + rot_bonus, 100.0)

        return round(final_score, 2)
    except Exception:
        # Saliency module may not be available in all OpenCV builds
        return 50.0
