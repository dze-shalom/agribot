"""
Database Migration Script - Automatic Version
Exports data from SQLite and imports to PostgreSQL on Render
"""
import os
import sys
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.orm import sessionmaker

def migrate_database(source_db_path, target_db_url):
    """Migrate data from SQLite to PostgreSQL"""

    print(f"Source: {source_db_path}")
    print(f"Target: {target_db_url[:50]}...")

    if not os.path.exists(source_db_path):
        print(f"Error: Database file not found: {source_db_path}")
        return False

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

        # Set environment to use PostgreSQL
        os.environ['DATABASE_URL'] = target_db_url
        os.environ['FLASK_ENV'] = 'production'

        from app.main import create_app
        app = create_app()
        with app.app_context():
            from database import db as target_db
            target_db.create_all()
        print("Tables created")

        # Migrate data for each table
        print("\nMigrating data...")

        # Order matters for foreign key constraints - users must come first
        table_order = ['users', 'conversations', 'messages', 'feedback', 'analytics_events',
                      'usage_analytics', 'error_logs', 'climate_data', 'geographic_data']

        for table_name in table_order:
            if table_name not in source_metadata.tables:
                continue

            table = source_metadata.tables[table_name]

            # Get all rows from source
            source_rows = source_session.execute(table.select()).fetchall()

            if source_rows:
                print(f"\n{table_name}: {len(source_rows)} rows")

                # Insert into target one row at a time
                success_count = 0
                for row in source_rows:
                    row_dict = dict(row._mapping)
                    try:
                        target_session.execute(table.insert().values(**row_dict))
                        target_session.commit()
                        success_count += 1
                    except Exception as e:
                        print(f"  WARNING: Skipping row due to error: {str(e)[:100]}")
                        target_session.rollback()
                        continue

                print(f"  OK: Migrated {success_count}/{len(source_rows)} rows")
            else:
                print(f"\n{table_name}: 0 rows (skipped)")

        # Handle remaining tables not in order list
        for table_name, table in source_metadata.tables.items():
            if table_name in table_order or table_name == 'alembic_version':
                continue

            source_rows = source_session.execute(table.select()).fetchall()

            if source_rows:
                print(f"\n{table_name}: {len(source_rows)} rows")
                success_count = 0
                for row in source_rows:
                    row_dict = dict(row._mapping)
                    try:
                        target_session.execute(table.insert().values(**row_dict))
                        target_session.commit()
                        success_count += 1
                    except Exception as e:
                        print(f"  WARNING: Skipping row due to error: {str(e)[:100]}")
                        target_session.rollback()
                        continue
                print(f"  OK: Migrated {success_count}/{len(source_rows)} rows")

        print("\nMigration completed successfully!")
        return True

    except Exception as e:
        print(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()
        target_session.rollback()
        return False
    finally:
        source_session.close()
        target_session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python migrate_db_auto.py <postgresql_url>")
        print("\nExample:")
        print('  python migrate_db_auto.py "postgresql://user:pass@host/dbname"')
        sys.exit(1)

    source_db = "instance/agribot.db"
    target_db_url = sys.argv[1]

    if not target_db_url.startswith('postgresql://'):
        print("Error: Invalid PostgreSQL URL. Must start with 'postgresql://'")
        sys.exit(1)

    print("WARNING: This will overwrite data in the production database!")
    print("Starting migration in 3 seconds... (Press Ctrl+C to cancel)")

    import time
    try:
        time.sleep(3)
    except KeyboardInterrupt:
        print("\nMigration cancelled.")
        sys.exit(0)

    # Run migration
    success = migrate_database(source_db, target_db_url)
    sys.exit(0 if success else 1)
