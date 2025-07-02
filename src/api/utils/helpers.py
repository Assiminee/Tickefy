from pathlib import Path
import shutil
from fastapi import UploadFile
from uuid import uuid4
import os
import socket
from src.utils.printErr import printErr
from hashlib import sha256

INDEX_DIR = Path('src/index')
DATA_DIR = Path('src/data')
TEMP_DIR = Path(DATA_DIR, 'temp')

def sha256_of_bytes(data: bytes) -> str:
    h = sha256()
    h.update(data)
    return h.hexdigest()

async def compute_image_hash(image: UploadFile) -> str:
    """
    Read the entire contents of the UploadFile into memory,
    compute sha256, then rewind the file so it can be read again.
    """
    data = await image.read()        # bytes of the image
    digest = sha256_of_bytes(data)
    await image.seek(0)               # rewind so you can reopen it
    return digest

def create_directories():
    try:
        if not TEMP_DIR.exists():
            print("Creating temp dir")
            TEMP_DIR.mkdir(parents=True, exist_ok=True)

        if not INDEX_DIR.exists():
            print("Creating index dir")
            INDEX_DIR.mkdir(exist_ok=True)

    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )


def send_signal(signal="0"):
    # Adresse IP du serveur (remplace par l'IP du destinataire)
    IP = '10.122.104.26'  # ← Change cette IP !
    PORT = 12345

    # Création du socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connexion au serveur
        client_socket.connect((IP, PORT))
        print(f"Connected to server {IP}:{PORT}")

        client_socket.send(signal.encode())
        print("Signal sent.")

        # Réception de la réponse
        resp = client_socket.recv(1024).decode()
        print("Server response :", resp)

    except Exception as e:
        printErr(e)
        raise

    finally:
        client_socket.close()

def save_tmp_file(image : UploadFile):
    try:
        temp_file_path = Path(TEMP_DIR, image.filename)
        print(f"Saving {image.filename} to {temp_file_path}")

        with open(temp_file_path, 'wb') as buffer:
            shutil.copyfileobj(image.file, buffer)

        return temp_file_path

    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )

def save_image(image : UploadFile, user_id, valid : bool, temp_file_path : Path):
    try:
        if not valid:
            if temp_file_path.exists():
                temp_file_path.unlink()

            return False, None

        user_dir = Path(DATA_DIR, str(user_id))
        new_file_name = str(uuid4()) + os.path.splitext(image.filename)[1]
        new_file_path = Path(user_dir, new_file_name)

        if not user_dir.exists():
            user_dir.mkdir(parents=True, exist_ok=True)

        shutil.move(temp_file_path, new_file_path)

        return True, new_file_path

    except Exception as e:
        printErr(e)
        raise Exception(
            "An unexpected error occurred. Please try again later."
            "If the error persists, please report it to the developer."
        )