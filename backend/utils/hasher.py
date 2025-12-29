from passlib.context import CryptContext

hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hash(item: str) -> str:
    return hasher.hash(item)


def match_hash(item: str, item_hash: str) -> bool:
    return hasher.verify(item, item_hash)
