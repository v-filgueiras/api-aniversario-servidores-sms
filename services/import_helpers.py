import re
import unicodedata
from datetime import date, datetime

import pandas as pd

DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")

TRUE_VALUES = {"true", "1", "1.0", "sim", "yes", "y", "s", "ativo"}
FALSE_VALUES = {"false", "0", "0.0", "nao", "não", "no", "n", "inativo"}

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

COLUMN_ALIASES = {
    "full_name": {"full_name", "nome", "nome completo", "name", "servidor"},
    "email": {"email", "e-mail", "e mail"},
    "birth_date": {"birth_date", "data_nascimento", "data de nascimento", "nascimento", "data nascimento"},
    "active": {"active", "ativo"},
}


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in normalized if not unicodedata.combining(ch))


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename whatever columns the sheet has (nome/full_name, ativo/active, ...)
    to the canonical names the rest of the app expects. Raises ValueError
    listing any required column that couldn't be matched."""

    rename_map = {}
    for original in df.columns:
        key = _strip_accents(str(original).strip().lower())
        for canonical, aliases in COLUMN_ALIASES.items():
            if key in aliases:
                rename_map[original] = canonical
                break

    df = df.rename(columns=rename_map)

    missing = [c for c in COLUMN_ALIASES if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes no arquivo: {', '.join(missing)}")

    return df


def parse_birth_date(raw_value) -> date:

    if isinstance(raw_value, pd.Timestamp):
        return raw_value.date()

    if isinstance(raw_value, date):
        return raw_value

    text = str(raw_value).strip()

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return pd.to_datetime(text, dayfirst=True).date()


def parse_active(raw_value) -> bool:
    if isinstance(raw_value, bool):
        return raw_value

    if isinstance(raw_value, (int, float)) and not pd.isna(raw_value):
        return bool(raw_value)

    text = str(raw_value).strip().lower()

    if text in TRUE_VALUES:
        return True
    if text in FALSE_VALUES:
        return False

    raise ValueError(f"valor de 'active' inválido: {raw_value!r}")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.match(str(value).strip()))


def read_spreadsheet(filename: str, file_obj) -> pd.DataFrame:
    if filename.endswith(".csv"):
        df = pd.read_csv(file_obj)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(file_obj)
    else:
        raise ValueError("Formato de arquivo inválido. Envie um .csv ou .xlsx")

    return normalize_columns(df)