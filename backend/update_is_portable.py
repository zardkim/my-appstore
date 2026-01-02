"""
Update is_portable field for existing versions based on filename analysis
"""
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.version import Version
from app.models.product import Product
from app.core.parser import FilenameParser


def update_existing_versions():
    """Update is_portable for all existing versions"""
    db: Session = SessionLocal()
    parser = FilenameParser()

    try:
        # Get all versions
        versions = db.query(Version).all()

        print(f"Found {len(versions)} versions to update...")
        updated_count = 0

        for version in versions:
            try:
                # Get parent folder name for better context
                parent_folder = ""
                if version.product:
                    folder_path = Path(version.product.folder_path)
                    parent_folder = folder_path.name

                # Parse filename to detect portable status
                parsed = parser.parse(version.file_name, parent_folder)
                is_portable = parsed.get('is_portable', False)

                # Update only if value changed
                if version.is_portable != is_portable:
                    version.is_portable = is_portable
                    updated_count += 1
                    print(f"  Updated: {version.file_name} -> is_portable={is_portable}")

            except Exception as e:
                print(f"  Error processing {version.file_name}: {e}")
                continue

        # Commit all changes
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} versions!")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting is_portable field update...\n")
    update_existing_versions()
    print("\nDone!")
