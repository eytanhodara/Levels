# LAMA Cloud Financial Analysis

This project uses LAMA Cloud to analyze financial data from PDF documents. It provides capabilities for:
- Processing financial PDFs
- Extracting financial data
- Analyzing company metrics
- Generating insights and reports

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
Create a `.env` file with your LAMA Cloud API credentials:
```
LAMA_CLOUD_API_KEY=your_api_key_here
```

## Usage

1. Place your financial PDFs in the `input` directory
2. Run the analysis:
```bash
python main.py
```

## Project Structure

- `main.py`: Main entry point
- `src/`: Source code directory
  - `pdf_processor.py`: PDF processing module
  - `financial_analyzer.py`: Financial data analysis module
  - `report_generator.py`: Report generation module
- `input/`: Directory for input PDFs
- `output/`: Directory for generated reports # Levels
