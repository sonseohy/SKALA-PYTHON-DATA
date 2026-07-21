from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
def render(data: dict, cfg) -> Path:
    env = Environment(loader=FileSystemLoader('templates'))
    tpl = env.get_template('report.html')
    html = tpl.render(
        title=cfg.title,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        **data,
    )
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    # ★ 타임스탬프를 파일명에 → 이전 리포트가 안 지워짐
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = cfg.output_dir / f'report_{stamp}.html'
    out.write_text(html, encoding='utf-8')
    return out
