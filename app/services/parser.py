from __future__ import annotations
# Import necessary components from LangChain and standard Python typing libraries.
from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from typing import TypeVar, Annotated, Any, Union
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompt_values import PromptValue
from langchain_core.prompts import BasePromptTemplate, PromptTemplate
from langchain_core.runnables.base import RunnableSerializable
from pydantic import SkipValidation
from typing_extensions import TypedDict
from langchain_core.exceptions import OutputParserException
from langchain_core.messages import get_buffer_string


# Define a prompt template string for retrying a failed language model completion.
# This template is used when an initial completion fails to parse or validate.
# It provides the model with the original prompt, the failed completion, and a
# specific error message to guide it in generating a valid response.
# Note: There is a typo "prlease" which should be "please".
RETRY_WITH_ERROR = """Prompt: {prompt}
Completion: {completion}
Above , the completion did not satisfy the constraints of the prompt.
Details:{error_message}
please retry with the same prompt and provide a valid completion."""

# Create a PromptTemplate instance for the retry mechanism.
# This formalizes the RETRY_WITH_ERROR string into a reusable LangChain component.
# This formalizes the RETRY_WITH_ERROR string into a reusable LangChain component.
# It defines the input variables required to format the prompt: 'prompt',
# 'completion', and 'error_message'.
RETRY_WITH_ERROR_PROMPT = PromptTemplate(
    input_variables=["prompt", "completion", "error_message"],
    template=RETRY_WITH_ERROR,
)

# Define a TypedDict for the input to the retry chain.
# This provides a clear and type-safe structure for the data that will be
# passed to the chain that uses the RETRY_WITH_ERROR_PROMPT.
class RetryWithErrorOutputParserRetryChainInput(TypedDict):
    """Type definition for the input to the retry chain."""
    prompt: str  # The original prompt sent to the language model.
    completion: str  # The initial, failed completion from the model.
    error_message: str  # The error message explaining why the completion failed.

T = TypeVar("T")

class RetryWithErrorOutputParser(BaseOutputParser[T]):

    parser: Annotated[BaseOutputParser[T], SkipValidation()]
    """The parser used to parse the output from the language model."""
    retry_chain: Annotated[
        Union[RunnableSerializable[RetryWithErrorOutputParserRetryChainInput, str], Any],
        SkipValidation(),
    ]
    """The chain that will be used to retry parsing the output."""
    max_retries: int = 1
    """The maximum number of retries allowed for parsing the output."""

    @classmethod
    def from_llm(
        cls,
        llm: BaseLanguageModel,
        parser: BaseOutputParser[T],
        prompt: BasePromptTemplate = RETRY_WITH_ERROR_PROMPT,
        max_retries: int = 1,
    ) -> RetryWithErrorOutputParser[T]:

        """Create a RetryWithErrorOutputParser from a language model and a parser."""
        retry_chain = prompt | llm | StrOutputParser() 
        return cls(parser=parser, retry_chain=retry_chain, max_retries=max_retries)
    
    def parse_with_prompt(self, completion: str, prompt_value: PromptValue) -> T:
        retries = 0

        while retries <= self.max_retries:
            try:
                print(f"Attempt {retries + 1} to parse the completion.\n")
                return self.parser.parse_with_prompt(completion, prompt_value)
            except OutputParserException as e:
                if retries == self.max_retries:
                    raise e
                
                error_message = str(e)
                print(f"Parsing error: {error_message}. Retrying...")
                
                # Prepare the input for the retry chain
                retry_input: RetryWithErrorOutputParserRetryChainInput = {
                    "prompt": get_buffer_string(prompt_value),
                    "completion": completion,
                    "error_message": error_message,
                }
                # Invoke the retry chain to get a new completion
                completion = self.retry_chain.invoke(retry_input)
                retries += 1

        message = "Failed to parse after maximum retries."
        raise OutputParserException(message)

    def parse(self, text: str) -> T:
        """Parse the text using the output parser."""
        raise NotImplementedError(
            "This method is not implemented. Use parse_with_prompt instead."
        )    