from jobreach.safety.send_scheduler import in_send_window, schedule_times
from jobreach.config.settings import AppSettings


def test_in_send_window_default_hours():
    settings = AppSettings(send_window_start="00:00", send_window_end="23:59")
    assert in_send_window(settings) is True


def test_schedule_times_spreads():
    settings = AppSettings(send_delay_seconds=60)
    times = schedule_times(4, 2, settings)
    assert len(times) == 4
