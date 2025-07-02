#!/usr/bin/env python3
"""
build_faiss_index.py

This script calculates face embeddings using Facenet (via facenet_pytorch),
indexes them with Faiss, and saves or updates the index on disk. It also
maintains a metadata JSON file mapping each embedding (by its position in
the index) to its corresponding user id and image path.
"""

import os
import json
import numpy as np
import torch
import faiss
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
from src.utils.printErr import printErr
from src.facial_recognition_pipelines.exceptions import FaceDetectionError, EmptyIndexError

# Define paths
INDEX_PATH = "src/index/faiss_index.bin"  # File where Faiss index is stored
METADATA_PATH = "src/index/metadata.json"  # JSON file for storing metadata mapping
METADATA = []
INDEX = None
DIMENSION = 512


# Set device for torch
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

# Initialize face detector and FaceNet model
mtcnn = MTCNN(
    image_size=160, margin=0, min_face_size=20,
    thresholds=[0.6, 0.7, 0.7], factor=0.709, post_process=True,
    device=device
)

resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)


def load_metadata():
    try:
        global METADATA
        # Load existing metadata if available
        if len(METADATA) == 0:
            if os.path.exists(METADATA_PATH):
                with open(METADATA_PATH, 'r') as f:
                    METADATA = json.load(f)

        return METADATA
    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )


def load_index():
    """Load the Faiss index from disk if it exists, or create a new one."""
    try:
        global INDEX

        if INDEX is None:
            if os.path.exists(INDEX_PATH):
                INDEX = faiss.read_index(INDEX_PATH)

                # Check if dimension matches, if not, raise a value error
                if INDEX.d != DIMENSION:
                    raise ValueError(
                        f"Index dimension ({INDEX.d}) does not match embedding dimension ({DIMENSION}). "
                        "Please verify the model or reinitialize the index manually.")

            else:
                INDEX = faiss.IndexFlatIP(DIMENSION)

        return INDEX
    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )

def l2_normalize(x: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    norm = np.linalg.norm(x, axis=1, keepdims=True)
    return x / (norm + eps)


def calculate_face_embeddings(image_path):
    """
    Calculate the face embedding for a given image.
    Raises a ValueError if no face is detected.
    """
    try:
        img = Image.open(image_path).convert('RGB')
        aligned_face = mtcnn(img)

        if aligned_face is None:
            raise FaceDetectionError("MTCNN face detector failed to detect a face when calculating embeddings")

        aligned_face = aligned_face.unsqueeze(0)
        aligned_face = aligned_face.to(device)
        embedding = resnet(aligned_face).detach().cpu().numpy()

        return l2_normalize(embedding)
    except Exception as e:
        printErr(e)

        if type(e) == FaceDetectionError:
            raise

        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )


def index_embedding(image_path, user_id, image_hash):
    try:
        load_metadata()
        # Create a set of already processed image paths for quick lookup
        processed_images = set(item['image_path'] for item in METADATA)

        if image_path in processed_images:
            return

        new_embedding = calculate_face_embeddings(image_path)
        new_metadata = {
            "user_id": user_id,
            "image_path": str(image_path),
            "hash": image_hash
        }

        METADATA.append(new_metadata)

        load_index()
        INDEX.add(new_embedding)
        faiss.write_index(INDEX, INDEX_PATH)

        with open(METADATA_PATH, 'w') as f:
            json.dump(METADATA, f, indent=4)

    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )


def compute_cosine_similarity(query_emb, db_emb):
    """
    Since embeddings are normalized, cosine similarity is simply the dot product.
    """
    return np.dot(query_emb, db_emb.T)[0][0]


def get_metadata_for_index(idx):
    """
    Retrieve the metadata (user_id) for a given index.
    Assumes that the metadata list order corresponds to the order of embeddings in the Faiss index.
    """
    load_metadata()

    if idx < len(METADATA):
        return METADATA[idx]["user_id"]

    return "Unknown"

async def is_indexed(image_hash):
    load_metadata()

    if len(METADATA) > 0 and any(item.get('hash') == image_hash for item in METADATA):
        return True

    return False

def is_empty_index():
    load_index()
    return INDEX.ntotal == 0

def compare_faces(image_path):
    try:
        load_index()
        load_metadata()

        if INDEX.ntotal == 0:
            raise EmptyIndexError("No images have been indexed yet")

        K = 4 if INDEX.ntotal > 4 else 1

        embedding = calculate_face_embeddings(image_path)

        if embedding is None:
            raise FaceDetectionError("No face detected")

        D, I = INDEX.search(embedding, K)

        # Compute cosine similarity for each returned neighbor and choose the best match
        best_similarity = D[0][0]
        best_index = I[0][0]

        label = 'Unknown' if best_similarity < 0.8 else get_metadata_for_index(best_index)
        similarity_percent = 0 if best_similarity < 0.8 else int(best_similarity * 100)

        return similarity_percent, label

    except FaceDetectionError as e:
        printErr(e)
        raise FaceDetectionError("Unable to detect a face. Please try again.")

    except IndexError as e:
        printErr(e)
        raise

    except Exception as e:
        printErr(e)

        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )