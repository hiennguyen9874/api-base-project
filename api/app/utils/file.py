import os
import re
import unicodedata

import aiofiles  # type: ignore
import shortuuid
from fastapi import UploadFile
from loguru import logger

__all__ = [
    "check_extension",
    "secure_filename",
    "gen_filename",
    "save_upload_file",
    "get_file_size",
]

_filename_ascii_strip_re = re.compile(r"[^A-Za-z0-9_.-]")

_windows_device_files = (
    "CON",
    "AUX",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "LPT1",
    "LPT2",
    "LPT3",
    "PRN",
    "NUL",
)


def check_extension(filename: str, extensions: list[str]) -> bool:
    return filename.endswith(tuple(extensions))


def secure_filename(filename: str) -> str:
    r"""Pass it a filename and it will return a secure version of it.  This
    filename can then safely be stored on a regular file system and passed
    to :func:`os.path.join`.  The filename returned is an ASCII only string
    for maximum portability.
    On windows systems the function also makes sure that the file is not
    named after one of the special device files.
    >>> secure_filename("My cool movie.mov")
    'My_cool_movie.mov'
    >>> secure_filename("../../../etc/passwd")
    'etc_passwd'
    >>> secure_filename("i contain cool \xfcml\xe4uts.txt")
    'i_contain_cool_umlauts.txt'
    The function might return an empty filename.  It's your responsibility
    to ensure that the filename is unique and that you abort or
    generate a random filename if the function returned an empty one.
    .. versionadded:: 0.5
    :param filename: the filename to secure
    """
    filename = unicodedata.normalize("NFKD", filename)
    filename = filename.encode("ascii", "ignore").decode("ascii")

    for sep in os.path.sep, os.path.altsep:
        if sep:
            filename = filename.replace(sep, " ")
    filename = str(_filename_ascii_strip_re.sub("", "_".join(filename.split()))).strip("._")

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == "nt" and filename and filename.split(".")[0].upper() in _windows_device_files:
        filename = f"_{filename}"
    return filename


def gen_filename(filename: str) -> str:
    name, extension = os.path.splitext(filename)
    name += f"_{str(shortuuid.ShortUUID().random(length=32))}"
    return name + extension


async def save_upload_file(
    upload_file: UploadFile, folder_path: str, filepath: str | None = None
) -> str | None:
    if upload_file.filename is None:
        return None

    safe_filename = secure_filename(upload_file.filename)

    if filepath is None:
        os.makedirs(folder_path, exist_ok=True)
        filepath = os.path.join(folder_path, safe_filename)

        while os.path.exists(filepath):
            safe_filename = gen_filename(safe_filename)
            filepath = os.path.join(folder_path, safe_filename)
    elif os.path.exists(filepath):
        os.remove(filepath)

    try:
        async with aiofiles.open(filepath, "wb") as f:
            # await f.write(await upload_file.read())  # type: ignore
            while content := await upload_file.read(2**20):
                await f.write(content)  # type: ignore
    except Exception as e:
        logger.warning("Save upload file error: {error}", error=str(e))
        return None
    finally:
        await upload_file.close()

    assert os.path.exists(filepath), f"Can't save file, {filepath}"

    return filepath


def get_file_size(path: str) -> int:
    assert os.path.exists(path), f"Path: {path} not exists"
    assert os.path.isfile(path), f"Path: {path} not file"

    return os.path.getsize(path)
