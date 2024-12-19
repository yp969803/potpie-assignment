from langchain.agents import initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFaceLLM
from langchain.tools import BaseTool
import os
from transformers import pipeline



class CodeReviewTool(BaseTool):
    name = "CodeReviewTool"
    description = "Tool for reviewing code and providing insights"

    def _run(self, code: str):

        generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')
        result = generator(code, max_length=100, num_return_sequences=1)
        return result[0]['generated_text']

    async def _arun(self, code: str):
        """Asynchronous implementation (if required)."""
        raise NotImplementedError("Asynchronous execution not supported.")


code_review_tool = CodeReviewTool()

llm = HuggingFaceLLM(model='EleutherAI/gpt-neo-1.3B') 

prompt_template = PromptTemplate(
    input_variables=["code"],
    template="Please analyze the following code and provide feedback:\n\n{code}"
)

agent = initialize_agent(
    tools=[code_review_tool],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True
)

def analyze_code(code_files):
    results = []
    for code in code_files:
        feedback = agent.run(f"Review the following code:\n\n{code}")
        results.append(feedback)
    return results

if __name__ == "__main__":
    example_code_files = [
        "def add(a, b):\n    return a + b",
        "def divide(a, b):\n    return a / b"
    ]
    reviews = analyze_code(example_code_files)
    for idx, review in enumerate(reviews, 1):
        print(f"Code {idx} Review:\n{review}\n")
