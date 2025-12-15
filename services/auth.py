# services/auth.py
# Simple user verification module

# Example: simple list of allowed UIDs
AUTHORIZED_UIDS = [
    "DE:AD:BE:EF",
    "12:34:56:78",
]

def is_authorized(uid: str) -> bool:
    """Check if a UID is authorized."""
    return uid in AUTHORIZED_UIDS
