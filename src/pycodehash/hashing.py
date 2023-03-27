# Functionality to hash the function body
import hashlib


def hash_string(input_string: str) -> str:
    """SHA256 hash of input string

    Args:
        input_string: the string to hash

    Returns:
        SHA256 hashed string
    """
    return hashlib.sha256(input_string.encode("utf-8")).hexdigest()
