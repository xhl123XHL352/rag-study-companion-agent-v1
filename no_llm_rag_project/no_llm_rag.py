from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np


@dataclass
class Chunk:
    content: str
    source: str
    index: int


class NoLLMRAG:
    def __init__(
        self,
        client,
        embedding_model: str,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

        self.client = client
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.chunks: list[Chunk] = []
        self.embeddings: np.ndarray | None = None

    def _split_text(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        step = self.chunk_size - self.chunk_overlap
        chunks = []
        for start in range(0, len(text), step):
            chunk = text[start:start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break
        return chunks

    def load_documents(self, docs_dir: Union[str, Path]) -> None:
        docs_dir = Path(docs_dir)
        if not docs_dir.is_dir():
            raise NotADirectoryError(f"Not a directory: {docs_dir}")

        self.chunks = []
        self.embeddings = None

        for path in docs_dir.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
                continue

            content = path.read_text(encoding="utf-8")
            for text in self._split_text(content):
                self.chunks.append(
                    Chunk(
                        content=text,
                        source=path.name,
                        index=len(self.chunks),
                    )
                )

    def create_embeddings(self) -> None:
        if not self.chunks:
            self.embeddings = None
            return

        all_embeddings = []
        batch_size = 10
        texts = [chunk.content for chunk in self.chunks]

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch,
            )
            all_embeddings.extend(item.embedding for item in response.data)

        self.embeddings = np.array(all_embeddings, dtype=np.float32)

    def save_index(self, index_path: Union[str, Path]) -> None:
        if self.embeddings is None:
            raise ValueError("No embeddings found. Call create_embeddings() first.")

        index_path = Path(index_path)
        index_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            index_path,
            embeddings=self.embeddings,
            chunks_content=np.array([chunk.content for chunk in self.chunks], dtype=object),
            chunks_source=np.array([chunk.source for chunk in self.chunks], dtype=object),
            chunks_index=np.array([chunk.index for chunk in self.chunks], dtype=np.int32),
        )

    def load_index(self, index_path: Union[str, Path]) -> None:
        index_path = Path(index_path)
        if not index_path.exists():
            raise FileNotFoundError(f"Index file not found: {index_path}")

        data = np.load(index_path, allow_pickle=True)
        self.embeddings = data["embeddings"].astype(np.float32)
        self.chunks = [
            Chunk(
                content=str(data["chunks_content"][i]),
                source=str(data["chunks_source"][i]),
                index=int(data["chunks_index"][i]),
            )
            for i in range(len(data["chunks_content"]))
        ]

    @staticmethod
    def _cosine_similarity(query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
        query_norm = np.linalg.norm(query_embedding)
        document_norms = np.linalg.norm(document_embeddings, axis=1)
        denominator = query_norm * document_norms
        denominator = np.where(denominator == 0, 1e-12, denominator)
        return np.dot(document_embeddings, query_embedding) / denominator

    def search(self, query: str, top_k: int = 3) -> list[tuple[Chunk, float]]:
        if self.embeddings is None:
            raise ValueError("No embeddings found. Build or load index first.")
        if not query.strip() or top_k <= 0:
            return []

        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=[query],
        )
        query_embedding = np.array(response.data[0].embedding, dtype=np.float32)

        scores = self._cosine_similarity(query_embedding, self.embeddings)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices]

    def format_results(self, results: list[tuple[Chunk, float]]) -> str:
        if not results:
            return "未检索到相关知识片段。"

        return "\n\n".join(
            f"片段{i + 1}\n来源：{chunk.source}\n相似度：{score:.4f}\n内容：\n{chunk.content}"
            for i, (chunk, score) in enumerate(results)
        )


def load_or_build_no_llm_rag(
    client,
    embedding_model: str,
    docs_dir: Union[str, Path],
    index_path: Union[str, Path],
) -> NoLLMRAG:
    rag = NoLLMRAG(client=client, embedding_model=embedding_model)
    index_path = Path(index_path)

    if index_path.exists():
        print(f"[RAG] 加载索引: {index_path}")
        rag.load_index(index_path)
    else:
        print(f"[RAG] 未找到索引，开始读取知识库并创建 embedding: {index_path}")
        rag.load_documents(docs_dir)
        rag.create_embeddings()
        rag.save_index(index_path)
        print(f"[RAG] 索引构建完成: {index_path}")

    return rag
