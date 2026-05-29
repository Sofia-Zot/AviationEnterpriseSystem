
import bcrypt


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt.

    Args:
        password: Пароль в виде строки.

    Returns:
        str: Хеш пароля в виде строки.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Проверяет пароль против хеша.

    Args:
        password: Пароль в виде строки.
        hashed: Хеш пароля в виде строки.

    Returns:
        bool: True если пароль верный, False иначе.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
