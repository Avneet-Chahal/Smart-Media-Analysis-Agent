import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


# Load variables from .env
load_dotenv()

FOUNDRY_PROJECT_ENDPOINT = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
FOUNDRY_AGENT_NAME = os.getenv("FOUNDRY_AGENT_NAME")

print("Checking Foundry configuration...")

if not FOUNDRY_PROJECT_ENDPOINT:
    raise ValueError("FOUNDRY_PROJECT_ENDPOINT is missing from .env")

if not FOUNDRY_AGENT_NAME:
    raise ValueError("FOUNDRY_AGENT_NAME is missing from .env")

print("✓ Foundry project endpoint found")
print(f"✓ Agent name: {FOUNDRY_AGENT_NAME}")

# Authenticate using Azure CLI
credential = DefaultAzureCredential()

# Connect to Microsoft Foundry
project = AIProjectClient(
    endpoint=FOUNDRY_PROJECT_ENDPOINT,
    credential=credential,
    allow_preview=True,
)

print("✓ Connected to Microsoft Foundry")

# Connect to the existing Foundry Agent
openai = project.get_openai_client(
    agent_name=FOUNDRY_AGENT_NAME
)

print("✓ Connected to Foundry Agent")

# Test question
question = "According to the uploaded educational material, what is polymorphism?"

print("\nSending question to Smart Media Agent...")
print(f"Question: {question}")

response = openai.responses.create(
    input=question
)

print("\n==============================")
print("AZURE FOUNDRY RESPONSE")
print("==============================")

print(response.output_text)

print("\n==============================")
print("CONNECTION TEST SUCCESSFUL")
print("==============================")