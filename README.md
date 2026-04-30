# RAG-Enhanced Intelligent Study Companion Agent

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
│   └── index.npz               # Generated vector index
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
