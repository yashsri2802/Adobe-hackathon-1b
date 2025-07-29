## Overview

This project is a Python-based document analysis tool that extracts relevant sections from PDF documents based on a specific persona and job description. It uses machine learning models to identify and rank document sections by their relevance to a given task, making it ideal for automated document processing and content extraction workflows.

## Project Structure

- README.md
  → Project overview and documentation

- requirements.txt
  → Python dependencies

- Dockerfile
  → Docker container configuration

- .dockerignore
  → Docker build exclusions

- round1b_offline.py
  → Main script for PDF analysis and section extraction

- batch_run.py
  → Script to batch process all cases

- models/
  → Pre-trained models directory
  └── all-MiniLM-L6-v2/
      → Sentence transformer model used for semantic similarity

- case1/
  → Test Case 1: Travel Planning
  ├── input/
  │   → Input PDF documents
  ├── output/
  │   → Generated JSON results
  └── challenge1b_input.json
      → Input configuration file for the case

- case2/
  → Test Case 2

- case3/
  → Test Case 3
## Code Explanation

### Main Processing Script (round1b_offline.py)

The core functionality is implemented in round1b_offline.py, which performs the following operations:

1. **PDF Text Extraction**: Uses PyMuPDF (fitz) to extract text and structural elements from PDF documents
2. **Document Outline Detection**: Automatically identifies document structure including:
   - Document title (largest text on first page)
   - Section headers (H1, H2, H3 levels based on font size and formatting)
   - Page numbers for each section
3. **Semantic Similarity Analysis**: Uses sentence transformers to compute similarity between:
   - User's persona and job description
   - Document sections and content
4. **Content Ranking**: Ranks sections by relevance using cosine similarity scores
5. **JSON Output Generation**: Creates structured output with metadata and extracted sections

### Key Functions:

- clean(txt): Text preprocessing and normalization
- extract_outline(pdf_path): PDF structure analysis and outline extraction
- main(): Orchestrates the entire processing pipeline

### Batch Processing (batch_run.py)

Automates processing of multiple test cases sequentially, ensuring consistent execution across different scenarios.

## Models Used

### Primary Model: all-MiniLM-L6-v2

- **Type**: Sentence Transformer (BERT-based)
- **Size**: ~87MB
- **Purpose**: Semantic similarity computation
- **Features**:
  - Efficient sentence embeddings
  - Good performance on similarity tasks
  - Optimized for CPU inference
  - Multilingual support

The model is stored locally in the models/ directory to enable offline processing without internet connectivity.

## Commands to Execute

### Prerequisites

1. **Install Dependencies**:
   ```
   pip install -r requirements.txt
2. **Verify Python Version**:
   ```
   python3 --version # Should be 3.11+
3. **Set Environment Variables for Offline Mode**:
   ```
   export HF_HUB_OFFLINE=1<br/>
   export TRANSFORMERS_OFFLINE=1
These commands ensure the application works in offline mode without attempting to download models from the internet.

# Set offline mode (if not already set)
  
  export HF_HUB_OFFLINE=1<br/>
  export TRANSFORMERS_OFFLINE=1

# Run batch processing for all cases
  
  python batch_run.py

## Docker Execution

Build and run with Docker:

### Build the container

docker build -t pdf-analyzer .

### Run the container

docker run --rm -v $(pwd)/output:/app/output pdf-analyzer

## Processing Time and Performance

### Estimated Processing Times

Based on the test cases with 7 PDF documents each:

- **Single Case Processing**: 10 seconds
- **All Three Cases**: ~30 seconds

## Dockerfile Explanation

The Dockerfile creates a containerized environment for reliable, reproducible execution:

### Base Image

dockerfile<br/>
FROM python:3.11-slim

- Uses Python 3.11 slim image for smaller footprint
- Provides stable Python environment

### System Dependencies

dockerfile<br/>
RUN apt-get update && apt-get install -y --no-install-recommends \
 gcc \
 g++ \
 libffi-dev \
 libssl-dev \
 && rm -rf /var/lib/apt/lists/\*

- **gcc/g++**: Required for compiling native Python extensions
- **libffi-dev**: For foreign function interface support
- **libssl-dev**: SSL/TLS support for secure connections
- Cleans up package cache to reduce image size

### Environment Configuration

dockerfile<br/>
ENV HF_HUB_OFFLINE=1 \
 TRANSFORMERS_OFFLINE=1 \
 PYTHONUNBUFFERED=1

- **HF_HUB_OFFLINE**: Forces Hugging Face to use local models only
- **TRANSFORMERS_OFFLINE**: Prevents online model downloads
- **PYTHONUNBUFFERED**: Ensures real-time log output

### Application Setup

dockerfile<br/>
COPY requirements.txt .<br/>
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

- Installs Python dependencies first (Docker layer caching optimization)
- --no-cache-dir: Reduces image size by not storing pip cache

### Output Directories

dockerfile<br/>
RUN mkdir -p /app/case1/output /app/case2/output /app/case3/output

- Creates output directories for results
- Ensures batch processing won't fail due to missing directories

### Execution

dockerfile<br/>
CMD ["python", "batch_run.py"]

- Automatically processes all cases when container starts

## Dependencies

### Core Libraries

- **torch** (2.2.2): PyTorch deep learning framework
- **torchvision** (0.17.2): Computer vision utilities
- **torchaudio** (2.2.2): Audio processing (model dependency)
- **sentence-transformers** (2.5.1): Semantic similarity computation
- **pymupdf** (1.23.26): PDF text extraction and processing
- **numpy** (1.26.4): Numerical computing

### Features

- **Offline Processing**: No internet required after initial setup
- **Containerized Deployment**: Consistent execution environment
- **Batch Processing**: Automated handling of multiple cases
- **Structured Output**: JSON format for easy integration
- **Semantic Analysis**: AI-powered content relevance ranking

## Use Cases

1. **Document Intelligence**: Automated extraction of relevant content
2. **Research Assistance**: Finding specific information across multiple documents
3. **Content Curation**: Identifying and ranking relevant sections
4. **Workflow Automation**: Batch processing of document collections
5. **Information Retrieval**: Semantic search within document collections count the words without including spaces and common pronouns
