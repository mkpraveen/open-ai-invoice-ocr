import streamlit as st
import os
import uuid
import json
from inv_graph import inv_graph
from IPython.display import Image, display
from langchain_core.runnables.graph_mermaid import MermaidDrawMethod

# Define paths
UPLOAD_DIR = os.path.abspath("data/images")
JSON_DIR = os.path.abspath("data/json")
ENHANCED_JSON_DIR = os.path.abspath("data/enhanced_json")

def main():
    st.set_page_config(page_title="Invoice OCR", layout="wide")
    st.title("Invoice OCR with LangGraph Agents")

    # Display the graph as png in streamlit
    # write the bytes to graph.png
    with open("graph.png", "wb") as f:
        # f.write(inv_graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER, max_retries=5, retry_delay=2.0))
        f.write(inv_graph.get_graph().draw_png())
   
    st.image("graph.png", caption="LangGraph Workflow", width=300)
    



    # Ensure directories exist
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(ENHANCED_JSON_DIR, exist_ok=True)

    uploaded_file = st.file_uploader("Upload an invoice (PDF or JPG)", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Save the uploaded file to a unique path
        ext = os.path.splitext(uploaded_file.name)[1]
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{ext}")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"File uploaded and saved to {file_path}")

        if st.button("Process Invoice"):
            with st.status("Processing invoice...", expanded=True) as status:
                st.write("Invoking graph...")
                
                inputs = {
                    "image_file_path": file_path,
                    "raw_json_path": JSON_DIR,
                    "enhanced_json_path": ENHANCED_JSON_DIR
                }
                
                final_state = None
                for s in inv_graph.stream(inputs):
                    for key, value in s.items():
                        st.write(f"Node '{key}' finished.")
                        if 'extracted_data_path' in value and value['extracted_data_path']:
                             st.write(f"- Extracted data saved to: {value['extracted_data_path']}")
                             final_state = value


                status.update(label="Invoice processing complete!", state="complete", expanded=False)

            st.success("Invoice processed successfully!")

            if final_state and final_state.get("extracted_data_path"):
                # Construct the path to the transformed file
                base_filename = os.path.basename(final_state["extracted_data_path"])
                transformed_filename = f"transformed_{base_filename}"
                transformed_file_path = os.path.join(ENHANCED_JSON_DIR, transformed_filename)

                if os.path.exists(transformed_file_path):
                    st.subheader("Transformed JSON")
                    with open(transformed_file_path, 'r') as f:
                        transformed_data = json.load(f)
                    st.json(transformed_data)
                else:
                    st.error("Transformed JSON file not found.")


if __name__ == "__main__":
    main()
