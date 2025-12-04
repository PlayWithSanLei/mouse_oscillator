# Mouse Oscillator

- 需求：按下鼠标侧键，让鼠标在 Y 轴快速上下小幅度平移；幅度和速度可配置。

- 安装：
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - 在系统偏好设置中授予终端/IDE 的“辅助功能”权限。

- 运行：
  - `python mouse_oscillator.py` 默认读取 `config.json`
  - 参数覆盖：
    - `--amplitude <pixels>` 振幅像素，默认 `12`
    - `--frequency <hz>` 频率，默认 `20`
    - `--key <char>` 触发键，默认 `x`
    - `--toggle` 切换模式（按一次开始，再按一次停止）

- 配置：见 `config.json`

- 用法：
  - 非切换模式：按住键盘 `x` 键时振动，松开停止。
  - 切换模式：按一次 `x` 开始，按一次 `x` 停止。

- 说明：
  - 依赖 `pynput`，首次运行可能需要系统“辅助功能/输入监控”权限。
  - 触发键默认是 `x`，可通过参数或配置调整为任意字符键。
