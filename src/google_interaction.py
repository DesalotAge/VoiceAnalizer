"""Define main class for interaction with google cloud services."""
from google.cloud import storage
from pathlib import Path
from typing import Optional


class GoogleCloudInteraction:
    """Define the main interaction methods."""

    def __init__(self, bucket_name):
        """Init google storage client and bucket."""
        self._client = storage.Client()
        self._bucket = self._client.bucket(bucket_name)

    def upload_file(
            self,
            filename: Optional[str] = None,
            upload_filename: Optional[str] = None,
            upload_binary: bool = False
            ) -> None:
        """Upload file to google storage bucket."""
        if filename is not None:
            # if filename exists trying to write data from this
            path = Path(filename)

            if not path.is_file():
                # if given filename is not a file return False
                raise FileNotFoundError("Given file doesn't exists")
            if upload_filename is None:
                # if upload filename is not given change it from existing file
                upload_filename = path.name

            # trying to move file in bucket
            blob = self._bucket.blob('files/' + upload_filename)
            blob.upload_from_file(open(filename, "rb" if upload_binary else "r"))
