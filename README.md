# Data Analyst AI


An AI-powered tool that analyzes Excel/CSV files and answers natural language questions about your data using LLM (Llama3 via Groq).


## Features

-  Analyze any Excel/CSV file structure automatically
-  Ask natural language questions about your data
-  Get accurate answers with calculations
-  Multi-sheet Excel file support
-  Conversational interface with history

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/data-analyst-ai.git
   cd data-analyst-ai
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

## Usage

1. Run the application:
   ```bash
   streamlit run main.py
   ```

2. Upload your Excel/CSV file
3. Ask questions like:
   - "What's the average salary by department?"
   - "Show total sales by month"
   - "Which employee has the highest sales?"

## Example Questions

| Question | Example Answer |
|----------|----------------|
| "How many employees in Finance?" | "1 (John Smith)" |
| "What's the total January sales?" | "$37,300" |
| "Who has 'Needs Improvement' feedback?" | "John Smith" |

## Project Structure

```
data-analyst-ai/
├── main.py            # Streamlit application
├── llm_handler.py     # LLM interaction logic
├── data_analyzer.py   # Data processing core
├── requirements.txt   # Dependencies
├── README.md          # This file
└── .env.example       # Environment template
```

## Requirements

- Python 3.9+
- Groq API key (free tier available)
- Libraries in `requirements.txt`

## Contributing

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

MOnirul Islamm - md08monirul@gmail.com

Project Link: https://github.com/MonirulIslamm08/data-analyst-ai
