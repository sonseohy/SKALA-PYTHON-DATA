from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Config:
    data_path: Path = BASE_DIR / 'data' / 'sales_raw.csv'
    output_dir: Path = BASE_DIR / 'output'
    template_dir: Path = BASE_DIR / 'templates'
    top_n: int = 10
    title: str = '매출 리포트'


CONFIG = Config()
