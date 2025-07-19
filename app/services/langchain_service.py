from langchain_core.outputs import Generation
from langchain_core.prompt_values import PromptValue
from langchain_huggingface.chat_models import ChatHuggingFace
from langchain_huggingface import HuggingFaceEndpoint
from app.core.config import Settings
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, BaseOutputParser
from app.services.schemas import TransactionAnalysis
from pydantic import BaseModel, ValidationError
from typing import Any, TypeVar, Generic
from langchain_core.runnables.base import RunnableSerializable
from app.services.parser import RetryWithErrorOutputParser
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI, ChatGoogleGenerativeAIError

settings = Settings()
hf_token = settings.HUGGINGFACE_API_TOKEN
gemini_api = settings.GOOGLE_GENAI_API

# Initialize the chat model with HuggingFace or Google Gemini based on availability

# llm = HuggingFaceEndpoint(
#     repo_id="deepseek-ai/DeepSeek-R1",
#     huggingfacehub_api_token=hf_token,
#     provider="fireworks-ai",
#     temperature=0.1,
# )
# # Pass it into ChatHuggingFace
# chat_model = ChatHuggingFace(llm=llm)

try:
    chat_model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        api_key=gemini_api,
        temperature=0.1,
    )
except ChatGoogleGenerativeAIError as e:
    raise RuntimeError(f"Failed to initialize Google Gemini model: {e}")



# Define the prompt template
system_message = SystemMessagePromptTemplate.from_template(
    "You are a helpful assistant that investigates fraudulent transactions."
)
human_message = HumanMessagePromptTemplate.from_template(
    """Analyze the transaction history: {transaction_history} and provide insights.
    Output Format:
    "insights": "<Your insights here>"
    "fraud_indicators": ["<Indicator 1>", "<Indicator 2>", ...]
    Ensure the output is concise and focused on potential fraud indicators."""
)

chat_prompt = ChatPromptTemplate.from_messages(
    [
        system_message,
        human_message,
    ]
)

# Create the output parser
output_parser = PydanticOutputParser(pydantic_object=TransactionAnalysis)

# Define the output parser for retrying failed completions
retry_output_parser = RetryWithErrorOutputParser.from_llm(
    llm=chat_model,
    parser=output_parser,
    max_retries=3
)

# Function to analyze transaction history
def analyze_transaction_history(transaction_history: str) -> TransactionAnalysis:
    """Analyze transaction history and return insights."""
    # Prepare the prompt with the transaction history
    prompt = chat_prompt.format_messages(transaction_history=transaction_history)
    
    # Generate the response using the chat model
    response = chat_model.invoke(prompt).content
    response = response[20:]

    print(f"Response from model: {response}")
    # Parse the output using the defined output parser
    # parsed_output = output_parser.parse(response)

    # If parsing fails, use the retry chain
    # if not isinstance(parsed_output, TransactionAnalysis):
    parsed_output = retry_output_parser.parse_with_prompt(response, prompt)

    return parsed_output


# Example usage
# if __name__ == "__main__":
#     transaction_history = "Transaction 1: $100, Transaction 2: $200, Transaction 3: $150 Transaction 4: $500 Transaction 5: $50 Transaction 6: $300 Transaction 7: $1000"
#     analysis_result = analyze_transaction_history(transaction_history)
#     print(analysis_result.model_dump_json())  # Print the insights in JSON format

