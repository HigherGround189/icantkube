import os
from typing import List, Optional

import pymysql
from fastapi import FastAPI, HTTPException

app = FastAPI(title="Machines Data", redirect_slashes=False)

DEFAULT_DB_HOST = "mariadb"
DEFAULT_DB_PORT = 3306
DEFAULT_DB_NAME = "machines"
DEFAULT_DB_USER = "admin"
DEFAULT_DB_TABLE = "machines"


def getenv_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid int for {name}: {value}") from exc


def get_db_config() -> dict:
    return {
        "host": os.getenv("DB_HOST", DEFAULT_DB_HOST),
        "port": getenv_int("DB_PORT", DEFAULT_DB_PORT),
        "user": os.getenv("DB_USER", DEFAULT_DB_USER),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", DEFAULT_DB_NAME),
        "cursorclass": pymysql.cursors.DictCursor,
        "connect_timeout": 5,
        "read_timeout": 10,
        "write_timeout": 10,
    }


def get_table_name() -> str:
    table = os.getenv("DB_TABLE", DEFAULT_DB_TABLE)
    if not table.replace("_", "").isalnum():
        raise RuntimeError("DB_TABLE must be alphanumeric/underscore only")
    return table


def parse_number(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    try:
        return int(text)
    except ValueError:
        try:
            return float(text)
        except ValueError:
            return None


def parse_csv_numbers(value: Optional[str]) -> Optional[List[float]]:
    if value is None:
        return None
    text = value.strip()
    if text == "":
        return None
    items = []
    for part in text.split(","):
        num = parse_number(part)
        if num is None:
            continue
        items.append(num)
    return items if items else None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/all")
def get_all():
    table = get_table_name()
    query = (
        "SELECT name, status, last_inference_results, training_progress "
        f"FROM `{table}`"
    )

    try:
        conn = pymysql.connect(**get_db_config())
    except pymysql.MySQLError as exc:
        raise HTTPException(status_code=500, detail=f"DB connection error: {exc}") from exc

    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except pymysql.MySQLError as exc:
        raise HTTPException(status_code=500, detail=f"DB query error: {exc}") from exc
    finally:
        conn.close()

    results = []
    for row in rows:
        results.append(
            {
                "name": row.get("name"),
                "status": row.get("status"),
                "lastInferenceResults": parse_csv_numbers(row.get("last_inference_results")),
                "trainingProgress": row.get("training_progress"),
            }
        )

    return results
