import io
import tempfile
from pathlib import Path
from abc import ABC, abstractmethod


class AudioSource(ABC):
    """(Abstract) Represents an audio source."""

    def __init__(self):
        self.file = None

    @abstractmethod
    def get_path(self):
        return self.file


class FileAudioSource(AudioSource):
    """Reads an audio file to be used as an audio source."""

    def __init__(self, filepath):
        super().__init__()
        self.filepath = filepath
        with open(self.filepath, "r", encoding="utf-8") as file:
            self.file = file

    def get_path(self):
        return self.filepath


class BytesAudioSource(AudioSource):
    """Writes a byte stream to a file to be used as an audio source."""

    def __init__(self, byte_stream: bytes):
        super().__init__()
        self.file = io.BytesIO(byte_stream)

    def get_path(self):
        # create the directory if it doesn't exist
        Path("./tmp").mkdir(exist_ok=True)

        tmp_file = tempfile.NamedTemporaryFile(
            delete=False, dir="./tmp"
        )  # create a temporary file
        tmp_file.write(self.file.read())  # write the bytes to the file
        tmp_file.flush()  # flush the buffer to force writing to the file
        tmp_file.close()  # close the file
        return tmp_file.name  # return the file path
