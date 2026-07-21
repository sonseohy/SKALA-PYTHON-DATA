from dataclasses import dataclass
from pathlib import Path

class Config:
    data_path: Path = Path('data/sales_raw.csv')
    output_dir: Path = Path('output')
    top_n: int = 10
CONFIG = Config()
