# Agentic Document Chunking System

An intelligent document chunking system that uses Large Language Models (LLM) to create semantically meaningful text segments. This system leverages the Phi framework and Ollama to perform context-aware text splitting, ensuring that document chunks maintain logical coherence.

## Key Features

- LLM-powered semantic chunking
- Intelligent chunk size optimization
- Preservation of context and meaning
- Automatic chunk merging for undersized segments
- Metadata tracking for processed chunks

## How It Works

### 1. Agent Configuration

```python
# Initialize the LLM agent
llm = Ollama(id=OLLAMA_MODEL)
agent = Agent(model=llm, show_tool_calls=True, markdown=True)

# Chunking parameters
CHUNK_SIZE = 1200      # Initial chunk size
MIN_CHUNK_SIZE = 500   # Minimum allowed chunk size
MAX_CHUNKS = 30        # Maximum chunks per document
```

### 2. Chunking Process

The system processes documents in three main stages:

1. **Initial Text Splitting**

   ```python
   chunk_text = plain_text[start_idx:start_idx + CHUNK_SIZE]
   ```

2. **Agent-Based Processing**

   ```python
   response = agent.run(
       "Split the following text into meaningful segments ensuring logical separation:\n{chunk_text}",
       max_tokens=8000
   )
   ```

3. **Chunk Optimization**
   ```python
   # Combine undersized chunks
   if len(chunk) < MIN_CHUNK_SIZE:
       temp_chunk += " " + chunk
   else:
       optimized_chunks.append(chunk)
   ```

## Usage Example

1. Prepare your document:

```python
# Input text is automatically cleaned
plain_text = clean_text(result[3])
```

2. Process with agent:

```python
while start_idx < len(plain_text) and chunk_count < MAX_CHUNKS:
    # Get text segment
    chunk_text = plain_text[start_idx:start_idx + CHUNK_SIZE]

    # Process with LLM agent
    response = agent.run(
        f"Split the following text into meaningful segments ensuring logical separation:\n{chunk_text}",
        max_tokens=8000
    )

    # Clean and structure the response
    structured_text += clean_agent_output(response) + "\n\n"
```

3. Output format:

```text
Chunk 1:
[Semantically complete segment of text]
---

Chunk 2:
[Next logical segment]
---
```

## Key Benefits

1. **Semantic Coherence**

   - Chunks maintain logical completeness
   - Sentences and paragraphs remain intact
   - Related concepts stay together

2. **Intelligent Size Management**

   - Automatically combines small chunks
   - Respects maximum chunk limits
   - Optimizes for processing efficiency

3. **Context Preservation**
   - Maintains document structure
   - Preserves semantic relationships
   - Keeps related information together

## Output Structure

### Chunked Text Files

```
chunked_data/
└── chunked_document.txt
    ├── Chunk 1: [Semantic segment]
    ├── Chunk 2: [Semantic segment]
    └── ...
```

### Metadata Tracking

```json
{
  "filename": "example.pdf",
  "total_chunks": 15,
  "total_length": 25000
}
```

## Optimization Tips

1. **Chunk Size Tuning**

   - Adjust `CHUNK_SIZE` based on document type
   - Consider content complexity
   - Balance processing speed vs. chunk coherence

2. **Agent Prompting**

   - Current prompt focuses on logical separation
   - Can be modified for specific document types
   - Adjustable based on content structure

3. **Merge Criteria**
   - `MIN_CHUNK_SIZE` ensures efficient processing
   - Prevents fragmentation
   - Maintains meaningful segment size

## Limitations

- Processing speed depends on LLM response time
- Maximum 30 chunks per document
- Requires Ollama model setup
- Text-only processing (no images/tables)

## Requirements

- Phi Framework
- Ollama
- Python 3.12+
- Sufficient RAM for document processing

## Error Handling

The system includes robust error handling for:

- Agent processing failures
- Text cleaning issues
- Chunk size violations
- Maximum chunk limit exceeded

## Logging

Console output provides processing insights:

```python
print(f"[INFO] {filename} - Panjang teks sebelum pemrosesan: {len(plain_text)}")
print(f"[INFO] Total chunks generated for {filename}: {len(chunk_data)}")
```
