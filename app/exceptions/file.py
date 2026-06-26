class FileError(Exception):
    pass


class FileNameError(FileError):
    pass


class FileTypeError(FileError):
    def __init__(self, file_type: str | None, allowed_types: list[str]) -> None:
        self.file_type = file_type
        self.allowed_types = allowed_types

        super().__init__(f"Invalid file type: {file_type}. Allowed: {allowed_types}")
