import boto3
from lib.image import image_hash, download_image, downscale_image
from lib.models import Image, ImageUsage, Session

BUCKET = 'vizlab-imgs'
DOWN_SIZE = (800, 800)
HASH_SIZE = 128 # must be a power of 2
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
    s3 = boto3.client('s3')

    # dowload the image
    # and compute the image hash from the original.
    # we don't save the original because it will be too expensive.
    url = event.get('url')
    img = download_image(url)
    hash = image_hash(img, HASH_SIZE)
    key = hash

    meta = {
        'height': img.height,
        'width': img.width,
        'format': img.format,
        'mode': img.mode
    }

    # check if image already is saved
    q = session.query(Image).filter(
        Image.hash==hash,
        Image.url==url
    )
    exists = session.query(q.exists()).scalar()
    if not exists:
        # create new image
        image = Image(url=url, key=key, hash=hash, **meta)
        session.add(image)
        session.commit()

        # save the downscaled image
        out = downscale_image(img, DOWN_SIZE, QUALITY)
        s3.Bucket(BUCKET).put(key=key, data=out, acl='private')

    # associate the image with the context
    context_id = event.get('context_id')
    usage = ImageUsage(image=image, context_id=context_id)
    session.add(usage)
    session.commit()
