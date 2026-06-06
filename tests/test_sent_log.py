from jobreach.logs.sent_log import SentLog


def test_sent_log_records_and_detects(tmp_path):
    log = SentLog(tmp_path / "sent.csv")
    assert not log.has_been_sent("a@example.com", "Hello")
    log.record_sent("a@example.com", "Hello", "1", "msg")
    assert log.has_been_sent("a@example.com", "Hello")
