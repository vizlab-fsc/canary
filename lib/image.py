import io
import requests
import tempfile
import imagehash
from PIL import Image


def image_hash(img, hash_size):
    """generate perceptual hash for image.
    uses whash, but other options are available:
    <https://github.com/JohannesBuchner/imagehash>"""
    return imagehash.dhash(img, hash_size=hash_size)


def image_hash_from_hex(hex, hash_size):
    return imagehash.hex_to_hash(hex, hash_size=hash_size)


def download_image(url):
    """downloads a remote image to a PIL Image"""
    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    res = requests.get(url, stream=True)
    if res.status_code == 200:
        for chunk in res:
            buffer.write(chunk)
        buffer.seek(0)
        return Image.open(io.BytesIO(buffer.read()))
    else:
        res.raise_for_status()


def downscale_image(img, size, quality):
    """downscale the image to fit a limit size,
    return a file stream"""
    # TODO gif support?
    img = resize_to_limit(img, size)
    img = img.convert('RGB')
    data = io.BytesIO()
    img.save(data, format='JPEG', quality=quality)
    data.seek(0)
    return data


def resize_to_limit(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    if x_i <= x_t and y_i <= y_t:
        return img.copy()
    else:
        return resize_to_fit(img, target_size)


def resize_to_fit(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    x_scale = x_t/x_i
    y_scale = y_t/y_i
    scale = min(x_scale, y_scale)
    scaled_size = (
        int(x_i*scale),
        int(y_i*scale)
    )
    return img.resize(scaled_size)


def resize_to_fill(img, target_size):
    x_t, y_t = target_size
    x_i, y_i = img.size
    x_scale = x_t/x_i
    y_scale = y_t/y_i
    scale = max(x_scale, y_scale)

    x_new = int(x_i*scale)
    y_new = int(y_i*scale)
    img = img.resize((x_new, y_new))
    x_center = x_new/2
    y_center = y_new/2

    l = int(x_center - x_t/2)
    r = int(x_center + x_t/2)
    u = int(y_center - y_t/2)
    d = int(y_center + y_t/2)

    img = img.crop((l, u, r, d))

    # Sometimes we may be one pixel off,
    # so just adjust if necessary
    if img.size != target_size:
        img = img.resize(target_size)
    return img
