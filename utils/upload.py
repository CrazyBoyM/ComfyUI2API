# -*- coding: utf-8 -*-
import io
import os
import uuid
import config
import requests
from PIL import Image

import logging

LOG = logging.getLogger(__name__)


class DownloadFailureError(OSError):
    ...


class NotFoundError(OSError):
    ...


def clean_files(filenames):
    for filename in filenames:
        try:
            os.remove(filename)
        except FileNotFoundError:
            ...
        except Exception as e:
            LOG.error(f"fail to delete the file '{filename}': {str(e)}")
        else:
            LOG.info(f"successfully clean the file '{filename}'")


def generate_filename(extension: str = ".jpg"):
    random_uuid = uuid.uuid4()
    filename = str(random_uuid) + extension
    return filename


def generate_filename_without_ext():
    return str(uuid.uuid4())


def _download_from_url(url: str, timeout=10, stream=None) -> requests.Response:
    try:
        resp = requests.get(url, timeout=timeout, stream=stream)
    except Exception as e:
        raise DownloadFailureError(str(e))

    if resp.status_code == 200:
        return resp
    elif resp.status_code == 404:
        raise NotFoundError(f"url '{url}' returns not found")
    else:
        raise DownloadFailureError(f"statuscode={resp.status_code}, body={resp.text}")


def download_file_from_url(url: str, output_path: str) -> None:
    resp = _download_from_url(url, stream=True)
    with open(output_path, "wb") as f:
        for data in resp.iter_content(1024):
            f.write(data)


def load_file_from_url(url: str) -> bytes:
    return _download_from_url(url).content


def load_image_from_url(url: str) -> Image.Image:
    imgio = io.BytesIO(load_file_from_url(url))
    return Image.open(imgio)


def upload_file_from_image(
    image: Image.Image,
    *,
    url: str = "",
    ext: str = ".png",
    task_id: str = "",
    storage: str = "",
) -> str:
    imgio = io.BytesIO()
    image.save(imgio, format="PNG")
    imgio.seek(0)
    return _upload_file_from_reader(
        imgio, ext=ext, url=url, task_id=task_id, storage=storage
    )


def upload_file_from_path(
    filepath: str,
    *,
    url: str = "",
    ext: str = ".png",
    task_id: str = "",
    storage: str = "",
) -> str:
    with open(filepath, "rb") as f:
        return _upload_file_from_reader(
            f, ext=ext, url=url, task_id=task_id, storage=storage
        )


def _upload_file_from_reader(
    input: io.IOBase,
    *,
    url: str = "",
    ext=".png",
    task_id: str = "",
    storage: str = "",
) -> str:
    if not url:
        url = get_upload_url(storage)

    url = f"{url}?Ext={ext}"
    headers = {"Authorization": f"Bearer {config.APIKEY}"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(
            f"fail to get signed upload url: statuscode={resp.status_code}, err={resp.text}"
        )

    data = resp.json()
    method = data.get("Method", "PUT")
    signedurl = data["SignedUrl"]
    resulturl = data["FileUrl"]

    resp = requests.request(method, signedurl, data=input)
    if resp.status_code == 200:
        return resulturl
    raise Exception(
        f"fail to upload file by signurl: statuscode={resp.status_code}, err={resp.text}"
    )


def get_upload_url(storage: str = "") -> str:
    url = config.UPLOAD_SIGN_URL
    if "{storage}" in url:
        if not storage and config.DEFAULT_STORAGE:
            storage = config.DEFAULT_STORAGE
        if storage:
            url = url.replace("{storage}", storage)
    return url
