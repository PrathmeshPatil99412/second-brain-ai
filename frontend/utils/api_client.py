"""
Centralized HTTP client for talking to the FastAPI backend.
Every Streamlit page imports from here instead of calling `requests`
directly — keeps the base URL and error handling in one place.
"""
import requests

BASE_URL = "http://127.0.0.1:8000/api/v1"


def upload_document(file) -> dict:
    files = {"file": (file.name, file.getvalue(), file.type)}
    response = requests.post(f"{BASE_URL}/documents/upload", files=files)
    response.raise_for_status()
    return response.json()


def create_note(title: str, content: str, folder: str | None) -> dict:
    payload = {"title": title, "content": content, "folder": folder}
    response = requests.post(f"{BASE_URL}/notes", json=payload)
    response.raise_for_status()
    return response.json()


def chat_query(query: str, chat_history: list[dict]) -> dict:
    payload = {"query": query, "chat_history": chat_history}
    response = requests.post(f"{BASE_URL}/chat/query", json=payload)
    response.raise_for_status()
    return response.json()


def semantic_search(query: str, top_k: int = 5) -> dict:
    payload = {"query": query, "top_k": top_k}
    response = requests.post(f"{BASE_URL}/search", json=payload)
    response.raise_for_status()
    return response.json()


def list_documents() -> dict:
    response = requests.get(f"{BASE_URL}/documents")
    response.raise_for_status()
    return response.json()


def get_document(document_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/documents/{document_id}")
    response.raise_for_status()
    return response.json()


def delete_document(document_id: str) -> dict:
    response = requests.delete(f"{BASE_URL}/documents/{document_id}")
    response.raise_for_status()
    return response.json()


def summarize_document(document_id: str) -> dict:
    response = requests.post(f"{BASE_URL}/summary/{document_id}")
    response.raise_for_status()
    return response.json()


def get_dashboard_stats() -> dict:
    response = requests.get(f"{BASE_URL}/dashboard")
    response.raise_for_status()
    return response.json()