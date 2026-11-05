# CSV Data Analyst Agent

An AI-powered CSV Data Analyst Agent that allows users to upload CSV files and ask questions about their data using natural language.

The application uses a Large Language Model (LLM) to understand user questions, select suitable Python analysis tools, execute operations using Pandas, and generate easy-to-understand answers.

## Features

- Upload CSV files through an interactive Streamlit interface.
- Support for common CSV encodings, including UTF-8, UTF-16, Windows-1252, and Latin-1.
- Automatic delimiter detection for comma, semicolon, tab, and pipe-separated files.
- Preview uploaded datasets.
- View dataset statistics, column information, missing values, and duplicate rows.
- Ask questions about uploaded data using natural language.
- AI-powered tool selection for data analysis.
- Perform numeric calculations such as sum, average, minimum, maximum, median, and standard deviation.
- Perform group-by analysis.
- Identify the most frequent values in a column.

## Technologies Used

- Python
- Streamlit
- Pandas
- Groq API
- Large Language Models (LLMs)
- python-dotenv

## Project Structure

```text
CSV-Data-Analyst-Agent/
│
├── app.py
├── agent.py
├── tools.py
├── sample.csv
├── employee.csv
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd CSV-Data-Analyst-Agent
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file in the project root directory and add:

```env
GROQ_API_KEY=your_groq_api_key
```

Replace `your_groq_api_key` with your own Groq API key.

**Never upload your `.env` file or expose your API key publicly.**

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## How It Works

1. The user uploads a CSV file.
2. The application reads the file using Pandas and detects its encoding and delimiter.
3. The user asks a question in natural language.
4. The LLM interprets the question and selects an appropriate Python analysis tool.
5. The selected tool performs the requested operation on the dataset.
6. The LLM converts the tool output into a clear natural-language response.

## Available Analysis Tools

| Tool | Description |
|---|---|
| `get_dataset_overview` | Retrieves dataset dimensions, columns, data types, and missing values. |
| `get_column_summary` | Provides a summary of a selected column. |
| `analyze_numeric_column` | Performs numeric calculations. |
| `group_by_analysis` | Performs grouped calculations. |
| `get_top_values` | Identifies the most frequent values. |

## Example Questions

- How many rows and columns are present in the dataset?
- What is the total sales amount?
- What is the average salary?
- Which category has the highest total sales?
- Which department has the highest average salary?
- What are the most common values in the Category column?

## Sample Dataset

The project includes sample CSV datasets for testing and demonstration.

## Future Enhancements

- Support for additional file formats.
- More advanced statistical analysis.
- Data visualization through interactive charts.
- Improved handling of complex analytical questions.
- Additional data-cleaning and preprocessing capabilities.

## Author

**A. Srinivas**
