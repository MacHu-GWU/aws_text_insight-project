# -*- coding: utf-8 -*-

"""
File type detector module
"""

import os
import enum


class FileTypeEnum(enum.Enum):
    text = "text"
    pdf = "pdf"
    image = "image"


file_extensions_mapper = {
    FileTypeEnum.pdf: {".pdf", },
    FileTypeEnum.image: {".jpg", ".jpeg", ".png", ".bmp"}
}


def detect_file_type(path: str) -> FileTypeEnum:
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    for file_type, exts in file_extensions_mapper:
        if ext in exts:
            return file_type
    raise TypeError
