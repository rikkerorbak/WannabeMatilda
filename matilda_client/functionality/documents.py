"""
Service User Documents client for Matilda Platform.

Handles document attachments for service users.
Endpoints:
- GET    /v1/organization/{organization}/service-user/{serviceUserId}/document
- POST   /v1/organization/{organization}/service-user/{serviceUserId}/document
- DELETE /v1/organization/{organization}/service-user/{serviceUserId}/document/{documentId}
"""

from pathlib import Path
from typing import Any, BinaryIO

import httpx

from matilda_client.client import MatildaClient
from matilda_client.models import ServiceUserDocumentResponse


class ServiceUserDocumentsClient:
    """
    Client for Service User Document attachments in Matilda Platform.

    IMPORTANT: Do not instantiate directly. Use MatildaClientManager:
        matilda = MatildaClientManager(...)
        docs = matilda.documents.get_documents(service_user_id="...")
    """

    BASE_ENDPOINT = "/v1/organization/{organization}/service-user/{serviceUserId}/document"
    DELETE_ENDPOINT = "/v1/organization/{organization}/service-user/{serviceUserId}/document/{documentId}"

    def __init__(self, matilda_client: MatildaClient):
        self.client = matilda_client

    def get_documents(self, service_user_id: str) -> list[dict[str, Any]]:
        """
        Get all documents associated with a service user.

        :param service_user_id: ID of the service user.
        :return: List of document metadata dictionaries.
        """
        endpoint = self.BASE_ENDPOINT.replace("{serviceUserId}", str(service_user_id))
        response = self.client.get(endpoint)
        return response.json()

    def get_documents_typed(self, service_user_id: str) -> list[ServiceUserDocumentResponse]:
        """
        Get all documents associated with a service user parsed into ServiceUserDocumentResponse.
        """
        docs = self.get_documents(service_user_id)
        return [ServiceUserDocumentResponse.from_dict(d) for d in docs]

    def upload_document(
        self,
        service_user_id: str,
        file: str | Path | bytes | BinaryIO,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> str:
        """
        Upload a document for a service user.

        :param service_user_id: ID of the service user.
        :param file: File path (str/Path), raw bytes, or opened binary file object.
        :param filename: Optional custom filename. If file is a path, basename is used by default.
        :param content_type: Optional MIME type (e.g. 'application/pdf').
        :return: Document ID or response string returned by server.
        """
        endpoint = self.BASE_ENDPOINT.replace("{serviceUserId}", str(service_user_id))

        if isinstance(file, (str, Path)):
            file_path = Path(file)
            actual_filename = filename or file_path.name
            with open(file_path, "rb") as f:
                content = f.read()
            files = {"file": (actual_filename, content, content_type or "application/octet-stream")}
        elif isinstance(file, bytes):
            actual_filename = filename or "document.bin"
            files = {"file": (actual_filename, file, content_type or "application/octet-stream")}
        else:
            actual_filename = filename or getattr(file, "name", "document.bin")
            files = {"file": (actual_filename, file, content_type or "application/octet-stream")}

        response = self.client.post(endpoint, files=files)
        try:
            return response.json()
        except Exception:
            return response.text.strip()

    def delete_document(self, service_user_id: str, document_id: str) -> bool:
        """
        Delete a document belonging to a service user.

        :param service_user_id: ID of the service user.
        :param document_id: ID of the document to delete.
        :return: True if deleted successfully, False if document was not found (404).
        """
        endpoint = (
            self.DELETE_ENDPOINT.replace("{serviceUserId}", str(service_user_id)).replace(
                "{documentId}", str(document_id)
            )
        )
        try:
            response = self.client.delete(endpoint)
            return response.status_code in (200, 204)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise

    # Danish / Nordic aliases (matching nexus-client style)
    hent_dokumenter = get_documents
    upload_dokument = upload_document
    slet_dokument = delete_document


# Class aliases
DocumentClient = ServiceUserDocumentsClient
DokumentClient = ServiceUserDocumentsClient
