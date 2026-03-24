"""Initialize database schema."""

from ups_guardian.core.config import load_config
from ups_guardian.data.db import init_schema
from ups_guardian.utils.paths import bundled_config_schema_path, user_config_path

if __name__ == "__main__":
    cfg = load_config(user_config_path())
    init_schema(cfg.database_path, str(bundled_config_schema_path()))
    print(f"Initialized database: {cfg.database_path}")
