from typing import Annotated
from fastapi import FastAPI, File, UploadFile, Depends, Form
from PIL import Image
from PIL import ImageOps
import io
import numpy as np
import onnxruntime as rt
from pydantic import BaseModel
import json
import hashlib
import redis

# load tags
# np.str_ is not work. https://stackoverflow.com/questions/14639496/how-to-create-a-numpy-array-of-arbitrary-length-strings
tag_csv_dtype = [('tag_id', int), ('name', object), ('category', int), ('count', int)]
tag_pool = np.genfromtxt("./wd-v1-4-moat-tagger-v2/selected_tags.csv",
                         skip_header=1, delimiter=",", dtype=tag_csv_dtype)
# init model
sess = rt.InferenceSession("./wd-v1-4-moat-tagger-v2/model.onnx", providers=None)
input_name = sess.get_inputs()[0].name

# deploy fastapi


class Evaluate(BaseModel):
    file: UploadFile = Form(...)
    threshold: float = 0.3
    format: str = 'json'
    limit: int = 50


app = FastAPI()

rds = redis.Redis(host='localhost', port=6379, db=0)


@app.get("/")
async def root():
    return {"message": "Hello autotagger"}

# Read form with fastapi
# https://github.com/tiangolo/fastapi/discussions/8406


@app.post("/evaluate")
async def evaluate(form_data: Evaluate = Depends()):
    print(form_data.file.filename)
    results = []

    # How to resize+padding?
    # https://stackoverflow.com/a/72393560/12764484
    threshold = 0.3
    for file in [form_data.file]:
        fp = await file.read()
        img = ImageOps.pad(Image.open(io.BytesIO(fp)).convert('RGB'), (448, 448))
        img_sha256 = hashlib.sha256(img.tobytes()).hexdigest()
        tags_info_str = rds.get(img_sha256)
        if tags_info_str:
            tags_info = json.loads(tags_info_str)
            print(f'Hit redis: {file.filename}, hash: {img_sha256}')
            results.append({"filename": file.filename, "tags": tags_info})
            continue

        pred = sess.run(None, {input_name: np.expand_dims(np.float32(img), 0)})[0]
        print(f"pred size = {pred.shape}")
        match_tags = tag_pool[np.argwhere(pred[0] > threshold).squeeze()]['name']
        match_score = pred[0][pred[0] > threshold]
        tags_info = {str(tag): float(score) for tag, score in zip(match_tags, match_score)}
        results.append({"filename": file.filename, "tags": tags_info})
        rds.set(img_sha256, json.dumps(tags_info))
    print(results)
    return results
