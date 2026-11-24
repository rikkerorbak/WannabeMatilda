"""
Unit tests for ServiceUserDocumentsClient functionality.
"""

from matilda_client.models import ServiceUserDocumentResponse


def test_get_documents(manager):
    docs = manager.documents.get_documents("usr-uuid-1234")
    assert len(docs) == 2
    assert docs[0]["name"] == "DietaryRequirements.pdf"
    assert docs[0]["documentId"] == "doc-001"


def test_get_documents_typed(manager):
    docs = manager.documents.get_documents_typed("usr-uuid-1234")
    assert len(docs) == 2
    assert isinstance(docs[0], ServiceUserDocumentResponse)
    assert docs[0].name == "DietaryRequirements.pdf"
    assert docs[0].documentId == "doc-001"


def test_upload_document_bytes(manager):
    doc_id = manager.documents.upload_document(
        service_user_id="usr-uuid-1234",
        file=b"%PDF-1.4 dummy pdf bytes",
        filename="test.pdf",
        content_type="application/pdf",
    )
    assert "doc-new-123" in str(doc_id)


def test_delete_document_success(manager):
    res = manager.documents.delete_document("usr-uuid-1234", "doc-001")
    assert res is True


def test_delete_document_not_found(manager):
    res = manager.documents.delete_document("usr-uuid-1234", "doc-not-found")
    assert res is False


def test_documents_danish_aliases(manager):
    docs = manager.dokumenter.hent_dokumenter("usr-uuid-1234")
    assert len(docs) == 2
