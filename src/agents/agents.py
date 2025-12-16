import os
import json
from typing import TypedDict

from tasks.invoice_extractor import InvoiceExtractor
from tasks.transform_data import InvoiceTransformer


class AgentState(TypedDict):
    image_file_path: str
    raw_json_path: str
    enhanced_json_path: str
    extracted_data_file_path: str
    transformed_file_path: str

#-----------------------------------------
# Agent Node for extract invoice data
#-----------------------------------------
def extract_invoice_node(state: AgentState):
    """
    Extracts invoice data from an image file.
    The resulting data is expected in a JSON format.
    This JSON document is not following any schema.
    
    :param state: The graph state containing the image file path, resulting JSON path and enhanced JSON path.
    :type state: AgentState
    """

    print("---EXTRACTING INVOICE---")
    image_path = state["image_file_path"]
    extract_path = state["raw_json_path"]
    
    extractor = InvoiceExtractor()
    
    base64_images = []
    filename = os.path.basename(image_path)
    if filename.endswith(".pdf"):
        base64_images = extractor.pdf_to_base64_images(image_path)
    elif filename.endswith(".jpg"):
        base64_images = extractor.jpg_to_base64(image_path)
    else:
        print(f"Skipping file {filename} as it is not a PDF or JPG.")
        return {"extracted_data_file_path": None}

    extracted_file = extractor.extract_from_multiple_pages(base64_images, filename, extract_path)
    print(f"Extracted file: {extracted_file}")

    return {"extracted_data_file_path": extracted_file}

#-----------------------------------------
# Agent Node for transform data
#-----------------------------------------
def transform_data_node(state: AgentState):
    """
    The raw json received from Extractor task will be transformed to the desired schema.
    
    :param state: The graph state containing the image file path, resulting JSON path and enhanced JSON path.
    :type state: AgentState
    """
    print("---TRANSFORMING DATA---")
    extracted_file_path = state["extracted_data_file_path"]
    enhanced_json_path = state["enhanced_json_path"]
    
    if not extracted_file_path:
        print("Skipping transformation as there is no extracted file.")
        return
        
    transformer = InvoiceTransformer()
    
    with open(extracted_file_path, 'r', encoding='utf-8') as f:
        json_raw = json.load(f)

    # Transform the JSON data
    transformed_json = transformer.transform_invoice_data(json_raw)

    # Save the transformed JSON to the save directory
    filename = os.path.basename(extracted_file_path)
    transformed_filename = f"transformed_{filename}"
    transformed_file_path = os.path.join(enhanced_json_path, transformed_filename)
    with open(transformed_file_path, 'w', encoding='utf-8') as f:
        json.dump(transformed_json, f, ensure_ascii=False, indent=2)

    print(f"Transformed file: {transformed_file_path}")

    return {"transformed_file_path": transformed_file_path}