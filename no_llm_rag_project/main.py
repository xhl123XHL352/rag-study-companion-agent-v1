import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from no_llm_rag import load_or_build_no_llm_rag


PROJECT_DIR = Path(__file__).resolve().parent
PARENT_DIR = PROJECT_DIR.parent

load_dotenv(PARENT_DIR / ".env", override=True)

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
TOP_K = int(os.getenv("RAG_TOP_K", "3"))

DOCS_DIR = Path(os.getenv("NO_LLM_DOCS_DIR", PARENT_DIR / "library"))
INDEX_PATH = Path(os.getenv("NO_LLM_INDEX_PATH", PROJECT_DIR / "no_llm_index.npz"))

if not BASE_URL or not API_KEY:
    raise EnvironmentError("请先在父目录 .env 中设置 BASE_URL 和 API_KEY。")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

rag = load_or_build_no_llm_rag(
    client=client,
    embedding_model=EMBEDDING_MODEL,
    docs_dir=DOCS_DIR,
    index_path=INDEX_PATH,
)


def main() -> None:
    print(f"[RAG] 知识库目录: {DOCS_DIR}")
    print(f"[RAG] 索引文件: {INDEX_PATH}")
    print(f"[RAG] 知识块数量: {len(rag.chunks)}")
    print("纯 embedding 检索项目已启动：不调用任何对话 LLM，只返回相似文本片段。")
    print("输入 q 或 exit 退出。")

    while True:
        try:
            query = input("no-llm-rag >> ")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in {"", "q", "exit"}:
            break

        results = rag.search(query, top_k=TOP_K)
        print(rag.format_results(results))
        print()


if __name__ == "__main__":
    main()
