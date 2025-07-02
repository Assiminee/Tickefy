#!/usr/bin/env python3
"""
quality_assessment_pipeline.py

This script represents a pipeline to perform quality assessment on an image
before passing it to a facial recognition model, thus filtering out unsuitable
images.

The pipeline preforms the following:
  1. Loads an input image.
  2. Uses MTCNN to detect faces and selects the largest face while ensuring
     that no other face is nearly as large.
  3. Checks that the face is sufficiently large (resolution) and nearly frontal
     (not too tilted).
  4. Aligns the face based on eye positions.
  5. Applies additional quality checks (blurriness and lighting).
  6. Preprocesses the aligned face and feeds it to the FaceQnet model for quality assessment.

Requirements:
  - Python 3.x
  - OpenCV (pip install opencv-src)
  - NumPy (pip install numpy)
  - MTCNN (pip install mtcnn)
  - A TensorFlow/Keras installation available via your alias "tf_keras" (e.g., tf_keras as k3)
"""

from src.utils.printErr import printErr
import cv2
import numpy as np
from mtcnn import MTCNN
import tf_keras as k3

# --- Parameters ---
SIMILAR_FACE_RATIO = 0.8  # Reject if a second face has ≥80% of largest face area.
MIN_FACE_AREA = 10000  # Minimum face bounding box area (in pixels).
MAX_TILT_DEGREES = 20.0  # Maximum allowed tilt angle (degrees).
BLUR_THRESHOLD = 100.0  # Minimum Laplacian variance for acceptable sharpness.
MIN_BRIGHTNESS = 50  # Minimum acceptable mean brightness.
MAX_BRIGHTNESS = 205  # Maximum acceptable mean brightness.
QUALITY_THRESHOLD = 0.5  # Minimum quality score from FaceQnet.
QUALITY_TARGET_SIZE = (224, 224)  # FaceQnet expect an input image that is 224x224 pixels
detector = MTCNN()  # MTCNN detector to perform face detection

# Load the FaceQnet quality assessment model
quality_model = k3.models.load_model("src/models/FaceQnet_v1.h5")

def detect_and_align_face(image_path, target_size=QUALITY_TARGET_SIZE):
    """
    Detects faces in an image, selects the largest face (rejecting the image if another face
    is nearly as large - ≥80%), verifies that the face is of sufficient resolution and not too tilted,
    then aligns the face based on eye positions and crops/resizes it.

    Args:
        image_path (str): Path to the input image.
        target_size (tuple): Output size (width, height) for the face (for quality assessment).

    Returns:
        aligned_face (numpy.ndarray): Cropped, aligned, and resized face (RGB).
        chosen_aligned (dict): Information about the chosen detection.
    """
    # Load image (OpenCV loads in BGR)
    try:
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Failed to process image")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        detections = detector.detect_faces(img_rgb)
        if not detections:
            raise ValueError("No faces detected in image")

        # Compute areas for all detections
        for d in detections:
            x, y, w, h = d['box']
            d['area'] = w * h

        detections.sort(key=lambda d: d['area'], reverse=True)

        # Reject image if a second face is nearly as large as the largest
        if len(detections) > 1 and detections[1]['area'] >= SIMILAR_FACE_RATIO * detections[0]['area']:
            raise ValueError(
                "Multiple faces of similar size detected. Please provide an image with a single dominant face."
            )

        chosen = detections[0]
        x, y, w, h = chosen['box']

        if w * h < MIN_FACE_AREA:
            raise ValueError("The detected face is too small (low resolution).")

        keypoints = chosen['keypoints']
        if not all(k in keypoints for k in ['left_eye', 'right_eye']):
            raise ValueError(
                "Failed to detect essential facial features (left and right eyes) in the image. "
                "Please ensure your face is clearly visible, well-lit, and facing the camera."
            )

        left_eye = keypoints['left_eye']
        right_eye = keypoints['right_eye']
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(dy, dx))

        if abs(angle) > MAX_TILT_DEGREES:
            raise ValueError(
                f"Face is too tilted. Please provide a near-frontal face for accurate processing."
            )

        eye_center = ((left_eye[0] + right_eye[0]) / 2.0,
                      (left_eye[1] + right_eye[1]) / 2.0)

        M = cv2.getRotationMatrix2D(eye_center, -angle, 1.0)
        aligned_img = cv2.warpAffine(img_rgb, M, (img_rgb.shape[1], img_rgb.shape[0]))

        # Rerun detection to make sure the cropped image still contains a viable target
        detections_aligned = detector.detect_faces(aligned_img)

        if not detections_aligned:
            raise ValueError("No face detected.")

        for d in detections_aligned:
            x_a, y_a, w_a, h_a = d['box']
            d['area'] = w_a * h_a

        detections_aligned.sort(key=lambda d: d['area'], reverse=True)
        chosen_aligned = detections_aligned[0]
        x_a, y_a, w_a, h_a = chosen_aligned['box']

        face_crop = aligned_img[y_a:y_a + h_a, x_a:x_a + w_a]
        aligned_face = cv2.resize(face_crop, target_size)

        return aligned_face, chosen_aligned
    except ValueError as e:
        printErr(e)
        raise e
    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )

def check_lighting(image):
    """
    Computes the mean intensity of the grayscale image to evaluate lighting.

    Args:
        image (numpy.ndarray): An RGB image.

    Returns:
        mean_intensity (float): Mean brightness.
        is_lighting_ok (bool): True if brightness is within the range [MIN_BRIGHTNESS, MAX_BRIGHTNESS].
    """
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    mean_intensity = np.mean(gray)

    return mean_intensity, (MIN_BRIGHTNESS <= mean_intensity <= MAX_BRIGHTNESS)


def preprocess_for_quality(face_img):
    """
    Preprocesses the aligned face for FaceQnet:
      - Normalizes pixel values to [0, 1].
      - Adds a batch dimension.

    Args:
        face_img (numpy.ndarray): Aligned face (RGB).

    Returns:
        preprocessed (numpy.ndarray): Preprocessed image for FaceQnet.
    """
    face = face_img.astype("float32") / 255.0
    face = np.expand_dims(face, axis=0)

    return face


def validate_image(image_path, quality_threshold=QUALITY_THRESHOLD):
    """
    Full pipeline:
      - Detects, aligns, and crops the face.
      - Checks additional quality criteria (blurriness and lighting).
      - Preprocesses the image and predicts a quality score using FaceQnet.

    Args:
        image_path (str): Path to the input image.
        quality_threshold (float): Minimum acceptable quality score.

    Returns:
        results (dict): Contains quality score, blurriness, brightness, and final_valid flag.
        aligned_face (numpy.ndarray): Final aligned face image (RGB).
    """
    try:
        results = {}
        aligned_face, detection_info = detect_and_align_face(image_path, target_size=QUALITY_TARGET_SIZE)

        brightness, lighting_ok = check_lighting(aligned_face)
        results['brightness'] = brightness

        if not lighting_ok:
            raise ValueError(f"Image lighting is not acceptable")

        # Preprocess for FaceQnet and predict quality score
        preprocessed_face = preprocess_for_quality(aligned_face)
        quality_score = quality_model.predict(preprocessed_face, verbose=1)
        quality_score = quality_score[0][0]
        results['quality_score'] = quality_score
        results['final_valid'] = quality_score >= quality_threshold

        return results, aligned_face

    except ValueError as e:
        printErr(e)
        raise e
    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )


def is_valid_face(face_image):
    results, aligned_face = validate_image(face_image, quality_threshold=QUALITY_THRESHOLD)

    print("Quality Score:", results['quality_score'])
    # print("Brightness (mean intensity):", results['brightness'])

    return results['final_valid']
