import os
import sys
import re
import unicodedata

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from typing import List

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
    CSVLoader,
    UnstructuredExcelLoader,
)
from langchain_core.documents import Document


class Utility:
    @staticmethod
    def read_file_content(file_path: str) -> List[Document]:
        """
        Reads and returns the content of a local file using LangChain loaders.
        If the file exists locally, it is used directly.

        Supported file types: .pdf, .docx, .txt, .csv, .xls, .xlsx.
        """

        if file_path.startswith("/"):
            file_path = file_path.lstrip("/")

        # Check if the file exists locally.
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file extension and select the proper loader.
        extension = os.path.splitext(file_path)[1].lower()
        if extension == ".pdf":
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif extension == ".docx":
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
        elif extension == ".txt":
            loader = TextLoader(file_path)
            documents = loader.load()
        elif extension == ".csv":
            loader = CSVLoader(file_path)
            documents = loader.load()
        elif extension in [".xls", ".xlsx"]:
            loader = UnstructuredExcelLoader(file_path)
            documents = loader.load()
        elif extension == ".md":
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
            documents = [Document(page_content=text, metadata={"source": file_path})]
        else:
            raise ValueError(f"Unsupported file type: {extension}")

        return documents
    
    @staticmethod
    def clean_text(content: str, preserve_paragraphs: bool = False) -> str:
        """
        Cleans and normalizes text by removing control characters, normalizing Unicode,
        standardizing whitespace, and optionally preserving paragraph breaks.

        Args:
            content (str): The input text to clean.
            preserve_paragraphs (bool): If True, paragraph breaks (\n\n) are preserved.
                                        If False, all whitespace is flattened.

        Returns:
            str: The cleaned and normalized text.
        """
        # Remove control characters and zero-width spaces
        content = re.sub(r"[\x00-\x09\x0B-\x1F\x7F-\x9F\u200B\uFEFF]", "", content)

        # Unicode normalization
        content = unicodedata.normalize("NFKD", content)

        # Remove markdown symbols
        markdown_chars = r"[\\*_`~#>\[\]!\(\)\-]"  # Add more if needed
        content = re.sub(markdown_chars, "", content)

        if preserve_paragraphs:
            # Normalize paragraph breaks
            content = re.sub(
                r"\n\s*\n", "\n\n", content
            )  # Clean and standardize paragraph breaks
            content = re.sub(r"[ \t]+", " ", content)  # Collapse internal spaces/tabs
            content = re.sub(r" *\n *", "\n", content)  # Clean space around newlines
        else:
            # Flatten all whitespace into single spaces
            content = re.sub(r"\s+", " ", content)

        return content.strip()
