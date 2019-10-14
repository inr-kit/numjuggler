import pytest
from numjuggler.utils.io import cd_temporarily
from six import StringIO
import numjuggler.likefunc as lf



@pytest.mark.parametrize("data, log, present, absent, expected_present_value, expected_absent_value, expected_text", [
    (
        """
            c 1: 12
            c 2: 14
        """,
        False,
        1, 3,
        12, 3,
        "",
    ),
    (
        """
            c 1: 12
            c 2: 14
        """,
        True,
        1, 3,
        12, 3,
        "cel 12: 1\ncel 3: 3\n",
    ),
])
def test_LikeFunction(
    data,
    log,
    present,
    absent,
    expected_present_value,
    expected_absent_value,
    expected_text
):
    input = StringIO(data)
    maps = lf.read_map_file(input, log)
    actual = StringIO()
    for k in maps:
        like_function = maps[k]
        assert like_function.log == log
        present_value = like_function(present)
        assert present_value == expected_present_value
        absent_value = like_function(absent)
        assert absent_value == expected_absent_value
        if log:
            like_function.write_log_as_map(k, actual)
        else:
            with pytest.raises(ValueError):
                like_function.write_log_as_map(k, actual)
    assert actual.getvalue() == expected_text
