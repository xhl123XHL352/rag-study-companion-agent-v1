# 无 LLM RAG 检索子项目

这个子项目是从零新建的最小 RAG 检索实现，不复制父项目的 `agent.py` 或 `rag_library.py`。

## 特点

- 只使用 embedding 模型进行向量检索。
- 不调用对话 LLM。
- 不使用 function calling。
- 不进行 LLM 总结、改写、筛选或重排序。
- 查询后直接返回相似度最高的知识库原文片段。

## 运行方式

在当前目录执行：

```powershell
py main.py
```

如果系统支持 `python` 命令，也可以执行：

```powershell
python main.py
```

## 数据来源

默认读取父目录中的知识库：

```text
../library
```

默认在本子项目目录下生成独立索引：

```text
no_llm_index.npz
```

这样不会复用或覆盖父项目的 `library/index.npz`。

## 环境变量

默认读取父目录 `.env` 中的：

```text
BASE_URL
API_KEY
EMBEDDING_MODEL
RAG_TOP_K
```

也可以额外设置：

```text
NO_LLM_DOCS_DIR
NO_LLM_INDEX_PATH
```

## 与原项目区别

| 项目 | 是否调用对话 LLM | 是否使用 embedding | 输出 |
|---|---:|---:|---|
| 父项目 | 是 | 是 | LLM 生成回答 |
| 本子项目 | 否 | 是 | 直接输出检索片段 |
