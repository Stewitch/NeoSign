import csv
import io
import random
import re
import string
from typing import Iterable, Sequence

from openpyxl import Workbook
from core.models import SystemConfig
from django.http import HttpResponse


def generate_random_password(length: int = 12) -> str:
    # Load policy from SystemConfig
    try:
        cfg, _ = SystemConfig.objects.get_or_create(pk=1)
    except Exception:
        cfg = None

    length = max(6, (cfg.password_length if cfg else length))
    require_upper = (cfg.password_require_uppercase if cfg else True)
    require_lower = (cfg.password_require_lowercase if cfg else True)
    require_digits = (cfg.password_require_digits if cfg else True)
    require_symbols = (cfg.password_require_symbols if cfg else True)
    symbols = (cfg.password_symbols if cfg else '!@#$%^&*')

    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    syms = symbols or ''

    pools = []
    if require_upper:
        pools.append(upper)
    if require_lower:
        pools.append(lower)
    if require_digits:
        pools.append(digits)
    if require_symbols and syms:
        pools.append(syms)

    # Fallback if all disabled: use digits
    if not pools:
        pools = [digits]

    # Ensure each required category contributes at least one character
    password_chars = []
    for pool in pools:
        password_chars.append(random.choice(pool))

    # Fill remaining length from combined pool
    all_chars = ''.join(pools)
    while len(password_chars) < length:
        password_chars.append(random.choice(all_chars))

    # Shuffle to avoid predictable positions
    random.shuffle(password_chars)
    return ''.join(password_chars)


def export_table_to_csv(headers: Sequence[str], rows: Iterable[Sequence[str]], filename: str) -> HttpResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    return response


def export_table_to_xlsx(headers: Sequence[str], rows: Iterable[Sequence[str]], filename: str, column_widths: Sequence[int] = None) -> HttpResponse:
    from openpyxl.styles import Alignment
    
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = '导出'
    sheet.append(list(headers))
    for row in rows:
        sheet.append(list(row))
    
    # Set column widths if provided
    if column_widths:
        for idx, width in enumerate(column_widths, start=1):
            column_letter = chr(64 + idx)  # A=65, B=66, etc.
            sheet.column_dimensions[column_letter].width = width
    
    # Format all cells to preserve leading zeros and display as text for student IDs
    for row in sheet.iter_rows(min_row=2):  # Skip header row
        for idx, cell in enumerate(row):
            if idx == 0 and cell.value:  # First column (student_id)
                # Force text format to preserve leading zeros
                cell.number_format = '@'
            # Center align all cells
            cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Center align header row
    for cell in sheet[1]:
        cell.alignment = Alignment(horizontal='center', vertical='center')

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
