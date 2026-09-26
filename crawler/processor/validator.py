"""PDF integrity verification and corrupted file removal."""

import os
from pathlib import Path
from typing import Tuple
from pypdf import PdfReader
from pypdf.errors import PdfReadError

from config import MAX_FILE_SIZE_BYTES, MIN_FILE_SIZE_BYTES
from utils.logger import get_logger

logger = get_logger("processor.validator")


def validate_pdf(file_path: Path) -> Tuple[bool, str]:
    """Validate that a file is a non-corrupt, readable PDF meeting size criteria.
    
    Returns:
        (is_valid, reason_or_status)
    """
    if not file_path.exists():
        return False, "File does not exist."

    # 1. Check file size
    size = os.path.getsize(file_path)
    if size < MIN_FILE_SIZE_BYTES:
        return False, f"File too small ({size} bytes). Minimum is {MIN_FILE_SIZE_BYTES} bytes."
    if size > MAX_FILE_SIZE_BYTES:
        return False, f"File too large ({size / (1024*1024):.1f} MB). Maximum is {MAX_FILE_SIZE_BYTES / (1024*1024):.1f} MB."

    # 2. Check PDF Magic Bytes in first 1024 bytes
    try:
        with open(file_path, "rb") as f:
            header = f.read(1024)
            if b"%PDF-" not in header:
                return False, "Invalid PDF header magic bytes (not a valid PDF document)."
    except Exception as exc:
        return False, f"Failed to read file header: {exc}"

    # 3. Test integrity with PyPDF parser
    try:
        reader = PdfReader(str(file_path), strict=False)
        num_pages = len(reader.pages)
        if num_pages == 0:
            return False, "PDF contains 0 readable pages."

        # Verify first page can be read/decrypted
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                return False, "PDF is password protected and cannot be decrypted."

        # Attempt to read at least page 1 text or structure
        _ = reader.pages[0].extract_text()
        return True, "Valid PDF"

    except PdfReadError as exc:
        return False, f"PyPDF read error (corrupted structure): {exc}"
    except Exception as exc:
        return False, f"Unexpected error parsing PDF structure: {exc}"


def remove_corrupt_file(file_path: Path, reason: str = "") -> bool:
    """Safely remove a corrupted, truncated, or invalid file from the file system."""
    try:
        if file_path.exists():
            file_path.unlink()
            logger.warning(f"[CORRUPT FILE REMOVED] {file_path.name} | Reason: {reason}")
            return True
        return False
    except Exception as exc:
        logger.error(f"Failed to delete corrupted file {file_path}: {exc}")
        return False

