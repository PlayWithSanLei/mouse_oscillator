# 鼠标上下振动工具

- 功能：按下快捷键，让鼠标在 Y 轴快速上下小幅度平移；振幅与频率可配置；支持“按住生效”和“切换模式”。

- 安装：
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - 在系统设置中为终端/IDE开启“辅助功能”和“输入监控”权限。

- 运行：
  - 命令行：`python mouse_oscillator.py`（默认读取 `config.json`）
  - 图形界面：`python mouse_oscillator_gui.py`（支持开始/停止、参数编辑与保存）
  - 参数覆盖：
    - `--amplitude <pixels>` 振幅像素，默认 `12`
    - `--frequency <hz>` 频率，默认 `20`
    - `--key <char>` 触发键，默认 `x`
    - `--toggle` 切换模式（按一次开始，再按一次停止）

- 配置：`config.json`
  - `amplitude_pixels`：振幅（像素）
  - `frequency_hz`：频率（Hz）
  - `trigger_key`：触发键（如 `x`）
  - `toggle_mode`：是否启用切换模式

- 用法：
  - 非切换模式：按住触发键时振动，松开停止。
  - 切换模式：按一次开始，再按一次停止。
  - 图形界面：点击“开始武装”进入武装状态，全局按住触发键即可抖动；“解除武装”停止；“应用参数”更新当前武装参数；“保存配置”写入 `config.json`；“加载配置”重新载入。

- 权限说明：
  - 依赖 `pynput`，首次运行可能需要系统“辅助功能/输入监控”权限。
  - 全局快捷键需在`系统设置 → 隐私与安全 → 输入监控`为终端/IDE或Python授权；未授权时界面会弹窗提示而不会崩溃。
  - 触发键默认是 `x`，可通过参数或配置调整为任意字符键。
