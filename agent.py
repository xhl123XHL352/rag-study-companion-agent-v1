import os
import json
import subprocess
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv
from rag_library import load_or_build_rag_library

# 1. 环境初始化
load_dotenv(override=True)

if os.getenv("BASE_URL") and os.getenv("API_KEY"):
    client = OpenAI(
        base_url=os.getenv("BASE_URL"),
        api_key=os.getenv("API_KEY"),
    )
else:
    raise EnvironmentError("Please set API_KEY and BASE_URL in your environment variables.")

CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen-plus")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-v4")
KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "library")
INDEX_PATH = os.getenv("INDEX_PATH", os.path.join(KNOWLEDGE_DIR, "index.npz"))
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))

# 2. 系统提示词（实验二：加入 RAG 检索上下文约束）
SYSTEM_PROMPT = (
    "你是一个带有 RAG 检索能力的智能助手。"
    "回答知识库相关问题前，应优先调用 search_knowledge 工具检索相关内容；"
    "如果系统提示中提供了知识库检索到的 context，你必须优先依据这些内容回答；"
    "如果知识库内容不足以回答，再结合你自身能力补充。"
    "遇到任何数学计算问题，你必须调用 calculate 工具进行计算，绝对不能自己给出答案！"
    "当用户要求执行终端命令时，你必须调用 run_terminal_command 工具，不能假装执行。"
)

# 3. 工具定义与实现
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "执行数学表达式计算。例如输入 '123 * 456' 或 '100 / 4'。遇到任何数字计算都必须使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "需要计算的数学表达式"
                    }
                },
                "required": ["expression"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "检索本地知识库，返回与问题最相关的知识片段。回答知识库、规则、流程、说明类问题前应优先调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "要检索的问题或关键词"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回的相关片段数量，默认 3",
                        "default": 3
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "在本机终端执行命令。mode 为 background 时后台执行并返回输出；mode 为 popup 时弹出新的终端窗口执行命令。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的终端命令"
                    },
                    "mode": {
                        "type": "string",
                        "description": "执行模式：background 表示后台执行并返回结果，popup 表示弹出新终端窗口执行",
                        "enum": ["background", "popup"]
                    }
                },
                "required": ["command", "mode"],
            },
        },
    }
]


def get_weather(city: str) -> str:
    import random
    conditions = ["sunny", "cloudy", "rainy", "stormy", "snowy"]
    condition = random.choice(conditions)
    temperature = random.randint(-10, 35)
    return f"The weather in {city} is {condition} with {temperature}°C."


def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算出错: {str(e)}"


def run_terminal_command(command: str, mode: str) -> str:
    try:
        if mode == "popup":
            subprocess.Popen(
                f'start powershell -NoExit -Command "{command}"',
                shell=True
            )
            return f"已在新终端窗口中执行命令: {command}"

        completed = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()
        parts = [
            "mode: background",
            f"command: {command}",
            f"returncode: {completed.returncode}",
            f"stdout: {stdout if stdout else '(empty)'}",
            f"stderr: {stderr if stderr else '(empty)'}",
        ]
        return "\n".join(parts)
    except Exception as e:
        return f"终端命令执行出错: {str(e)}"


def build_rag_library():
    if not os.path.isdir(KNOWLEDGE_DIR):
        return None

    try:
        return load_or_build_rag_library(
            client=client,
            embedding_model=EMBEDDING_MODEL,
            docs_dir=KNOWLEDGE_DIR,
            index_path=INDEX_PATH,
            verbose=True,
        )
    except Exception as e:
        print(f"知识库初始化失败，将以普通智能体模式运行: {e}")
        return None


rag = build_rag_library()


def search_knowledge(query: str, top_k: int = 3) -> str:
    if not query.strip():
        return "检索问题不能为空。"
    if top_k <= 0:
        return "top_k 必须大于 0。"
    if not rag:
        return f"知识库不可用，请检查目录 {KNOWLEDGE_DIR} 或索引文件 {INDEX_PATH}。"

    try:
        context = rag.build_context(query, top_k=top_k)
        return context if context else "未检索到相关知识片段。"
    except Exception as e:
        return f"知识库检索出错: {e}"


# 将新工具注册到字典中
tools_implementation = {
    "get_weather": get_weather,
    "calculate": calculate,
    "search_knowledge": search_knowledge,
    "run_terminal_command": run_terminal_command,
}


def build_rag_system_prompt(messages: list[dict[str, Any]]) -> str:
    latest_query = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            latest_query = str(message.get("content", ""))
            break

    if not latest_query.strip() or not rag:
        return SYSTEM_PROMPT

    try:
        context = rag.build_context(latest_query, top_k=RAG_TOP_K)
    except Exception as e:
        print(f"知识库检索失败: {e}")
        return SYSTEM_PROMPT

    if not context.strip():
        return SYSTEM_PROMPT

    return (
        f"{SYSTEM_PROMPT}\n\n"
        "以下是从知识库检索到的 context，请严格基于这些内容回答：\n"
        f"{context}"
    )


# 4. Agent 主循环（实验二：将检索结果拼接到系统提示词中）
def agent_loop(messages: list):
    while True:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "system", "content": build_rag_system_prompt(messages)}] + messages,
            tools=TOOLS,
        )

        message = response.choices[0].message

        assistant_turn = {"role": "assistant", "content": message.content or ""}
        if message.tool_calls:
            assistant_turn["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments
                    }
                }
                for call in message.tool_calls
            ]

        messages.append(assistant_turn)

        if not message.tool_calls:
            print(f"\033[32m[Assistant] {assistant_turn['content']}\033[0m")
            break

        for call in message.tool_calls:
            tool_name = call.function.name
            args = json.loads(call.function.arguments or "{}")
            tool_fn = tools_implementation.get(tool_name)

            if tool_fn:
                print(f"\033[33m[Tool Call] {tool_name} ({args})\033[0m")
                try:
                    output = tool_fn(**args)
                except Exception as e:
                    output = f"工具 {tool_name} 执行失败: {e}"
            else:
                output = f"未找到工具: {tool_name}"

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": tool_name,
                "content": str(output),
            })


# 5. 命令行交互
if __name__ == "__main__":
    history = []

    if rag:
        print(f"[RAG] 已加载知识库目录: {KNOWLEDGE_DIR}")
        print(f"[RAG] 索引文件: {INDEX_PATH}")
        print(f"[RAG] 知识块数量: {len(rag.chunks)}")
    else:
        print(f"未找到可用知识库目录或知识库初始化失败: {KNOWLEDGE_DIR}")
        print("将以普通智能体模式运行；如需启用 RAG，请检查 library 目录、index.npz 和向量模型配置。")

    print("Agent 已启动！输入 'q' 或 'exit' 退出。")
    while True:
        try:
            query = input("\033[36ms02 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break

        if query.strip().lower() in ("q", "exit", ""):
            break

        history.append({"role": "user", "content": query})
        agent_loop(history)
        print()
