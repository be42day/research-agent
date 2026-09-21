from unittest.mock import MagicMock, patch

import pytest

from chat_model.tools import download_pdf, search_arxiv


def test_search_arxiv():
    fake_result = MagicMock()

    fake_result.title = "Test Paper"
    fake_result.updated.date.return_value.isoformat.return_value = "2026-01-01"
    fake_result.summary = "Test abstract"
    fake_result.pdf_url = "https://example.com/test.pdf"

    fake_client = MagicMock()
    fake_client.results.return_value = [fake_result]

    with patch(
        "chat_model.tools.arxiv.Client",
        return_value=fake_client,
    ):
        result = search_arxiv.invoke({
            "topic": "physics informed neural networks",
            "max_results": 1,
        })

    assert len(result) == 1
    assert result[0]["title"] == "Test Paper"
    assert result[0]["pdf_url"] == "https://example.com/test.pdf"


def test_search_arxiv_failure():
    fake_client = MagicMock()
    fake_client.results.side_effect = Exception("arXiv API error")

    with patch(
        "chat_model.tools.arxiv.Client",
        return_value=fake_client,
    ):
        with pytest.raises(Exception, match="arXiv API error"):
            search_arxiv.invoke({
                "topic": "test",
                "max_results": 1,
            })


def test_download_pdf(tmp_path):
    fake_response = MagicMock()

    fake_response.content = b"%PDF-test-content"
    fake_response.raise_for_status.return_value = None

    with patch(
        "chat_model.tools.requests.get",
        return_value=fake_response,
    ):
        result = download_pdf.invoke({
            "url": "https://example.com/test.pdf",
            "output_dir": str(tmp_path),
        })

    output_file = tmp_path / "test.pdf"

    assert result == str(output_file)
    assert output_file.exists()
    assert output_file.read_bytes() == b"%PDF-test-content"


def test_download_pdf_failure(tmp_path):
    fake_response = MagicMock()

    fake_response.raise_for_status.side_effect = Exception(
        "404 Not Found"
    )

    with patch(
        "chat_model.tools.requests.get",
        return_value=fake_response,
    ):
        with pytest.raises(Exception, match="404 Not Found"):
            download_pdf.invoke({
                "url": "https://example.com/missing.pdf",
                "output_dir": str(tmp_path),
            })