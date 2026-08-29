"""AI短视频自动化制作 - ModelScope 创空间入口

ModelScope 创空间(Studio)默认在仓库根目录加载 app.py。
本文件作为入口转发器，加载 web/app.py 的 Streamlit 应用。
"""

import runpy
from pathlib import Path

_APP_PATH = Path(__file__).parent / "web" / "app.py"

runpy.run_path(str(_APP_PATH), run_name="__main__")
