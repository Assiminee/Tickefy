from pathlib import Path
from fastapi import FastAPI, APIRouter, UploadFile
from fastapi.responses import JSONResponse
from src.api.utils.helpers import save_tmp_file, save_image, create_directories, send_signal, compute_image_hash
from src.facial_recognition_pipelines.exceptions import ExistingUserError
from src.facial_recognition_pipelines.index_pipeline import index_embedding, compare_faces, is_indexed, is_empty_index
from src.facial_recognition_pipelines.quality_assesment_pipeline import is_valid_face
from src.utils.printErr import printErr
import os
create_directories()
app = FastAPI()
router = APIRouter(prefix="/api/v1")

@router.get("/")
def root():
    return {"message": "Hello assiminee!"}

@router.post('/users/{user_id}/assess_image_quality')
async def assess_image_quality(user_id, image : UploadFile):
    temp_file_path = None
    try:
        image_hash = await compute_image_hash(image)
        image_is_indexed = await is_indexed(image_hash)

        if image_is_indexed:
            print("Image already indexed")
            raise ValueError(
                "The image provided is a duplicate of a previously saved image"
            )

        temp_file_path = save_tmp_file(image)
        valid_face = is_valid_face(temp_file_path)

        if not is_empty_index() and valid_face:
            similarity, label = compare_faces(temp_file_path)

            if similarity > .8 and label != user_id:
                raise ExistingUserError(label)

        ret, img_path = save_image(image, user_id, valid_face, temp_file_path)

        if ret:
            index_embedding(img_path, user_id, image_hash)

        return {"is_image_valid" : bool(valid_face)}

    except ExistingUserError as e:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()

        return JSONResponse(
            status_code=409, content={"label": e}
        )

    except Exception as e:
        if temp_file_path and temp_file_path.exists():
            temp_file_path.unlink()

        return JSONResponse(
            status_code=400, content={"is_image_valid" : False, "message": str(e)}
        )

@router.post('/users/identify')
async def identify(image : UploadFile):
    temp_file_path = Path('')
    signal = "0"

    try:
        image_hash = await compute_image_hash(image)
        image_is_indexed = await is_indexed(image_hash)

        temp_file_path = save_tmp_file(image)

        # if valid_face:
        similarity, label = compare_faces(temp_file_path)
        print(similarity)

        if similarity < 0.8:
            temp_file_path.unlink()
            raise Exception("Unable to identify the face")

        if image_is_indexed:
            temp_file_path.unlink()
        else:
            ret, img_path = save_image(image, label, True, temp_file_path)
            index_embedding(img_path, label, image_hash)

            signal = "1"

        send_signal(signal)
        return {"identified" : similarity > 0.8, "message" : label}

        # raise Exception("Unable to identify the face")
    except Exception as e:
        printErr(e)
        if temp_file_path.exists():
            temp_file_path.unlink()

        return JSONResponse(
            status_code=400, content={"identified" : False, "message": str(e)}
        )

# @router.post('/compare')
# def compare():
#     values = []
#     images_path = 'images'
#     for i in range(5):
#         for user_dir in os.listdir(images_path):
#             user_dir_path = os.path.join(images_path, user_dir)
#             print()
#             print("Trying to identify images of {} ".format(user_dir))
#             d = {user_dir: []}
#             for image in os.listdir(user_dir_path):
#                 image_path = os.path.join(user_dir_path, image)
#
#                 valid_face = is_valid_face(image_path)
#
#                 if valid_face:
#                     similarity, label = compare_faces(image_path)
#                     d[user_dir].append((similarity, label))
#                     print("Image similarity is: {}".format(similarity))
#
#             values.append(d)
#
#     return {"message": "Face comparison complete", "values": values}

app.include_router(router)
