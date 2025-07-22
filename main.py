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

    system_prompt = {
        "role": "system",
        "content": f"""
You are a religious guru and an expert in Hindu literature, particularly the Bhagavad Gita.

You must strictly follow the rules below:

1. You are only allowed to answer using the content provided in the context below.
2. Do NOT draw from any other scriptures, spiritual traditions, or external knowledge — even if the user asks.
3. If the question cannot be answered from the context provided below, respond with:
   "I'm only able to answer questions that relate to the Bhagavad Gita based on the context provided. Let's return to that topic. I apoligize if you believe you were on topic but I couldn't answer the question. AI is not perfect after all! not yet atleast!"
4. Do NOT add personal interpretations or speculative commentary.
5. Every valid answer must include:
   - Topic
   - The chapters in Gita that deal with this topic
   - The specific verses in those chapters
   - A snippet of those verses
   - Summary
   - Follow-up questions that you may have on this topic
6. any question that the user asks, always understand it "from the context of Bhagavat Gita" if the user doesnt explicitly mention it.

Your answers must be in **simple, clear language** and remain strictly tied to the context.

--------------------------
## CONTEXT:
{relevant_sections}
""",
    }

    # Always prepend system prompt freshly to avoid drift
    chat_history = [system_prompt]

    if not history:
        chat_history.append(
            {
                "role": "assistant",
                "content": "Namaste, Ask me any questions on Bhagavat Gita!",
            }
        )
    else:
        chat_history += history

    chat_history.append({"role": "user", "content": message})
    initial_state = State(messages=chat_history)
    response = graph.invoke(initial_state)
    return response["messages"][-1].content


def main():
    print("Hello from langgraph-demo!")
    gr.ChatInterface(
        chat,
        type="messages",
        title="Let's chat on Bhagavat Gita",
        # chatbot=gr.Chatbot(
        #     type="messages",
        #     value=[
        #         {
        #             "role": "assistant",
        #             "content": "Namaste! I'm here to answer any questions on Bhagavat Gita.",
        #         }
        #     ]
        # ),
        examples=[
            "What does Gita say about Karma?",
            "Why did God create this world?",
            "What is the relationship between knowledge and action?",
            "Who are friends and enemies per Gita?",
            "According to Gita, what is devotion?",
        ],
        example_labels=["Karma", "Creation", "Knowledge", "Relationships", "Devotion"],
    ).launch()


if __name__ == "__main__":
    main()
