import csv
import io
import random
import re
import string
from typing import Iterable, Sequence

from openpyxl import Workbook
from django.http import HttpResponse


def generate_random_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(chars) for _ in range(length))


def export_table_to_csv(headers: Sequence[str], rows: Iterable[Sequence[str]], filename: str) -> HttpResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


def export_table_to_xlsx(headers: Sequence[str], rows: Iterable[Sequence[str]], filename: str) -> HttpResponse:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '导出'
    sheet.append(list(headers))
    for row in rows:
        sheet.append(list(row))

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    workbook.save(response)
    return response


def parse_users_from_text(text: str) -> dict[str, str]:
    """Parse student list from text input.
    Accepts lines or whitespace separated entries, supports formats:
    - "1234567890"
    - "1234567890 张三"
    - "1234567890,张三" or "1234567890，张三"
    Returns dict {student_id: name_or_empty}
    """
    if not text:
        return {}
    entries = re.split(r"[\r\n\s]+", text.strip())
    result: dict[str, str] = {}
    # Re-scan lines to preserve association when using comma format per line
    for line in re.split(r"\r?\n", text.strip()):
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^(\d{4,23})\s*[，,]\s*(.+)$", line)
        if m:
            sid = m.group(1)
            name = m.group(2).strip()
            if re.match(r"^\d{4,23}$", sid):
                result[sid] = name
            continue
        # fallback: whitespace split
        parts = line.split()
        if len(parts) >= 2 and re.match(r"^\d{4,23}$", parts[0]):
            result[parts[0]] = " ".join(parts[1:])
        elif len(parts) == 1 and re.match(r"^\d{4,23}$", parts[0]):
            result[parts[0]] = result.get(parts[0], "")
    # Also include any standalone ids from global entries
    for token in entries:
        if re.match(r"^\d{4,23}$", token) and token not in result:
            result[token] = ""
    return result


def parse_users_from_csv_upload(file) -> dict[str, str]:
    """Parse uploaded CSV file to {student_id: name}.
    Assumes first column is student_id, second optional is name.
    Skips header row if first cell looks like a label.
    """
    result: dict[str, str] = {}
    try:
        if not file:
            return result
        # Read as text
        data = file.read().decode('utf-8', errors='ignore')
        buffer = io.StringIO(data)
        reader = csv.reader(buffer)
        row_idx = 0
        for row in reader:
            row_idx += 1
            if not row:
                continue
            cell0 = (row[0] or '').strip()
            if row_idx == 1 and re.search(r"username|学号|用户", cell0, re.I):
                continue
            if re.match(r"^\d{4,23}$", cell0):
                name = (row[1] or '').strip() if len(row) > 1 else ''
                result[cell0] = name or result.get(cell0, '')
    except Exception:
        # Silently ignore parse failures; caller can validate emptiness
        pass
    return result
