from typing import TypedDict, override
from langgraph.constants import END, START
from langgraph.graph.state import StateGraph
from typing_extensions import Annotated
from pydantic import BaseModel
from langgraph.graph.message import add_messages
import gradio as gr
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from db import MyDatabase

load_dotenv(override=True)
mydb = MyDatabase()


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-4o-mini")


def chatNode(state: State):
    messages = state["messages"]
    print("messages = ", messages)
    responseMessage = llm.invoke(messages)
    newState = State(messages=[responseMessage])
    return newState


def encryptNode(state: State):
    messages = state["messages"]
    messages[-1].content += "\n--------- \n with love, \n##### Krishna"
    newState = State(messages=messages)
    return newState


graph_builder.add_node("MyChatNode", chatNode)
graph_builder.add_node("MyEncryptNode", encryptNode)
graph_builder.add_edge(START, "MyChatNode")
graph_builder.add_edge("MyChatNode", "MyEncryptNode")
graph_builder.add_edge("MyEncryptNode", END)
graph = graph_builder.compile()


def chat(message, history):
    # Ensure history is a list of message dicts
    relevant_sections = mydb.get_data(message)
    if not history:
        history = [
            {
                "role": "system",
                "content": f"""You are a religious researcher, expert in Hindu literature like Bhagavat Gita. 
                User asks questions and you will answer from the context given below. it is important that you answer ONLY from the context given below and nowhere else.
                In your response, mention which chapter and verses from which you came up with this explanation.
                DO NOT talk about other spiritual traditions. Limit yourself to the context at all times.
                organize your response under subheadings for clarity and keep it simple in terms of language and brief. Do not add your interpretation or additional commentary.
                Answer any question in the context of Bhagavat Gita (particularly from the context given below). If you dont know the answer, just say so.

                here is the context:
                {relevant_sections}
            """,
            },
            {
                "role" : "assistant",
                "content" : "Namaste, Ask me any questions on Bhagavat Gita!"
            }
        ]
    initial_state = State(messages=history + [{"role": "user", "content": message}])
    print("initial_state = ", initial_state)
    response = graph.invoke(initial_state)
    return response["messages"][-1].content


def main():
    print("Hello from langgraph-demo!")
    gr.ChatInterface(
        chat,
        type="messages",
        title="Let's chat on Bhagavat Gita",
        examples=[
            "What does Gita say about Karma?",
            "Why did God create this world?",
            "What is the relationship between knowledge and action?",
            "Who are friends and enemies per Gita?"
        ],
    ).launch()


if __name__ == "__main__":
    main()
