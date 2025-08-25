import os
from app.config import settings
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore


class VannaService(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None) -> None:
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)


def get_vanna_instance() -> VannaService:
    """Get configured Vanna instance."""
    cdir = os.getcwd()
    vn = VannaService(
        config={
            "model": settings.model_name,
            "path": os.path.join(cdir, settings.chroma_folder),
        }
    )

    vn.connect_to_sqlite(settings.sqlite_path)
    return vn


vanna = get_vanna_instance()
