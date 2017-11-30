from lib.parser import image_urls


def handler(event, context):
    posts = event.get('posts')
    processed = []
    for post in posts:
        images = post['attachments']
        images.extend(image_urls(post))
        post['images'] = images
        processed.append(post)
    return processed
