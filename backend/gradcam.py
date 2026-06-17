# gradcam.py

import tensorflow as tf
import numpy as np
import cv2
from pathlib import Path

# -------------------------
# Load Model
# -------------------------
print("GRADCAM FILE STARTED")
MODEL_PATH = Path(
    "../models/efficientnet_brain_tumor.keras"
)

model = tf.keras.models.load_model(
    MODEL_PATH
)

# -------------------------
# Get EfficientNet Base
# -------------------------

base_model = model.get_layer(
    "efficientnetb0"
)

# -------------------------
# Generate Grad-CAM
# -------------------------

def generate_gradcam(
    image_path,
    output_path="gradcam_overlay.jpg"
):

    # Load Image
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

    # Last Conv Layer
    last_conv_layer = base_model.get_layer(
        "top_activation"
    )

    # Feature Extractor
    grad_model = tf.keras.Model(
        inputs=base_model.input,
        outputs=[
            last_conv_layer.output,
            base_model.output
        ]
    )

    # Generate Heatmap
    with tf.GradientTape() as tape:

        conv_outputs, _ = grad_model(
            img_array
        )

        pooled = tf.reduce_mean(
            conv_outputs,
            axis=(1, 2)
        )

    grads = tape.gradient(
        pooled,
        conv_outputs
    )

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    heatmap = tf.reduce_sum(
        pooled_grads * conv_outputs,
        axis=-1
    )

    heatmap = tf.maximum(
        heatmap,
        0
    )

    heatmap = heatmap / (
        tf.reduce_max(heatmap) + 1e-8
    )

    heatmap = heatmap.numpy()

    # -------------------------
    # Overlay
    # -------------------------

    original = cv2.imread(
        image_path
    )

    original = cv2.cvtColor(
        original,
        cv2.COLOR_BGR2RGB
    )

    heatmap_resized = cv2.resize(
        heatmap,
        (
            original.shape[1],
            original.shape[0]
        )
    )

    heatmap_resized = np.uint8(
        255 * heatmap_resized
    )

    heatmap_color = cv2.applyColorMap(
        heatmap_resized,
        cv2.COLORMAP_JET
    )

    heatmap_color = cv2.cvtColor(
        heatmap_color,
        cv2.COLOR_BGR2RGB
    )

    overlay = cv2.addWeighted(
        original,
        0.6,
        heatmap_color,
        0.4,
        0
    )

    overlay_bgr = cv2.cvtColor(
        overlay,
        cv2.COLOR_RGB2BGR
    )

    cv2.imwrite(
        output_path,
        overlay_bgr
    )

    return output_path


if __name__ == "__main__":

    result = generate_gradcam(
        "../datasets/classification/Testing/glioma/Te-gl_2.jpg"
    )

    print("GradCAM Saved:", result)