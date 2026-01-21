## POC for Image-to-Text task using an LLM 

Modified code with reference to the OpenAI Cookbook 
- https://cookbook.openai.com/examples/data_extraction_transformation

## LLM Dependency
One of the below would be needed
- OpenAI ApiKey in .env (gpt4-o-mini) https://platform.openai.com/docs/models/gpt-4o-mini
- Ollama local with Gemma 3 [[https://ollama.com/library/gemma3]] (vision capability), Llamma 3  [[https://ollama.com/library/llama3]]

Note : code change needed on OpenAI object initialization 

## Technical Documentation

### Purpose
This project is a Streamlit-based invoice OCR pipeline that uses a LangGraph workflow to:
1) extract raw invoice data from an uploaded PDF/JPG using an LLM with vision, and
2) transform that raw JSON into a structured schema.

### High-Level Architecture
- UI entrypoint: `src/streamlit_app.py` provides file upload, status updates, and JSON previews.
- Workflow orchestration: `src/inv_graph.py` defines a two-node LangGraph state machine.
- Extraction: `src/tasks/invoice_extractor.py` converts PDFs to images, base64 encodes inputs, and calls the LLM with system/user prompts to get raw JSON.
- Transformation: `src/tasks/transform_data.py` prompts the LLM to normalize the raw JSON into the target schema.
- Node glue code: `src/agents/agents.py` binds extractor/transformer into LangGraph nodes and writes outputs.

### Runtime Data Flow (Flowchart)
```mermaid
flowchart TD
  A[User uploads invoice] --> B[Streamlit saves file to data/images]
  B --> C{Process Invoice}
  C --> D[LangGraph: extract_invoice node]
  D --> E[InvoiceExtractor: PDF/JPG -> base64 image]
  E --> F[OpenAI chat.completions vision]
  F --> G[Write raw JSON to data/json]
  G --> H[LangGraph: transform_data node]
  H --> I[InvoiceTransformer: LLM transform to schema]
  I --> J[Write transformed JSON to data/enhanced_json]
  J --> K[Streamlit renders JSON + input preview]
```

### Runtime Interaction (Sequence Diagram)
```mermaid
sequenceDiagram
  participant User
  participant UI as Streamlit UI
  participant Graph as LangGraph
  participant Extractor as InvoiceExtractor
  participant Transformer as InvoiceTransformer
  participant OpenAI as OpenAI API
  participant FS as File System

  User->>UI: Upload PDF/JPG
  UI->>FS: Save file to data/images
  User->>UI: Click "Process Invoice"
  UI->>Graph: inv_graph.stream(inputs)
  Graph->>Extractor: extract_invoice_node(state)
  Extractor->>FS: Read file
  Extractor->>OpenAI: chat.completions (vision prompt)
  OpenAI-->>Extractor: Raw JSON
  Extractor->>FS: Write data/json/*_extracted.json
  Graph->>Transformer: transform_data_node(state)
  Transformer->>OpenAI: chat.completions (schema prompt)
  OpenAI-->>Transformer: Structured JSON
  Transformer->>FS: Write data/enhanced_json/transformed_*.json
  UI->>FS: Read outputs for display
  UI-->>User: Show raw + transformed JSON and input preview
```

### Key Files and Directories
- `src/streamlit_app.py`: UI, file handling, and graph invocation.
- `src/inv_graph.py`: LangGraph workflow definition.
- `src/agents/agents.py`: Node implementations and output persistence.
- `src/tasks/invoice_extractor.py`: PDF/JPG preprocessing + extraction prompt.
- `src/tasks/transform_data.py`: Schema-based transformation prompt.
- `src/prompts/prompts.yaml`: Prompt templates used for extraction/transform.
- `src/schemas/`: Target schema definitions for transformed output.
- `data/images/`: Uploaded source files.
- `data/json/`: Raw extraction outputs.
- `data/enhanced_json/`: Transformed outputs.

## Screenshots
Example - UI
![alt text](image.png)

```mermaid
---
config:
  flowchart:
    curve: linear
---
graph TD;
  __start__([<p>__start__</p>]):::first
  extract_invoice(extract_invoice)
  transform_data(transform_data)
  __end__([<p>__end__</p>]):::last
  __start__ --> extract_invoice;
  extract_invoice --> transform_data;
  transform_data --> __end__;
  classDef default fill:#f2f0ff,line-height:1.2
  classDef first fill-opacity:0
  classDef last fill:#bfb6fc
```

