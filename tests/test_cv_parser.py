from jobreach.cv.parser import parse_cv


def test_parse_txt_cv(tmp_path):
    path = tmp_path / "resume.txt"
    path.write_text("Hello   world\n\n\nPython", encoding="utf-8")
    assert parse_cv(str(path)) == "Hello world\n\nPython"
