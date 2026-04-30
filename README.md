# RAG-Enhanced Intelligent Study Companion Agent / RAG 增强型智能学伴 Agent

## README Structure / 说明文档结构

This README is a bilingual document. The English version comes first, followed by the Chinese version.

本文档为中英双语说明文档。结构为：先英文说明，后中文说明。

- [English Version](#english-version)
- [中文版](#中文版)

---

# English Version

## RAG-Enhanced Intelligent Study Companion Agent

A RAG-enhanced AI Agent for university policy question answering. This project combines local knowledge retrieval, embedding-based vector search, and LLM function calling to help students query academic regulations and institutional policies more accurately and efficiently.

## Overview

Students often need to search through long policy documents when checking academic regulations, student status rules, course procedures, or university management policies. Manually reading these documents is time-consuming, and general-purpose large language models may produce unsupported or inaccurate answers when handling school-specific rules.

This project solves that problem by building a local knowledge base from university regulation documents and connecting it with an LLM-powered Agent. When a user asks a question, the system retrieves the most relevant document fragments first, then uses them as grounded context for answer generation.

## Key Features

- RAG-enhanced question answering
- Local document knowledge base
- Recursive text chunking with overlap
- Embedding-based vector indexing
- Cosine similarity retrieval
- Function calling Agent workflow
- Knowledge search tool
- Mathematical calculation tool
- Weather query demo tool
- Local terminal command execution tool
- No-LLM RAG baseline project for comparison
- Configurable API, model, and retrieval settings through `.env`

## Core Workflow

1. Load local documents from the `library` directory.
2. Split long documents into semantic chunks with overlap.
3. Generate embeddings for each text chunk.
4. Save or load the local vector index from `index.npz`.
5. Receive a user question from the command line.
6. Retrieve the most relevant knowledge fragments using cosine similarity.
7. Inject retrieved context into the system prompt.
8. Let the LLM Agent decide whether to call tools.
9. Return a final answer grounded in the retrieved knowledge.

## Project Structure

```text
.
├── agent.py                    # Main LLM Agent with RAG and tool calling
├── rag_library.py              # RAG library for chunking, embedding, indexing, and search
├── library/                    # Local knowledge base documents
│   ├── knowledge.txt
│   ├── 北京理工大学本科生学籍管理细则.txt
│   ├── 北京理工大学本科生管理规定.txt
│   └── index.npz               # Generated vector index, ignored by Git
└── no_llm_rag_project/          # Retrieval-only baseline project
    ├── main.py
    ├── no_llm_rag.py
    ├── README.md
    └── requirements.txt
```

## Tools Supported by the Agent

### `search_knowledge`

Searches the local knowledge base and returns the most relevant text fragments. The Agent is designed to prioritize this tool when answering questions related to rules, policies, procedures, and local documents.

### `calculate`

Executes mathematical expressions. The system prompt requires the Agent to use this tool for calculation tasks instead of directly generating answers.

### `run_terminal_command`

Runs terminal commands on the local machine. It supports both background execution and popup terminal execution.

### `get_weather`

A simple demonstration tool for function calling.

## Requirements

Recommended Python version:

```text
Python 3.10+
```

Main dependencies:

```text
openai
python-dotenv
numpy
```

Install dependencies manually:

```bash
pip install openai python-dotenv numpy
```

## Environment Variables

Create a `.env` file in the project root and configure the following variables:

```env
BASE_URL=your_api_base_url
API_KEY=your_api_key
CHAT_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v4
KNOWLEDGE_DIR=library
INDEX_PATH=library/index.npz
RAG_TOP_K=3
```

Required variables:

- `BASE_URL`: API base URL compatible with the OpenAI SDK
- `API_KEY`: Your API key

Optional variables:

- `CHAT_MODEL`: Chat model used by the Agent
- `EMBEDDING_MODEL`: Embedding model used for vector indexing and retrieval
- `KNOWLEDGE_DIR`: Directory containing local documents
- `INDEX_PATH`: Path of the saved vector index
- `RAG_TOP_K`: Number of retrieved chunks used as context

## How to Run

Run the main Agent:

```bash
python agent.py
```

On Windows, you can also use:

```powershell
py agent.py
```

After startup, the program will load or build the RAG index and enter an interactive command-line chat mode.

Example questions:

```text
What are the rules for undergraduate student status management?
```

```text
According to the school policy, what should a student do in case of academic status change?
```

```text
Calculate 123 * 456
```

To exit:

```text
q
```

or:

```text
exit
```

## No-LLM RAG Baseline

The project also includes a retrieval-only baseline in `no_llm_rag_project`. This version does not call a chat LLM and does not use function calling. It only performs embedding-based retrieval and directly returns the most relevant original text snippets.

Run it with:

```bash
cd no_llm_rag_project
python main.py
```

This baseline is useful for comparing pure retrieval results with LLM-enhanced RAG answers.

## Use Cases

- University policy Q&A
- Academic regulation consultation
- Student status management inquiry
- Course and teaching procedure guidance
- Local document-based intelligent assistant
- RAG and Agent learning project
- Vertical AI application prototype

## Technical Highlights

- Uses recursive text splitting to preserve semantic structure.
- Adds chunk overlap to reduce information loss across chunk boundaries.
- Stores embeddings and metadata in a local `.npz` index file.
- Uses cosine similarity for efficient semantic retrieval.
- Combines retrieved context with system prompts to reduce hallucination.
- Implements a tool-calling loop where the Agent can call external functions and use their results for final answers.

## Notes

- The first run may take longer because the system needs to build the vector index.
- If `index.npz` already exists, the system will load it directly.
- If documents in `library` are updated, delete the old index file and rerun the program to rebuild the index.
- Do not upload your `.env` file or API key to a public repository.

## License

This project is for learning and research purposes. You may modify it according to your own academic or development needs.

---

# 中文版

## RAG 增强型智能学伴 Agent

这是一个面向高校规章制度问答场景的 RAG 增强型 AI Agent 项目。项目结合了本地知识库检索、Embedding 向量搜索和大语言模型 Function Calling 能力，帮助学生更高效、准确地查询学籍管理、课程流程、教学管理规定等校内制度信息。

## 项目简介

在高校学习和管理场景中，学生经常需要查阅大量规章制度文件，例如学籍管理细则、本科生管理规定、课程相关流程等。传统方式需要人工翻阅长文档，效率较低；而直接使用通用大模型回答这类问题时，又容易出现依据不明确、回答不准确或“幻觉”的问题。

本项目通过构建本地知识库，并将其与 LLM Agent 结合，在用户提问时先检索相关制度原文片段，再将检索结果作为上下文提供给大模型生成回答，从而提升回答的准确性、可追溯性和实用性。

## 核心功能

- RAG 增强问答
- 本地文档知识库管理
- 文本递归切分与重叠窗口处理
- Embedding 向量索引构建
- 基于余弦相似度的语义检索
- Function Calling Agent 工具调用流程
- 本地知识库检索工具
- 数学计算工具
- 天气查询示例工具
- 本地终端命令执行工具
- 无 LLM 的 RAG 检索对照项目
- 支持通过 `.env` 配置 API、模型和检索参数

## 核心流程

1. 从 `library` 目录读取本地知识库文档。
2. 使用递归切分策略将长文档拆分为语义片段。
3. 通过 overlap 机制降低分块边界造成的信息丢失。
4. 调用 Embedding 模型为每个文本片段生成向量。
5. 将向量和文本元数据保存为本地索引文件。
6. 用户在命令行中输入问题。
7. 系统根据问题向量检索最相关的知识片段。
8. 将检索到的 context 注入系统提示词。
9. Agent 判断是否需要调用工具。
10. 工具执行结果回填给模型。
11. 模型基于检索内容和工具结果生成最终回答。

## 项目结构

```text
.
├── agent.py                    # 主 Agent 程序，包含 RAG 和工具调用逻辑
├── rag_library.py              # RAG 库，负责文本切分、向量化、索引和检索
├── library/                    # 本地知识库目录
│   ├── knowledge.txt
│   ├── 北京理工大学本科生学籍管理细则.txt
│   ├── 北京理工大学本科生管理规定.txt
│   └── index.npz               # 自动生成的向量索引文件，不建议上传到 GitHub
└── no_llm_rag_project/          # 无 LLM 的纯检索对照项目
    ├── main.py
    ├── no_llm_rag.py
    ├── README.md
    └── requirements.txt
```

## Agent 支持的工具

### `search_knowledge`

用于检索本地知识库，返回与用户问题最相关的文本片段。对于规章制度、流程说明、校内政策等问题，Agent 会优先使用该工具进行查询。

### `calculate`

用于执行数学表达式计算。系统提示词要求 Agent 在遇到数学计算问题时必须调用该工具，而不是直接由模型生成答案，从而降低计算错误。

### `run_terminal_command`

用于在本地终端执行命令。该工具支持后台执行和弹出新终端窗口执行两种模式。

### `get_weather`

一个简单的天气查询示例工具，主要用于演示 Function Calling 的基本流程。

## 环境要求

推荐 Python 版本：

```text
Python 3.10+
```

主要依赖：

```text
openai
python-dotenv
numpy
```

可以通过以下命令安装依赖：

```bash
pip install openai python-dotenv numpy
```

## 环境变量配置

在项目根目录创建 `.env` 文件，并配置以下变量：

```env
BASE_URL=your_api_base_url
API_KEY=your_api_key
CHAT_MODEL=qwen-plus
EMBEDDING_MODEL=text-embedding-v4
KNOWLEDGE_DIR=library
INDEX_PATH=library/index.npz
RAG_TOP_K=3
```

必填变量：

- `BASE_URL`：兼容 OpenAI SDK 的 API 地址
- `API_KEY`：API 密钥

可选变量：

- `CHAT_MODEL`：Agent 使用的对话模型
- `EMBEDDING_MODEL`：向量化和检索使用的 Embedding 模型
- `KNOWLEDGE_DIR`：本地知识库目录
- `INDEX_PATH`：向量索引保存路径
- `RAG_TOP_K`：每次检索返回的知识片段数量

> 注意：`.env` 文件中通常包含 API Key，不要上传到公开仓库。

## 运行方式

运行主 Agent：

```bash
python agent.py
```

Windows 环境也可以使用：

```powershell
py agent.py
```

程序启动后，会自动加载或构建 RAG 索引，并进入命令行交互模式。

示例问题：

```text
本科生学籍管理有哪些规定？
```

```text
根据学校规定，学生学籍异动应该如何处理？
```

```text
计算 123 * 456
```

退出程序：

```text
q
```

或：

```text
exit
```

## 无 LLM RAG 对照项目

项目中还包含一个纯检索版本：`no_llm_rag_project`。该版本不调用对话大模型，也不使用 Function Calling，只进行 Embedding 向量检索，并直接返回相似度最高的原文片段。

运行方式：

```bash
cd no_llm_rag_project
python main.py
```

这个子项目可以用于对比“纯向量检索”和“LLM 增强生成”两种方案的效果差异。

## 适用场景

- 高校规章制度问答
- 学籍管理政策咨询
- 课程和教学流程查询
- 本地文档智能问答助手
- RAG 技术学习与实验
- Agent 工具调用机制学习
- 垂类 AI 应用原型开发

## 技术亮点

- 使用递归文本切分，尽量保留文档语义结构。
- 引入 chunk overlap，减少文本分块边界带来的上下文丢失。
- 使用 `.npz` 文件保存本地向量索引和文本元数据。
- 使用余弦相似度实现语义检索。
- 将检索结果注入系统提示词，降低模型幻觉。
- 实现工具调用闭环，使 Agent 能够根据问题自动调用外部函数。
- 同时提供 LLM 增强版本和无 LLM 检索版本，便于效果对比。

## 注意事项

- 首次运行时，如果索引文件不存在，系统会自动构建向量索引，耗时可能较长。
- 如果 `index.npz` 已存在，系统会直接加载索引。
- 如果更新了 `library` 目录中的知识库文件，建议删除旧索引后重新运行程序，以生成新的索引。
- 不要将 `.env`、API Key、缓存文件、向量索引文件上传到公开仓库。
- 本项目主要用于课程学习、RAG 实验和垂类 AI 原型验证。

## License

本项目用于学习、研究和课程实验。你可以根据自己的学习或开发需求进行修改和扩展。
