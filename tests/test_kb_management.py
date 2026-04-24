from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_kb_upload_list_reindex_and_delete() -> None:
    content = b"# Refund Policy\n\nIf a customer requests a refund, support should review the case."

    upload_response = client.post(
        "/kb/upload",
        files={"file": ("refund_policy_test.md", content, "text/markdown")},
    )

    assert upload_response.status_code == 200
    uploaded = upload_response.json()
    document_id = uploaded["id"]
    assert uploaded["filename"] == "refund_policy_test.md"

    list_response = client.get("/kb/documents")
    assert list_response.status_code == 200
    docs = list_response.json()
    assert any(doc["id"] == document_id for doc in docs)

    reindex_response = client.post("/kb/reindex")
    assert reindex_response.status_code == 200
    reindex_payload = reindex_response.json()
    assert reindex_payload["document_count"] >= 1
    assert reindex_payload["chunk_count"] >= 1

    delete_response = client.delete(f"/kb/documents/{document_id}")
    assert delete_response.status_code == 200

    list_after_delete = client.get("/kb/documents")
    assert list_after_delete.status_code == 200
    docs_after_delete = list_after_delete.json()
    assert not any(doc["id"] == document_id for doc in docs_after_delete)


def test_kb_upload_rejects_unsupported_file_type() -> None:
    response = client.post(
        "/kb/upload",
        files={"file": ("bad.pdf", b"%PDF fake", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Unsupported KB file type" in response.json()["detail"]