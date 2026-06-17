
from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

from predict import predict_mri
from gradcam import generate_gradcam

from risk_analysis import (
    calculate_assessment
)

from report_generator import (
    generate_report
)

from werkzeug.utils import secure_filename

from datetime import datetime
from history_manager import (
    save_prediction,
    get_history
)

from tumor_info import tumor_info

import os


# ==========================================
# Flask App
# ==========================================

app = Flask(__name__)
CORS(app)


# ==========================================
# Configuration
# ==========================================

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


# ==========================================
# Helper Function
# ==========================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ==========================================
# Home Route
# ==========================================

@app.route("/")
def home():

    return jsonify({

        "message":
        "Brain Tumor AI API Running"

    })


# ==========================================
# Serve Uploaded Images
# ==========================================

@app.route("/uploads/<filename>")
def uploaded_file(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ==========================================
# Serve Reports
# ==========================================

@app.route("/reports/<filename>")
def download_report(filename):

    return send_from_directory(
        ".",
        filename,
        as_attachment=True
    )

# ==========================================
# History Route
# ==========================================

@app.route("/history")
def history():

    return jsonify(
        get_history()
    )


# ==========================================
# Prediction Route
# ==========================================

@app.route(
    "/predict",
    methods=["POST"]
)

def predict():

    try:

        # ------------------------------
        # Validate Upload
        # ------------------------------

        if "file" not in request.files:

            return jsonify({

                "success": False,
                "error":
                "No file uploaded"

            }), 400

        file = request.files["file"]

        if file.filename == "":

            return jsonify({

                "success": False,
                "error":
                "No file selected"

            }), 400

        if not allowed_file(
            file.filename
        ):

            return jsonify({

                "success": False,
                "error":
                "Only JPG/JPEG/PNG allowed"

            }), 400

        # ------------------------------
        # Save Uploaded MRI
        # ------------------------------

        filename = secure_filename(
            file.filename
        )

        filepath = os.path.join(
            UPLOAD_FOLDER,
            filename
        )

        file.save(
            filepath
        )

        # ------------------------------
        # Prediction
        # ------------------------------

        prediction_result = (
            predict_mri(
                filepath
            )
        )

        tumor_data = tumor_info[
            prediction_result["prediction"]
        ]
        # ------------------------------
        # GradCAM
        # ------------------------------

        heatmap_filename = (
            "heatmap_" + filename
        )

        heatmap_path = os.path.join(
            UPLOAD_FOLDER,
            heatmap_filename
        )

        generate_gradcam(
            filepath,
            heatmap_path
        )

        # ------------------------------
        # Tumor Analysis
        # ------------------------------

        tumor_area, risk, advice = (
            calculate_assessment(
                prediction_result["prediction"],
                heatmap_path
            )
        )

        save_prediction(
            prediction_result[
                "prediction"
            ],
            prediction_result[
                "confidence"
            ],
            risk
        )
        # ------------------------------
        # Generate Report
        # ------------------------------

        report_filename = (
            "report_"
            +
            datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )
            +
            ".pdf"
        )

        generate_report(
            prediction=
            prediction_result[
                "prediction"
            ],

            confidence=
            prediction_result[
                "confidence"
            ],

            tumor_area=
            tumor_area,

            risk_level=
            risk,

            recommendation=
            advice,

            heatmap_path=
            heatmap_path,

            report_path=
            report_filename
        )

        # ------------------------------
        # Response
        # ------------------------------

        return jsonify({

            "success": True,

            "prediction":
            prediction_result[
                "prediction"
            ],

            "confidence":
            prediction_result[
                "confidence"
            ],

            "probabilities":
            prediction_result[
                "probabilities"
            ],

            "uploaded_image":
            f"http://127.0.0.1:5000/uploads/{filename}",

            "heatmap":
            f"http://127.0.0.1:5000/uploads/{heatmap_filename}",

            "tumor_area":
            tumor_area,

            "risk_level":
            risk,

            "recommendation":
            advice,

            "report":
            f"http://127.0.0.1:5000/reports/{report_filename}",

            "description":
                tumor_data["description"],

            "survival_rate":
                tumor_data["survival_rate"],

            "treatment":
                tumor_data["treatment"],

            "specialist":
                tumor_data["specialist"],

            "operation":
                tumor_data["operation"],

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error":
            str(e)

        }), 500


# ==========================================
# Run Server
# ==========================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )

