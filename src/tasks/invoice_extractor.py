import os
import io
import base64
import json
import fitz  # PyMuPDF
from PIL import Image  # Pillow
from openai import OpenAI
from dotenv import load_dotenv
from prompts.prompt_loader import PromptLoader

class InvoiceExtractor:

    def __init__(self, model_id="gpt-4o", prompt_file=os.path.abspath("src/prompts/prompts.yaml")):
        # Load environment variables
        load_dotenv()
        
        # Use OpenAI with local Ollama 
        self.client = OpenAI()
        self.model_id = model_id
        self.loader = PromptLoader(prompt_file)

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def pdf_to_base64_images(self, pdf_path):
        # Handles PDFs with multiple pages
        pdf_document = fitz.open(pdf_path)
        base64_images = []
        temp_image_paths = []

        total_pages = len(pdf_document)

        for page_num in range(total_pages):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            temp_image_path = f"temp_page_{page_num}.png"
            img.save(temp_image_path, format="PNG")
            temp_image_paths.append(temp_image_path)
            base64_image = self.encode_image(temp_image_path)
            base64_images.append(base64_image)

        for temp_image_path in temp_image_paths:
            os.remove(temp_image_path)

        return base64_images

    def jpg_to_base64(self, jpg_path):
        base64_images = []
        with open(jpg_path, "rb") as image_file:
            base64_images.append(base64.b64encode(image_file.read()).decode("utf-8"))
            return base64_images


    def extract_invoice_data(self, base64_image):
        # System prompt from yaml
        system_prompt = self.loader.get_prompt("extraction_task", "system")
        # User prompt from yaml
        user_prompt = self.loader.get_prompt("extraction_task", "user")

        response = self.client.chat.completions.create(
            model=self.model_id,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}", "detail": "high"},
                        },
                    ],
                },
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content

    def extract_from_multiple_pages(self, base64_images, original_filename, output_directory):
        entire_invoice = []

        for base64_image in base64_images:
            invoice_json = self.extract_invoice_data(base64_image)
            invoice_data = json.loads(invoice_json)
            entire_invoice.append(invoice_data)

        # Ensure the output directory exists
        os.makedirs(output_directory, exist_ok=True)

        output_filename = ""

        # Construct the output file path, remove the extension and add '_extracted.json'
        # Find last . in the file name, remove the extention then add new extension
        if '.' in original_filename:
            name_without_extension = original_filename.rsplit('.', 1)[0]
            output_filename = os.path.join(output_directory, f"{name_without_extension}_extracted.json")
        else:
            output_filename = os.path.join(output_directory, f"{original_filename}_extracted.json")

        if os.path.exists(output_filename):
            os.remove(output_filename)

        # Save the entire_invoice list as a JSON file
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(entire_invoice, f, ensure_ascii=False, indent=4)
        return output_filename

    def process_directory(self, read_path, write_path):
        for filename in os.listdir(read_path):
            print("File Name - " + filename)
            file_path = os.path.join(read_path, filename)
            if os.path.isfile(file_path):
                base64_images = []
                if filename.endswith(".pdf"):
                    base64_images = self.pdf_to_base64_images(file_path)
                elif filename.endswith(".jpg"):
                    base64_images = self.jpg_to_base64(file_path)
                else:
                    continue

                self.extract_from_multiple_pages(base64_images, filename, write_path)
