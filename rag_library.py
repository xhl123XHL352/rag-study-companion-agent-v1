from dataclasses import dataclass
from pathlib import Path
from typing import Union

import numpy as np


@dataclass
class Chunk:
    content: str
    source: str
    index: int


class RAGLibrary:
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

    def _split_by_separator(self, text: str, separator: str) -> list[str]:
        if separator == "":
            return list(text)
        return [part for part in text.split(separator) if part.strip()]

    def _fallback_split(self, text: str) -> list[str]:
        step = self.chunk_size - self.chunk_overlap
        chunks = []

        for start in range(0, len(text), step):
            chunk = text[start:start + self.chunk_size].strip()
            if chunk:
                chunks.append(chunk)
            if start + self.chunk_size >= len(text):
                break

        return chunks

    def _merge_segments(self, segments: list[str], separator: str) -> list[str]:
        chunks = []
        buffer = ""

        for segment in segments:
            piece = segment.strip()
            if not piece:
                continue

            candidate = piece if not buffer else buffer + separator + piece
            if len(candidate) <= self.chunk_size:
                buffer = candidate
                continue

            if buffer:
                chunks.append(buffer.strip())

            if len(piece) > self.chunk_size:
                chunks.extend(self._split_text_recursive(piece, 1))
                buffer = ""
            else:
                buffer = piece

        if buffer.strip():
            chunks.append(buffer.strip())

        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        if not chunks or self.chunk_overlap == 0:
            return chunks

        overlapped_chunks = [chunks[0]]
        for i in range(1, len(chunks)):
            prefix = chunks[i - 1][-self.chunk_overlap:].strip()
            current = chunks[i].strip()
            if prefix:
                combined = f"{prefix}\n{current}".strip()
                overlapped_chunks.append(combined[:self.chunk_size])
            else:
                overlapped_chunks.append(current)

        return overlapped_chunks

    def _split_text_recursive(self, text: str, level: int = 0) -> list[str]:
        text = text.strip()
        if not text:
            return []
        if len(text) <= self.chunk_size:
            return [text]

        separators = ["\n\n", "\n", "。", ""]
        separator = separators[level] if level < len(separators) else ""

        if separator == "":
            return self._fallback_split(text)

        segments = self._split_by_separator(text, separator)
        if len(segments) <= 1:
            return self._split_text_recursive(text, level + 1)

        chunks = self._merge_segments(segments, separator)
        return chunks if chunks else self._split_text_recursive(text, level + 1)

    def _split_text(self, text: str) -> list[str]:
        chunks = self._split_text_recursive(text, 0)
        return self._add_overlap(chunks)

    def load_documents(self, dir_path: Union[str, Path]) -> None:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Not a directory: {dir_path}")

        self.chunks = []
        self.embeddings = None

        for path in dir_path.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".txt", ".md"}:
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

        texts = [chunk.content for chunk in self.chunks]
        all_embeddings = []
        batch_size = 10

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=batch,
            )
            all_embeddings.extend(item.embedding for item in response.data)

        self.embeddings = np.array(all_embeddings, dtype=np.float32)

    def save_index(self, filepath: Union[str, Path]) -> None:
        if self.embeddings is None:
            raise ValueError("No embeddings found. Call create_embeddings() first.")

        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        np.savez(
            filepath,
            embeddings=self.embeddings,
            chunks_content=np.array([chunk.content for chunk in self.chunks], dtype=object),
            chunks_source=np.array([chunk.source for chunk in self.chunks], dtype=object),
            chunks_index=np.array([chunk.index for chunk in self.chunks], dtype=np.int32),
        )

    def load_index(self, filepath: Union[str, Path]) -> None:
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Index file not found: {filepath}")

        data = np.load(filepath, allow_pickle=True)
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
    def _cosine_similarity(query: np.ndarray, documents: np.ndarray) -> np.ndarray:
        query_norm = np.linalg.norm(query)
        document_norms = np.linalg.norm(documents, axis=1)
        denominator = query_norm * document_norms
        denominator = np.where(denominator == 0, 1e-12, denominator)
        return np.dot(documents, query) / denominator

    def search(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        if self.embeddings is None:
            raise ValueError("No embeddings found. Call create_embeddings() first.")
        if not query.strip() or top_k <= 0:
            return []

        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=[query],
        )
        query_embedding = np.array(response.data[0].embedding, dtype=np.float32)

        similarities = self._cosine_similarity(query_embedding, self.embeddings)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        return [(self.chunks[i], float(similarities[i])) for i in top_indices]

    def build_context(self, query: str, top_k: int = 5) -> str:
        results = self.search(query, top_k=top_k)
        return "\n\n".join(
            [
                f"片段{i + 1}（来源：{chunk.source}，相似度：{score:.4f}）:\n{chunk.content}"
                for i, (chunk, score) in enumerate(results)
            ]
        )


def load_or_build_rag_library(
    client,
    embedding_model: str = "text-embedding-v4",
    docs_dir: Union[str, Path] = "library",
    index_path: Union[str, Path] = "library/index.npz",
    verbose: bool = True,
) -> RAGLibrary:
    docs_dir = Path(docs_dir)
    index_path = Path(index_path)

    rag = RAGLibrary(client=client, embedding_model=embedding_model)

    if index_path.exists():
        if verbose:
            print(f"[RAG] 加载索引: {index_path}")
        rag.load_index(index_path)
    else:
        if verbose:
            print(f"[RAG] 未找到索引，开始构建: {index_path}")
        rag.load_documents(docs_dir)
        rag.create_embeddings()
        rag.save_index(index_path)
        if verbose:
            print(f"[RAG] 索引构建完成: {index_path}")

    return rag
