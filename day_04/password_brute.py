from typing import List


class PasswordBrute:

    def __init__(self, min_value=123257, max_value=647015, exp_length=6, only_pairs=False):
        self._valid = []
        self._range = (min_value, max_value)
        self._exp_length = exp_length
        self._only_pairs = only_pairs

    def check_password(self, password_str):
        # type: (str) -> None
        # - It is a six-digit number.
        # - The value is within the range given in your puzzle input.
        # - Two adjacent digits are the same (like 22 in 122345).
        # - Going from left to right, the digits never decrease; they only ever increase or stay the same
        # (like 111123 or 135679).

        password_int = int(password_str)
        if len(password_str) != self._exp_length:
            raise RuntimeError('Invalid length')

        if not (self._range[0] <= password_int <= self._range[1]):
            raise RuntimeError('Not in range')

        # Check for never decreasing and pair

        previous = int(password_str[0])
        current_cluster = password_str[0]
        digit_clusters = []  # type: List[int]

        for character in password_str[1:]:
            current = int(character)
            if current == previous:
                current_cluster += character
            else:
                if len(current_cluster) >= 2:
                    digit_clusters.append(len(current_cluster))
                current_cluster = character

            if current < previous:
                raise RuntimeError('Not increasing')
            previous = current

        if len(current_cluster) >= 2:
            digit_clusters.append(len(current_cluster))

        if self._only_pairs:
            if 2 not in digit_clusters:
                raise RuntimeError('No pair')
        elif not digit_clusters:
            raise RuntimeError('No matching digits')

    def is_valid_password(self, password_str):
        # type: (str) -> bool
        try:
            self.check_password(password_str)
            return True
        except RuntimeError as e:
            return False

    def _gen_pwd(self):
        for pwd in range(self._range[0], self._range[1] + 1):
            # This is in case the range will need 0s but the count would then be wrong
            # yield ('{:0%sd}' % self._exp_length).format(pwd)
            yield str(pwd)

    def brute_force(self):
        return {
            pwd_str
            for pwd_str in self._gen_pwd()
            if self.is_valid_password(pwd_str)
        }


if __name__ == '__main__':
    any_cluster = PasswordBrute(123257, 647015)

    valid_passwords = list(any_cluster.brute_force())
    print(f'Found {len(valid_passwords)} passwords with any cluster')  # 2220

    only_pairs = PasswordBrute(123257, 647015, only_pairs=True)
    valid_passwords = list(only_pairs.brute_force())
    print(f'Found {len(valid_passwords)} passwords with only pairs')  # 1316 is too low
