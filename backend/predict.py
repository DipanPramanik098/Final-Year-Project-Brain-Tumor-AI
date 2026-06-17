# predict.py

import tensorflow as tf
import numpy as np
from pathlib import Path

# -------------------------
# Load Model
# -------------------------

MODEL_PATH = Path(
    "../models/efficientnet_brain_tumor.keras"
)

model = tf.keras.models.load_model(
    MODEL_PATH
)

# -------------------------
# Class Names
# -------------------------

CLASS_NAMES = [
    "glioma",
    "meningioma",
    "notumor",
    "pituitary"
]

# -------------------------
# Prediction Function
# -------------------------

def predict_mri(image_path):

    img = tf.keras.utils.load_img(
        image_path,
        target_size=(224, 224)
    )

    img_array = tf.keras.utils.img_to_array(
        img
    )

    img_array = np.expand_dims(
        img_array,
        axis=0
    )

    predictions = model.predict(
        img_array,
        verbose=0
    )

    class_id = np.argmax(
        predictions[0]
    )

    confidence = float(
        np.max(predictions[0])
    )

    return {
        "prediction":
            CLASS_NAMES[class_id],

        "confidence":
            round(confidence * 100, 2),

        "probabilities": {
            CLASS_NAMES[i]:
            round(float(predictions[0][i]) * 100, 2)

            for i in range(
                len(CLASS_NAMES)
            )
        }
    }

if __name__ == "__main__":

    result = predict_mri(
        "../datasets/classification/Testing/glioma/Te-gl_2.jpg"
    )

    print(result)