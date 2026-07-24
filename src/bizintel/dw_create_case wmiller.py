"""dw_create_wmiller.py - example.

An example that creates a star schema data warehouse using DuckDB.

This project combines SQL and Python - two key skills for BI development.
It demonstrates recreating an empty star schema data warehouse.
After calling this, call the etl_case.py script to load data into the warehouse.

Author: Denise Case
Date: 2026-06

Development: This script is intended for development and testing purposes.
  - It drops and recreates the warehouse tables to ensure a clean slate for testing and development.
  - This approach is suitable for development but should be used with caution in production environments.
  - Once a data warehouse is in production, we should use migrations and careful incremental updates.

Process:
    - Create the artifacts/ folder if it does not exist.
    - Connect to (or create) the DuckDB data warehouse.
    - Drop existing tables if they exist.
    - Create dimension tables (customers, products).
    - Create the fact table (sales).
    - Log table creation results.

Output:
- artifacts/smart_sales.duckdb

Terminal command to run this file from the root project folder:

uv run python -m bizintel.dw_create_wmiller

OBS:
  Don't edit this file - it should remain a working example.
  Copy it, rename it with your alias, and modify your copy.
  If you do, include your command to run it in the docstring above and in README.md.
"""

# === Section 1. Import dependencies and set up constants ===


# === IMPORTS (USE uv to CREATE YOUR ENVIRONMENT) ===

from pathlib import Path
from typing import Final

from datafun_toolkit.logger import log_path
import duckdb  # Verify duckdb is in pyproject.toml dependencies

from bizintel.utils_logger import LOG, log_header

# === DECLARE CONSTANTS ===

# Path to the DuckDB data warehouse file.
# DuckDB stores the entire warehouse in one file.
DW_FILE: Final[Path] = Path("artifacts/smart_sales_w.duckdb")


# === Section 2. Define Reusable Functions ===

# === Section 2.1 DEFINE A CREATE DIMENSION CUSTOMERS FUNCTION ===

# A dimension table holds descriptive attributes about a business entity.
# The customers dimension describes who made each purchase.


def create_dim_customers(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the customers dimension table.

    WHY: Dimension tables hold the descriptive context for our facts.
    The customer dimension lets us analyze sales by region,
    join date, and other customer attributes.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("START create customers dimension table....")

    LOG.info("DROP the table if it already exists so we can recreate it cleanly")
    LOG.info("- Use SQL command: DROP TABLE IF EXISTS dim_customers")
    LOG.info("- Use conn.execute() to run the SQL command")

    conn.execute("DROP TABLE IF EXISTS dim_customers")

    LOG.info("CREATE TABLE with typed columns")
    LOG.info("- Every table should have one primary key column")
    LOG.info("- Look at the data to decide suitable column types")
    LOG.info("- CustomerID is the primary key and should be an INTEGER")
    LOG.info("- Name is text so we use VARCHAR (variable number of characters)")
    LOG.info("- Region is text so we use VARCHAR (variable number of characters)")
    LOG.info("- JoinDate should be a DATE column")

    conn.execute("""
        CREATE TABLE dim_customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name VARCHAR,
            region VARCHAR,
            join_date DATE,
            reward_points INTEGER,
            reward_level VARCHAR

        )
    """)

    LOG.info("  dim_customers created.")


# === Section 2.2 DEFINE A CREATE DIMENSION PRODUCTS FUNCTION ===

# The products dimension describes what was purchased.


def create_dim_products(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the products dimension table.

    WHY: The product dimension lets us analyze sales by category,
    price range, and product name.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("START create products dimension table....")

    LOG.info("DROP the table if it already exists so we can recreate it cleanly")
    LOG.info("- Use SQL command: DROP TABLE IF EXISTS dim_products")
    LOG.info("- Use conn.execute() to run the SQL command")

    conn.execute("DROP TABLE IF EXISTS dim_products")

    LOG.info("CREATE TABLE with typed columns")
    LOG.info("- Every table should have one primary key column")
    LOG.info("- Look at the data to decide suitable column types")
    LOG.info("- ProductID is the primary key and should be an INTEGER")
    LOG.info("- ProductName is text so we use VARCHAR (variable number of characters)")
    LOG.info("- Category is text so we use VARCHAR (variable number of characters)")
    LOG.info("- UnitPrice should be a DOUBLE column")

    conn.execute("""
        CREATE TABLE dim_products (
            product_id INTEGER PRIMARY KEY,
            product_name VARCHAR,
            category VARCHAR,
            unit_price DECIMAL(10,2),
            supplier VARCHAR,
            supplier_id INTEGER

        )
    """)

    LOG.info("  dim_products created.")


# === Section 2.3 DEFINE A CREATE FACT SALES FUNCTION ===

# A fact table holds the measurable events we want to analyze.
# Each row in the fact table is one transaction.
# Foreign keys link each sale to its customer and product dimensions.


def create_fact_sales(conn: duckdb.DuckDBPyConnection) -> None:
    """Create the sales fact table.

    WHY: The fact table is the center of a star schema.
    It holds the numeric measures (SaleAmount) and foreign keys
    that link to each dimension table.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("START create sales fact table....")

    LOG.info("DROP the table if it already exists so we can recreate it cleanly")
    LOG.info("- Use SQL command: DROP TABLE IF EXISTS fact_sales")
    LOG.info("- Use conn.execute() to run the SQL command")

    conn.execute("DROP TABLE IF EXISTS fact_sales")

    LOG.info("The fact table references the dimension tables")
    LOG.info("   - use a foreign key to dim_customers(CustomerID)")
    LOG.info("   - use a foreign key to dim_products(ProductID)")

    LOG.info("   - the REFERENCES keyword ensures referential integrity")
    LOG.info("   - every sale must link to a valid customer and product")
    conn.execute("""
        CREATE TABLE fact_sales (
            transaction_id INTEGER PRIMARY KEY,
            sale_date DATE,
            customer_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            store_id INTEGER,
            campaign_id INTEGER,
            sale_amount DECIMAL(10,2),
            sale_type VARCHAR,
            reward_points_earned INTEGER,

        )
    """)

    LOG.info("  fact_sales created.")


# === Section 2.4 DEFINE A DELETE TABLES FUNCTION ===


def delete_tables(conn: duckdb.DuckDBPyConnection) -> None:
    """Delete all tables in reverse order of creation.

    WHY: Ensures a clean slate before creating schema objects.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("START delete tables....")

    LOG.info("- Dropping fact_sales table if it exists")
    conn.execute("DROP TABLE IF EXISTS fact_sales")

    LOG.info("- Dropping dim_products table if it exists")
    conn.execute("DROP TABLE IF EXISTS dim_products")

    LOG.info("- Dropping dim_customers table if it exists")
    conn.execute("DROP TABLE IF EXISTS dim_customers")

    LOG.info("  All tables deleted.")


# === Section 2.5 DEFINE A VERIFY FUNCTION ===


def verify_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Log all tables in the warehouse to verify creation.

    WHY: Always verify after creating schema objects.
    A table that fails silently is harder to debug later.

    Args:
        conn: Open DuckDB connection.

    Returns:
        None
    """
    LOG.info("START verify warehouse schema....")

    LOG.info("SHOW TABLES returns a list of all tables in the database")
    LOG.info("- Calling .fetchall() on the result of SHOW TABLES")
    LOG.info("- Gets the result - we can store it in a variable named 'tables'")
    tables = conn.execute("SHOW TABLES").fetchall()

    LOG.info("  - Retrieved tables from the warehouse.")
    LOG.info(" - tables has a tuple for each table in the warehouse")
    LOG.info(" - the first tuple element (at the 0 index) is the table name")
    LOG.info(f"  Tables in warehouse: {[t[0] for t in tables]}")


# === MAIN FUNCTION ===


def main() -> None:
    """Main function to create the data warehouse schema."""

    log_header(LOG, "BI")

    LOG.info("========================")
    LOG.info("START main()")
    LOG.info("========================")

    log_path(LOG, "Data warehouse:", DW_FILE)

    LOG.info("Create the artifacts/ folder if it does not exist")
    DW_FILE.parent.mkdir(parents=True, exist_ok=True)

    LOG.info("Connect to DuckDB - creates the file if it does not exist")
    LOG.info("Connecting to DuckDB data warehouse........")
    conn: duckdb.DuckDBPyConnection = duckdb.connect(str(DW_FILE))

    LOG.info("Created conn: a DuckDB connection object")
    LOG.info("CALL a function to delete tables in reverse order of creation")
    delete_tables(conn)

    LOG.info("CALL a function to create dim_customers........")
    LOG.info("PASS IN conn: the DuckDB connection object")
    create_dim_customers(conn)

    LOG.info("CALL a function to create dim_products........")
    LOG.info("PASS IN conn: the DuckDB connection object")
    create_dim_products(conn)

    LOG.info("CALL a function to create fact_sales........")
    LOG.info("PASS IN conn: the DuckDB connection object")
    create_fact_sales(conn)

    LOG.info("CALL a function to verify the schema........")
    LOG.info("PASS IN conn: the DuckDB connection object")
    verify_schema(conn)

    # Close the connection when done
    conn.close()

    LOG.info("Workflow 1-CREATE DW complete")
    LOG.info("========================")
    LOG.info("Executed successfully!")
    LOG.info("========================")


# === CONDITIONAL EXECUTION GUARD ===

if __name__ == "__main__":
    main()
