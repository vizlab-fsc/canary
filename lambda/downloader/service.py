import os
import boto3
from lib.util import parse_sns_event
from lib.models import Image, ImageUsage, Session
from lib.image import image_hash, download_image, downscale_image

DOWN_SIZE = (800, 800)
HASH_SIZE = 16 # must be a power of 2. 16 for more accuracy, but slower
QUALITY = 80


def handler(event, context):
    """
    1. downloads a single image url
    2. computes image hash
    3. saves to db, if completely new image
    4. downscales image and saves to s3
    5. associates the image to a context
    """
    session = Session()
    s3 = boto3.resource('s3')
    bucket_name = os.environ['s3_bucket']
    bucket = s3.Bucket(bucket_name)
    event = parse_sns_event(event)

    # dowload the image
    # and compute the image hash from the original.
    # we don't save the original because it will be too expensive.
    url = event.get('url')
    img = download_image(url)
    hash = str(image_hash(img, HASH_SIZE))
    key = hash

    meta = {
        'height': img.height,
        'width': img.width,
        'format': img.format,
        'mode': img.mode
    }

    # check if image already is saved
    image = session.query(Image).filter(
        Image.hash==hash,
        Image.url==url
    ).first()
    if image is None:
        # save the downscaled image
        out = downscale_image(img, DOWN_SIZE, QUALITY)
        bucket.put_object(Key=key, Body=out, ACL='public-read')

        # create new image
        image = Image(url=url, key=key, hash=hash, **meta)
        session.add(image)
        session.commit()

    # associate the image with the context
    context_id = event.get('context_id')
    usage = ImageUsage(image=image, context_id=context_id)
    session.add(usage)
    session.commit()
    session.close()
