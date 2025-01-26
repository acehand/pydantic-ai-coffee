# Pydantic Coffee API

A FastAPI-based coffee shop order management system with Pydantic validation, pandas data handling, and AI-powered order analysis.

## Features

- 🛠️ Built with FastAPI, Pydantic, and pandas
- 📊 CSV-based order storage and analysis
- ✨ AI-powered order pattern detection
- 🔍 Advanced querying capabilities
- 🚀 Real-time order validation
- 📈 Order analytics and trends

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pydantic_coffee

# Create virtual environment
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

### Usage

```bash
# Run the FastAPI server
    uvicorn pydantic_coffee.main:app --reload
```

### Requirements
  - Python ≥ 3.9
  - FastAPI
  - Pydantic
  - pandas
  - logfire
  - uvicorn
  - pydantic-ai

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```