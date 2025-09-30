from langchain.memory import ConversationBufferMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from typing import List

class ShortTermMemory:
    def __init__(self):
        # LangChainDeprecationWarning: 请参阅迁移指南 at: https://python.langchain.com/docs/versions/migrating_memory/
        # 在 LangGraph 中我们将手动处理消息，此处的 ConversationBufferMemory 主要用于格式化
        self.memory = ConversationBufferMemory(return_messages=True)

    def add_message(self, message: BaseMessage):
        if isinstance(message, HumanMessage):
            self.memory.chat_memory.add_user_message(message.content)
        elif isinstance(message, AIMessage):
            self.memory.chat_memory.add_ai_message(message.content)

    def get_messages(self) -> List[BaseMessage]:
        return self.memory.chat_memory.messages

    def clear(self):
        self.memory.clear()

    def get_history_string(self) -> str:
        """返回格式化的聊天历史字符串"""
        history = ""
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                history += f"Human: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history += f"AI: {msg.content}\n"
        return history
