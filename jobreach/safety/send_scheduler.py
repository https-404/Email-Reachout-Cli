from datetime import datetime, time, timedelta, timezone

from jobreach.config.settings import AppSettings


def parse_hhmm(value: str) -> time:
    hour, minute = value.split(":")
    return time(int(hour), int(minute))


def in_send_window(settings: AppSettings, now: datetime | None = None) -> bool:
    now = now or datetime.now()
    start = parse_hhmm(settings.send_window_start)
    end = parse_hhmm(settings.send_window_end)
    current = now.time()
    if start <= end:
        return start <= current <= end
    return current >= start or current <= end


def schedule_times(count: int, days: int, settings: AppSettings) -> list[str]:
    """Spread sends across days at send_window_start."""
    start = parse_hhmm(settings.send_window_start)
    per_day = max(1, count // days)
    times: list[str] = []
    base = datetime.now(timezone.utc).replace(hour=start.hour, minute=start.minute, second=0, microsecond=0)
    for index in range(count):
        day_offset = index // per_day
        scheduled = base + timedelta(days=day_offset, minutes=(index % per_day) * settings.send_delay_seconds // 60)
        times.append(scheduled.isoformat())
    return times


def today_sent_count(sent_log_rows: list[dict]) -> int:
    today = datetime.now(timezone.utc).date()
    count = 0
    for row in sent_log_rows:
        try:
            sent_date = datetime.fromisoformat(row["sent_at"].replace("Z", "+00:00")).date()
        except ValueError:
            continue
        if sent_date == today:
            count += 1
    return count
