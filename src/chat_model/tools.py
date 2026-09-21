import arxiv
from pathlib import Path
import requests
from urllib.parse import urlparse

from langchain_core.tools import tool


@tool
def search_arxiv(topic: str, max_results: int = 5) -> list[dict]:
    """Search arXiv for research papers related to a topic."""

    try:
        client = arxiv.Client()

        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        papers = []

        for result in client.results(search):
            papers.append({
                "title": result.title,
                "updated": result.updated.date().isoformat(),
                "abstract": result.summary,
                "pdf_url": result.pdf_url,
            })

        return papers

    except Exception as exc:
        raise RuntimeError(
            f"Failed to search arXiv: {exc}"
        ) from exc


@tool
def download_pdf(url: str, output_dir: str = "papers") -> str:
    """Download a PDF from a URL and return the local file path."""

    try:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError("Invalid PDF URL.")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = parsed_url.path.rstrip("/").split("/")[-1]

        if not filename:
            raise ValueError("Could not determine a filename from the URL.")

        if not filename.endswith(".pdf"):
            filename += ".pdf"

        output_path = output_dir / filename

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(response.content)

        return str(output_path)

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Failed to download PDF: {exc}"
        ) from exc

    except OSError as exc:
        raise RuntimeError(
            f"Failed to save PDF: {exc}"
        ) from exc


chat_tools = [search_arxiv, download_pdf]