"""Google Drive/Docs service — create and manage HR documents."""

from googleapiclient.discovery import Resource


def create_document(docs: Resource, drive: Resource, title: str, content: str) -> dict:
    """
    Create a Google Doc with the given title and content.
    Returns the created document metadata including its URL.
    """
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]

    requests = [
        {
            "insertText": {
                "location": {"index": 1},
                "text": content,
            }
        }
    ]
    docs.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    file_meta = drive.files().get(
        fileId=doc_id, fields="id,name,webViewLink,createdTime"
    ).execute()

    return {
        "id": doc_id,
        "title": file_meta["name"],
        "url": file_meta["webViewLink"],
        "created": file_meta.get("createdTime", ""),
    }


def list_hr_documents(drive: Resource, max_results: int = 20) -> list[dict]:
    """List Google Docs in Drive, newest first."""
    results = drive.files().list(
        q="mimeType='application/vnd.google-apps.document'",
        pageSize=max_results,
        orderBy="createdTime desc",
        fields="files(id,name,webViewLink,createdTime)",
    ).execute()

    return results.get("files", [])


def format_document_list(docs_list: list[dict]) -> str:
    """Return a human-readable document list."""
    if not docs_list:
        return "No documents found."

    lines = []
    for doc in docs_list:
        created = doc.get("createdTime", "")[:10]
        lines.append(f"  • [{created}] {doc['name']}\n    {doc['webViewLink']}")

    return "\n".join(lines)
