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

    expand = st.expander("LangGraph Workflow", icon=":material/info:")
    # You can also use "with" notation:
    with expand:
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
                
                raw_json_data_file_path = None
                enhanced_json_data_file_path = None


                for s in inv_graph.stream(inputs):
                    for key, value in s.items():
                        st.write(f"Node '{key}' finished.")
                        if 'extracted_data_file_path' in value and value['extracted_data_file_path']:
                             st.write(f"- Extracted data saved to: {value['extracted_data_file_path']}")
                             raw_json_data_file_path = value['extracted_data_file_path']
                        if 'transformed_file_path' in value and value['transformed_file_path']:
                             st.write(f"- Transformed data saved to: {value['transformed_file_path']}")
                             enhanced_json_data_file_path = value['transformed_file_path']                    

                status.update(label="Invoice processing complete!", state="complete", expanded=False)

            st.success("Invoice processed successfully!")

            # Create two containers in streamlit that shows both raw and tranformed json
            col1, col2, col3 = st.columns(3)
            with col1:
                if os.path.exists(enhanced_json_data_file_path):
                    st.subheader("Transformed JSON")
                    with open(enhanced_json_data_file_path, 'r') as f:
                        transformed_data = json.load(f)
                    st.json(transformed_data)
                else:
                    st.error("Transformed JSON file not found.")
            with col2:
                if os.path.exists(raw_json_data_file_path):
                    st.subheader("Raw JSON")
                    with open(raw_json_data_file_path, 'r') as f:
                        raw_data = json.load(f)
                    st.json(raw_data)
                else:
                    st.error("Raw JSON file not found.")
            with col3:
                if os.path.exists(file_path):
                    st.subheader("Uploaded Image")
                    st.image(file_path)
                else:
                    st.error("Uploaded image file not found.")



if __name__ == "__main__":
    main()
