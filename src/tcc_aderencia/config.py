"""Project paths and settings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW = DATA / "raw"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
REFERENCE = DATA / "reference"
REPORTS = ROOT / "reports"

DEFAULT_TERRITORY_LEVEL = "rgi"  # região geográfica imediata (ADR-0002)
DEFAULT_CNCT_EDITION = 4  # ADR-0001 (proposta)
SEED = 20261118
