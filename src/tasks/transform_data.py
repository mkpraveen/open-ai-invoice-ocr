from openai import OpenAI # OpenAI SDK
import os
import json

from dotenv import load_dotenv
from schemas.schemas import InvoiceHeader 
from prompts.prompt_loader import PromptLoader

class InvoiceTransformer:
    def __init__(self, model_id="llama3", prompt_file=os.path.abspath("src/prompts/prompts.yaml")):
        # Load environment variables from .env
        load_dotenv()

        # Use OpenAI with local Ollama 
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.model_id = model_id
        self.loader = PromptLoader(prompt_file)

    def transform_invoice_data(self, json_raw):
        system_prompt = self.loader.get_prompt("transform_task", "system", 
                                          schema_class=InvoiceHeader)
        user_prompt = self.loader.get_prompt("transform_task", "user", json_raw=json_raw)
        
        # print("System Prompt - " + system_prompt)
        # print("User Prompt - " + user_prompt)

        response = self.client.chat.completions.create(
            model=self.model_id,
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

    def process_directory(self, extracted_invoice_json_path, save_path):
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
                transformed_json = self.transform_invoice_data(json_raw)

                # Save the transformed JSON to the save directory
                transformed_filename = f"transformed_{filename}"
                transformed_file_path = os.path.join(save_path, transformed_filename)
                with open(transformed_file_path, 'w', encoding='utf-8') as f:
                    json.dump(transformed_json, f, ensure_ascii=False, indent=2)