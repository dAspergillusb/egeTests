from random import choice
from string import printable

def gen_password() -> str:
    alphabet: str = printable[:72]
    print(alphabet)
    password: list[str] = []
    for _ in range(10):
        password.append(choice(alphabet))
    return "".join(password)


if __name__ == '__main__':
    for _ in range(19):
        print(gen_password())