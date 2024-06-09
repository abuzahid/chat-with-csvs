# chat-with-csvs

## Overview
`chat-with-csvs` is a tool designed to help you interact with and analyze CSV files through a user-friendly interface powered by Streamlit.

## Installation
To get started, you need to install all the necessary dependencies. Ensure you have Python installed on your system, then run the following command:

```bash
pip install -r requirements.txt
```
## Usage
Prepare Your Data:
keep a .env file with the following information:
GROQ_API_KEY=your groq api key
GROQ_MODEL="llama3-8b-8192" or you can choose any other model

Place all the CSV files you want to analyze in the **data** directory.
Run the Application:

Launch the application by running the following command in your terminal:

```bash
streamlit run app.py
```
Directory Structure
The project directory should look something like this:

```
chat-with-csvs/
│
├── data/
│   ├── your-file-1.csv
│   ├── your-file-2.csv
│   └── ...
│
├── app.py
├── .env
├── requirements.txt
├── README.md
└── ...
```
Notes
Ensure that the CSV files are properly formatted and placed in the data directory for the application to function correctly.
Customize app.py as needed to tailor the application to your specific requirements.
