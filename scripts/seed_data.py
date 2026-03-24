"""Seed sample UPS devices into database."""

from ups_guardian.core.config import load_config
from ups_guardian.data.device_repository import DeviceRepository
from ups_guardian.utils.paths import bundled_seed_csv_path, user_config_path

if __name__ == "__main__":
    cfg = load_config(user_config_path())
    repo = DeviceRepository(cfg.database_path)
    inserted = repo.import_csv(str(bundled_seed_csv_path()))
    print(f"Inserted {inserted} devices")
