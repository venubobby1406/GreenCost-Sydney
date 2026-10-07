"""Safe, project-specific attachment names for browser downloads."""
import re
import unicodedata
from urllib.parse import quote


def report_filename(name, years, extension):
    stem = unicodedata.normalize("NFKC", name or "")
    stem = re.sub(r"[^\w -]", "", stem).strip(" _-")[:80].rstrip(" _-")
    stem = re.sub(r"\s+", "-", stem) or "GreenCost"
    return f"{stem}-{years}-year-report.{extension}"


def attachment_header(name, years, extension):
    filename = report_filename(name, years, extension)
    ascii_name = report_filename((name or "").encode("ascii", "ignore").decode(), years, extension)
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{quote(filename, safe="")}'
