from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.models import Base
from .api import endpoints
from .db import engine
import logging
from sqlalchemy import inspect, text

logger = logging.getLogger(__name__)

def run_migrations():
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table_name in Base.metadata.tables.keys():
            if not inspector.has_table(table_name):
                continue

            existing_columns = {c['name'] for c in inspector.get_columns(table_name)}

            table = Base.metadata.tables[table_name]
            for column in table.columns:
                if column.name not in existing_columns:
                    col_type = str(column.type.compile(engine.dialect))
                    # Handle basic SQLite types that might differ slightly in string rep
                    if "VARCHAR" in col_type:
                        col_type = "VARCHAR"
                    elif "DATETIME" in col_type:
                        col_type = "DATETIME"
                    elif "BOOLEAN" in col_type:
                        col_type = "BOOLEAN"

                    default_clause = ""
                    if column.default is not None and column.default.is_scalar:
                        if isinstance(column.default.arg, str):
                            default_clause = f" DEFAULT '{column.default.arg}'"
                        elif isinstance(column.default.arg, bool):
                            default_clause = f" DEFAULT {1 if column.default.arg else 0}"
                        elif isinstance(column.default.arg, (int, float)):
                            default_clause = f" DEFAULT {column.default.arg}"

                    stmt = f"ALTER TABLE {table_name} ADD COLUMN {column.name} {col_type}{default_clause}"
                    try:
                        conn.execute(text(stmt))
                        logger.warning(f"Auto-migrated: Added column {table_name}.{column.name}")
                    except Exception as e:
                        logger.error(f"Failed to add column {table_name}.{column.name}: {e}")

# First run standard create_all for missing tables
Base.metadata.create_all(bind=engine)
# Then attempt to auto-migrate missing columns for existing tables
run_migrations()

app = FastAPI(title="VeloRank API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to VeloRank API"}
