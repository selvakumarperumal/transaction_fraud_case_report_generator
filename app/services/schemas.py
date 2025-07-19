from pydantic import BaseModel, Field

# Define the model output schema
class TransactionAnalysis(BaseModel):
    insights: str = Field(
        description="Insights derived from the transaction data analysis."
    )
    fraud_indicators: list[str] = Field(
        description="List of potential fraud indicators identified in the transaction history."
    )
