## Pipeline

1. `arbiter` runs on a schedule, sending out messages containing sources for `scraper` to update
    - output messages in the form: `{"source_id": <SOURCE ID>}`
2. `scraper` fetches post for sources
    - output messages in the form: `{"source_id": <SOURCE ID>, "post": <POST DATA>}`
3. `parser` filters posts for new ones with images, saves them to the db, and extracts image urls
    - output messages in the form: `{"context_id": <CONTEXT ID>, "url": <IMAGE URL>}`
4. `downloader` downloads images, computes their hashes, resizes them, saves them to s3, saves their metadata to db, and associates them with their post ("context")
