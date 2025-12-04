# Mouse Oscillator

- 需求：按下鼠标侧键，让鼠标在 Y 轴快速上下小幅度平移；幅度和速度可配置。

- 安装：
  - `python3 -m venv .venv && source .venv/bin/activate`
  - `pip install -r requirements.txt`
  - 在系统偏好设置中授予终端/IDE 的“辅助功能”权限。

- 运行：
  - `python mouse_oscillator.py` 默认读取 `config.json`
- GUI：`python mouse_oscillator_gui.py` 打开界面，支持开始/停止与配置编辑保存
  - 参数覆盖：
    - `--amplitude <pixels>` 振幅像素，默认 `12`
    - `--frequency <hz>` 频率，默认 `20`
    - `--key <char>` 触发键，默认 `x`
    - `--toggle` 切换模式（按一次开始，再按一次停止）

- 配置：见 `config.json`

- 用法：
  - 非切换模式：按住键盘 `x` 键时振动，松开停止。
  - 切换模式：按一次 `x` 开始，按一次 `x` 停止。
  - GUI：点击 `Start` 进入“武装”状态，全局按住触发键（默认 `x`）即可抖动；`Stop` 解除武装并停止；`Apply` 更新当前武装参数；`Save Config` 保存到 `config.json`；`Load Config` 重新加载。

- 说明：
  - 依赖 `pynput`，首次运行可能需要系统“辅助功能/输入监控”权限。
  - GUI 的全局快捷键需要在`系统设置 → 隐私与安全 → 输入监控`为终端/IDE或Python授权；未授权时会提示并不崩溃。
  - 触发键默认是 `x`，可通过参数或配置调整为任意字符键。
