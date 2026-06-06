import time


def wait_between_sends(delay_seconds: int) -> None:
    if delay_seconds > 0:
        time.sleep(delay_seconds)
