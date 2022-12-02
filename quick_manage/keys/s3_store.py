from minio import Minio
from minio.datatypes import Object
from urllib3.response import HTTPResponse
from typing import List, Generator
from io import BytesIO

from quick_manage.s3 import S3Config
from ..keys import KeyStore


class S3Store(KeyStore):
    def __init__(self, config: S3Config):
        self.config = config
        self.config.prefix = self.config.prefix.strip("/")

    def put(self, key_name: str, value: str):
        key_name = key_name.strip()
        object_name = f"{self.config.prefix}/{key_name}" if self.config.prefix else key_name

        client = self._client()
        raw_bytes = value.encode("utf-8")
        buffer = BytesIO(raw_bytes)
        client.put_object(self.config.bucket, object_name, buffer, len(raw_bytes))

    def get(self, key_name: str) -> str:
        key_name = key_name.strip()
        object_name = f"{self.config.prefix}/{key_name}" if self.config.prefix else key_name

        client = self._client()
        result: HTTPResponse = client.get_object(self.config.bucket, object_name)
        return result.data.decode("utf-8")

    def list(self) -> List[str]:
        client = self._client()
        prefix = self.config.prefix + "/"
        result: Generator[Object] = client.list_objects(self.config.bucket, prefix, recursive=True)
        return [item.object_name.lstrip(prefix) for item in result]

    def _client(self) -> Minio:
        return Minio(self.config.url,
                     access_key=self.config.access_key,
                     secret_key=self.config.secret_key)
