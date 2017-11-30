import boto3
from datetime import datetime
from lib.image import image_hash, download_image, downscale_image

BUCKET = 'vizlab-imgs'
DOWN_SIZE = (800, 800)
HASH_SIZE = 128 # must be a power of 2
QUALITY = 80


def handler(event, context):
    s3 = boto3.client('s3')

    # dowload the image
    # and compute the image hash from the original.
    # we don't save the original because it will be too expensive.
    url = event.get('url')
    img = download_image(url)
    hash = image_hash(img, HASH_SIZE)
    key = hash # TODO is this the best way to do this?

    meta = {
        'hash': hash,
        'size': img.size,
        'format': img.format,
        'mode': img.mode,
        'retrieved': datetime.utcnow().timestamp()
    }

    # save the downscaled image
    out = downscale_image(img, DOWN_SIZE, QUALITY)
    s3.Bucket(BUCKET).put(key=key, data=out, acl='private')
    return meta
