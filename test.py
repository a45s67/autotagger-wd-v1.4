import onnxruntime as rt
import numpy as np
from PIL import Image
from PIL import ImageOps

numpy_array = np.random.rand(1, 448, 448, 3).astype(np.float32)
# prediction test
# https://onnxruntime.ai/docs/api/python/tutorial.html

sess = rt.InferenceSession("./wd-v1-4-moat-tagger-v2/model.onnx", providers=None)
input_name = sess.get_inputs()[0].name
pred_onx = sess.run(None, {input_name: numpy_array})[0]
print(pred_onx)

# load tags
# np.str_ is not work. https://stackoverflow.com/questions/14639496/how-to-create-a-numpy-array-of-arbitrary-length-strings
dtype = [('tag_id', int), ('name', object), ('category', int), ('count', int)]
arr = np.genfromtxt("./wd-v1-4-moat-tagger-v2/selected_tags.csv",
                    skip_header=1, delimiter=",", dtype=dtype)
match_tags = arr[np.argwhere(pred_onx[0] > 0.5).squeeze()]['name']

# Try to test real images

# How to resize+padding?
# https://stackoverflow.com/a/72393560/12764484
images = [Image.open('fern.png').convert("RGB"), Image.open('yamata.png').convert("RGB")]
resize_imgs = [ImageOps.pad(img, (448, 448)) for img in images]

for img in resize_imgs:
    np_image = np.float32(img)
    pred = sess.run(None, {input_name: np.expand_dims(np_image, 0)})[0]
    match_tags = arr[np.argwhere(pred[0] > 0.5).squeeze()]['name']
    print(match_tags)
