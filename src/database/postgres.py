
# mypy: ignore-errors

import os

from langgraph.checkpoint.postgres import PostgresSaver


def create_checkpointer() -> PostgresSaver:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is not configured."
        )

    checkpointer = PostgresSaver.from_conn_string(
        database_url
    )

    checkpointer.setup()

    return checkpointer