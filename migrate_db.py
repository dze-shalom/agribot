"""
Database Migration Script
Exports data from SQLite and imports to PostgreSQL on Render
"""
import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

def migrate_database(source_db_path, target_db_url):
    """Migrate data from SQLite to PostgreSQL"""

    print(f"Source: {source_db_path}")
    print(f"Target: {target_db_url[:50]}...")

    # Create engines
    source_engine = create_engine(f'sqlite:///{source_db_path}')
    target_engine = create_engine(target_db_url)

    # Get metadata from source
    source_metadata = MetaData()
    source_metadata.reflect(bind=source_engine)

    print(f"\nFound {len(source_metadata.tables)} tables:")
    for table_name in source_metadata.tables.keys():
        print(f"  - {table_name}")

    # Create sessions
    SourceSession = sessionmaker(bind=source_engine)
    TargetSession = sessionmaker(bind=target_engine)

    source_session = SourceSession()
    target_session = TargetSession()

    try:
        # Create all tables in target database
        print("\nCreating tables in target database...")
        from app.main import create_app
        app = create_app()
        with app.app_context():
            from app.extensions import db as target_db
            target_db.create_all()
        print("✓ Tables created")

        # Migrate data for each table
        print("\nMigrating data...")
        for table_name, table in source_metadata.tables.items():
            # Skip alembic version table
            if table_name == 'alembic_version':
                continue

            # Get all rows from source
            source_rows = source_session.execute(table.select()).fetchall()

            if source_rows:
                print(f"\n{table_name}: {len(source_rows)} rows")

                # Insert into target
                for row in source_rows:
                    row_dict = dict(row._mapping)
                    target_session.execute(table.insert().values(**row_dict))

                target_session.commit()
                print(f"  ✓ Migrated {len(source_rows)} rows")
            else:
                print(f"\n{table_name}: 0 rows (skipped)")

        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        target_session.rollback()
        raise
    finally:
        source_session.close()
        target_session.close()

if __name__ == "__main__":
    # Get database paths
    source_db = input("Enter path to SQLite database (or press Enter for 'instance/agribot.db'): ").strip()
    if not source_db:
        source_db = "instance/agribot.db"

    if not os.path.exists(source_db):
        print(f"❌ Error: Database file not found: {source_db}")
        sys.exit(1)

    print("\nTo get your PostgreSQL connection string from Render:")
    print("1. Go to https://dashboard.render.com/")
    print("2. Click on your 'agribot-db' database")
    print("3. Copy the 'Internal Database URL' (starts with postgresql://)")
    print()

    target_db_url = input("Enter PostgreSQL connection string from Render: ").strip()

    if not target_db_url.startswith('postgresql://'):
        print("❌ Error: Invalid PostgreSQL URL. Must start with 'postgresql://'")
        sys.exit(1)

    # Confirm migration
    print("\n⚠️  WARNING: This will overwrite data in the production database!")
    confirm = input("Type 'yes' to proceed: ").strip().lower()

    if confirm != 'yes':
        print("Migration cancelled.")
        sys.exit(0)

    # Run migration
    migrate_database(source_db, target_db_url)
