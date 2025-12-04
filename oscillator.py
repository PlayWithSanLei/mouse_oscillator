class Oscillator:
    def __init__(self, center_y: int, amplitude: int, frequency_hz: float):
        self.center_y = center_y
        self.amplitude = amplitude
        self.frequency_hz = frequency_hz

    def position_at(self, t_seconds: float) -> int:
        phase = (t_seconds * self.frequency_hz) % 1.0
        return int(self.center_y + (self.amplitude if phase < 0.5 else -self.amplitude))

    def offset_at(self, t_seconds: float) -> int:
        phase = (t_seconds * self.frequency_hz) % 1.0
        return int(self.amplitude if phase < 0.5 else -self.amplitude)

    def top(self) -> int:
        return int(self.center_y + self.amplitude)

    def bottom(self) -> int:
        return int(self.center_y - self.amplitude)
