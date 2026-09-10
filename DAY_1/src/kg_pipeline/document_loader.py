from pathlib import Path

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


def load_documents(reference_dir: str | Path) -> list[Document]:
    reference_dir = Path(reference_dir)
    loader = DirectoryLoader(
        str(reference_dir),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=False,
    )
    return loader.load()
