from langchain_huggingface.chat_models import ChatHuggingFace
from langchain_huggingface import HuggingFaceEndpoint
from langchain.schema.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv
import os

hf_token = os.getenv("HF_TOKEN")

# Create base LLM first
llm = HuggingFaceEndpoint(
    repo_id="deepseek-ai/DeepSeek-R1",
    huggingfacehub_api_token=hf_token,
    provider="fireworks-ai",
    temperature=0.1,
)

# Pass it into ChatHuggingFace
chat_model = ChatHuggingFace(llm=llm)

# Define the prompt template with system and AI messages
messages = [
    HumanMessage(content="What is the capital of France?, and why?"),
]

response = chat_model.invoke(input=messages)

print(response)