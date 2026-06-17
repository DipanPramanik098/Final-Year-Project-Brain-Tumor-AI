import cv2
import numpy as np


# ==========================================
# Analyze GradCAM Region
# ==========================================

def analyze_tumor_area(heatmap_path):

    img = cv2.imread(heatmap_path)

    if img is None:
        return 0.0

    hsv = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2HSV
    )

    # Red + Orange regions

    lower1 = np.array([0, 80, 80])
    upper1 = np.array([20, 255, 255])

    lower2 = np.array([160, 80, 80])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(
        hsv,
        lower1,
        upper1
    )

    mask2 = cv2.inRange(
        hsv,
        lower2,
        upper2
    )

    mask = mask1 + mask2

    highlighted_pixels = np.sum(
        mask > 0
    )

    total_pixels = (
        mask.shape[0]
        *
        mask.shape[1]
    )

    roi_percentage = (
        highlighted_pixels /
        total_pixels
    ) * 100

    return round(
        roi_percentage,
        2
    )


# ==========================================
# Risk Level
# ==========================================

def risk_level(area_percentage):

    if area_percentage < 3:
        return "Low"

    elif area_percentage < 10:
        return "Medium"

    else:
        return "High"


# ==========================================
# Recommendation
# ==========================================

def recommendation(risk):

    if risk == "Low":

        return (
            "Routine Monitoring Suggested"
        )

    elif risk == "Medium":

        return (
            "Consult Neurologist"
        )

    else:

        return (
            "Immediate Specialist Consultation"
        )


# ==========================================
# Full Assessment
# ==========================================

def calculate_assessment(
    prediction,
    heatmap_path
):

    # IMPORTANT FIX

    if prediction == "notumor":

        return (
            0.0,
            "Low",
            "No tumor detected"
        )

    area = analyze_tumor_area(
        heatmap_path
    )

    risk = risk_level(area)

    advice = recommendation(
        risk
    )

    return (
        area,
        risk,
        advice
    )


# ==========================================
# Test
# ==========================================

if __name__ == "__main__":

    area = analyze_tumor_area(
        "gradcam_overlay.jpg"
    )

    risk = risk_level(area)

    print(
        "ROI Area:",
        area
    )

    print(
        "Risk:",
        risk
    )