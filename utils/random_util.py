import random
import string
import os


class RandomUtil:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_random_string(length=5):
        if type(length) is int and 0 < length < 53:
            return ''.join(random.sample(string.ascii_letters, length))
        raise ValueError("Invalid input!")

    @staticmethod
    def get_random_digit(length=5):
        if type(length) is int and 0 < length < 25:
            return int(''.join(str(i) for i in random.sample(range(0, 25), length)))
        raise ValueError("Invalid input!")

    @staticmethod
    def get_random_mix_string(length=5):
        if type(length) is int and 0 < length < 85:
            return ''.join(
                random.sample(r"AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz,./;'\"[]\`-=<>?:\{}|_+)(*&^%$#@!~",
                              length))
        raise ValueError("Invalid input!")

    @staticmethod
    def get_random_phone(length=10):
        if type(length) is int and 0 < length < 25:
            return int(''.join(str(i) for i in random.sample(range(0, 25), length)))
        raise ValueError("Invalid input!")

    @staticmethod
    def get_random_email(length=10):
        if type(length) is int and 0 < length < 63:
            return ''.join(random.sample(string.ascii_letters + string.digits, length)) + '@xxx.com'
        raise ValueError("Invalid input!")

    @staticmethod
    def get_random_array_item(given_array):
        if type(given_array) is list and len(given_array) > 0:
            return random.choice(given_array)
        raise ValueError("Invalid input!")


if __name__ == "__main__":
    print(RandomUtil.get_random_string(20))
    print(os.getcwd())
