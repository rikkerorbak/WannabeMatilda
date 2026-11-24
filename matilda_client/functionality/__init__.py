"""
Functionality modules for Matilda Platform Client.
"""

from .documents import ServiceUserDocumentsClient
from .parties import PartiesClient
from .service_users import ServiceUsersClient

__all__ = [
    "PartiesClient",
    "ServiceUserDocumentsClient",
    "ServiceUsersClient",
]
