from openai import OpenAI # OpenAI SDK
import os
import json
import time

from dotenv import load_dotenv
from schemas import InvoiceHeader  # Assuming you have a schemas.py file with InvoiceData defined
from prompt_loader import PromptLoader
from invoice_extractor import main_extract

# Load environment variables from .env
load_dotenv()  # load variables from .env into the environment

api_key = os.getenv("OPENAI_API_KEY")

# client = OpenAI(api_key=api_key)

# Use OpenAI with local Ollama 
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

# model_id = "gpt-4o-mini"
model_id = "llama3"


loader = PromptLoader("prompts.yaml")


def transform_invoice_data(json_raw):
    system_prompt = loader.get_prompt("transform_task", "system", 
                                      schema_class=InvoiceHeader)
    user_prompt = loader.get_prompt("transform_task", "user", json_raw=json_raw)
    
    print("System Prompt - " + system_prompt)
    print("User Prompt - " + user_prompt)

    response = client.chat.completions.create(
        model=model_id,
        response_format={ "type": "json_object" },
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt}
                ]
            }
        ],
        temperature=0.0,
    )
    return json.loads(response.choices[0].message.content)



def main_transform(extracted_invoice_json_path, save_path):
    # Ensure the save directory exists
    os.makedirs(save_path, exist_ok=True)

    # Process each JSON file in the extracted invoices directory
    for filename in os.listdir(extracted_invoice_json_path):
        print("File Name - " + filename)

        if filename.endswith(".json"):
            file_path = os.path.join(extracted_invoice_json_path, filename)

            # Load the extracted JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_raw = json.load(f)

            # Transform the JSON data
            transformed_json = transform_invoice_data(json_raw)

            # Save the transformed JSON to the save directory
            transformed_filename = f"transformed_{filename}"
            transformed_file_path = os.path.join(save_path, transformed_filename)
            with open(transformed_file_path, 'w', encoding='utf-8') as f:
                json.dump(transformed_json, f, ensure_ascii=False, indent=2)





read_path= "./data/pdf"
write_path= "./data/json"
enhanced_json = "./data/enhanced_json"



if __name__ == "__main__":
    main_extract(read_path, write_path)
    # Sleep for 20 seconds
    time.sleep(20)
    
    main_transform(write_path, enhanced_json)
