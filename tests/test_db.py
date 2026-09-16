from sqlalchemy import inspect

from app.db.session import engine, initialize_database


EXPECTED_TABLES = {
    "users",
    "recipes",
    "recipe_images",
    "ingredients",
    "preparation_steps",
    "tags",
    "recipe_tags",
    "shopping_lists",
    "shopping_list_items",
    "import_jobs",
}


def test_initialize_database_creates_expected_tables() -> None:
    initialize_database()

    table_names = set(inspect(engine).get_table_names())

    assert EXPECTED_TABLES.issubset(table_names)
