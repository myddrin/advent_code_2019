import pytest

from day_04.password_brute import PasswordBrute


def test_has_pair():
    pwd = PasswordBrute(min_value=0, max_value=999999)

    pwd.check_password('122345')
    with pytest.raises(RuntimeError, match='No matching digits'):
        pwd.check_password('123456')


def test_only_pairs():
    pwd = PasswordBrute(min_value=0, max_value=999999, only_pairs=True)

    pwd.check_password('112233')
    with pytest.raises(RuntimeError, match='No pair'):
        pwd.check_password('123444')
    pwd.check_password('111122')


def test_has_6_digits():
    pwd = PasswordBrute(min_value=0, max_value=15000000)

    pwd.check_password('122345')
    with pytest.raises(RuntimeError, match='Invalid length'):
        pwd.check_password('12567')
    with pytest.raises(RuntimeError, match='Invalid length'):
        pwd.check_password('123456789')


def test_within_range():
    pwd = PasswordBrute(min_value=122345, max_value=122346)

    pwd.check_password('122345')  # inclusive lower bound
    with pytest.raises(RuntimeError, match='Not in range'):
        pwd.check_password('122344')
    with pytest.raises(RuntimeError, match='Not in range'):
        pwd.check_password('122347')
    pwd.check_password('122346')  # inclusive upper bound


def test_never_decrease():
    pwd = PasswordBrute(min_value=0, max_value=999999)

    pwd.check_password('122345')
    with pytest.raises(RuntimeError, match='Not increasing'):
        pwd.check_password('543221')

    with pytest.raises(RuntimeError, match='Not increasing'):
        pwd.check_password('646999')


@pytest.mark.parametrize('pwd_str', (
    '111111',
))
def test_some_valid_passwords(pwd_str):
    pwd = PasswordBrute(min_value=0, max_value=999999)
    pwd.check_password(pwd_str)


@pytest.mark.parametrize('pwd_str', (
    '223450',
    '123789',
))
def test_some_invalid_passwords(pwd_str):
    pwd = PasswordBrute(min_value=0, max_value=999999)
    with pytest.raises(RuntimeError):
        pwd.check_password(pwd_str)
