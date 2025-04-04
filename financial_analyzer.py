import os
import json
import re
from collections import defaultdict
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
import sqlite3

DB_FILE = "financial_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS financial_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        year TEXT,
        quarter TEXT,
        category TEXT,
        subfield TEXT,
        value TEXT
    )
    ''')
    conn.commit()
    conn.close()

def insert_financial_data(company, year, quarter, category, subfield, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO financial_info (company, year, quarter, category, subfield, value)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (company, year, quarter, category, subfield, value))
    conn.commit()
    conn.close()

class FinancialAnalyzerLocal:
    def __init__(self):
        self.llm = OpenAI(model="gpt-3.5-turbo", max_tokens=512)

        self.index = LlamaCloudIndex(
            name="Apple",
            project_name="Default",
            organization_id="64ca1621-fce5-4052-971f-524e394a3008",
            api_key=os.getenv("LLAMA_CLOUD_API_KEY")
        )

        retriever_lvl1 = self.index.as_retriever(retrieval_mode="files_via_content", files_top_k=1)
        self.engine_lvl1 = RetrieverQueryEngine.from_args(retriever_lvl1, llm=self.llm, response_mode="tree_summarize")

        retriever_lvl2 = self.index.as_retriever(retrieval_mode="chunks", similarity_top_k=5)
        self.engine_lvl2 = RetrieverQueryEngine.from_args(retriever_lvl2, llm=self.llm, response_mode="tree_summarize")

        init_db()

    def extract_quarters(self):
        prompt = """
        Carefully analyze the full content of all documents and extract every unique fiscal quarter and year with financial information.

        Follow this process step-by-step:

        1. First, identify all date mentions that indicate the end of a fiscal quarter. These often appear in phrases like:
        - "For the quarterly period ended March 31, 2021"
        - "Three months ended June 30, 2022"
        - "Quarter ended September 30, 2023"
        - "For the quarter ended December 28, 2024"

        2. Extract the dates from those phrases and convert them into fiscal quarters based on these rules:
        - January 1 to March 31 → Q1
        - April 1 to June 30 → Q2
        - July 1 to September 30 → Q3
        - October 1 to December 31 → Q4

        3. From each date, determine the correct year and quarter, and generate a list like:
        ["Q1 2021", "Q2 2021", ..., "Q4 2024"]

        4. Also include any quarters mentioned explicitly (e.g., "Q2 2023") even if a date isn't associated.

        Return a **Python list of unique** quarter-year strings in that format, sorted by year and quarter.
        """

        response = self.engine_lvl1.query(prompt)
        matches = re.findall(r'Q[1-4]\s20\d{2}', str(response))
        all_quarters = sorted(set(matches), key=lambda x: (x.split()[1], x.split()[0]))

        grouped = defaultdict(list)
        for q in all_quarters:
            quarter, year = q.split()
            grouped[year].append(quarter)

        return grouped


    def extract_financials(self, company: str, quarter: str):#TODO add Year
        year = quarter.split()[1]
        prompt = f"""
        Provide Apple's financial metrics for {quarter} in the following JSON format:
        {{
          "revenue": {{"value": ..., "growth_percentage": ...}},
          "gross_profit": {{"value": ..., "margin": ...}},
          "ebitda": {{"value": ..., "margin": ...}},
          "net_income": {{"value": ..., "margin": ...}}
        }}
        All values should be numeric and in millions USD.
        Percentages should be returned as raw numbers, without the % symbol.
        If a value is missing or not found, use "-".
        """
        response = self.engine_lvl1.query(prompt)
        print(f"\n📊 Level 1 Financials for {quarter}:")
        try:
            data = json.loads(str(response))
            print(json.dumps(data, indent=2))
            for category, subfields in data.items():
                for sub, value in subfields.items():
                    insert_financial_data(company, year, quarter.split()[0], category, sub, str(value))
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON from response:\n", response)

    def extract_balance_sheet(self, company: str, quarter: str):
        year = quarter.split()[1]
        prompt = f"""
        Provide Apple's balance sheet asset breakdown for {quarter} in the following JSON format:
        {{
          "cash_and_cash_equivalents": ..., "st_investments": ..., "accounts_receivable_net": ..., "notes_receivable_net": ..., 
          "inventories_total": ..., "raw_materials": ..., "work_in_process": ..., "finished_goods": ..., "other_inventory": ...,
          "prepaid_expenses": ..., "derivative_and_hedging_assets_current": ..., "misc_st_assets": ..., "total_current_assets": ...,
          "property_plant_equipment_net": ..., "property_plant_equipment_gross": ..., "accumulated_depreciation": ..., "lt_receivables": ..., 
          "other_lt_assets": ..., "intangible_assets_total": ..., "goodwill": ..., "other_intangible_assets": ...,
          "deferred_tax_assets": ..., "derivative_and_hedging_assets_noncurrent": ..., "misc_lt_assets": ..., "total_noncurrent_assets": ..., 
          "total_assets": ...
        }}
        Values should be numeric in millions USD. If a value is missing or not found in the data, return "-".
        """
        response = self.engine_lvl2.query(prompt)
        print(f"\n📊 Level 2 Balance Sheet for {quarter}:")
        try:
            data = json.loads(str(response))
            print(json.dumps(data, indent=2))
            for category, value in data.items():
                insert_financial_data(company, year, quarter.split()[0], category, "value", str(value))
        except json.JSONDecodeError:
            print("❌ Failed to parse JSON from response:\n", response)

if __name__ == "__main__":
    analyzer = FinancialAnalyzerLocal()
    quarters_by_year = analyzer.extract_quarters()
    for year, quarters in quarters_by_year.items():
        print(f"\n📅 Year: {year}")
        for q in quarters:
            quarter = f"{q} {year}"
            analyzer.extract_financials("Apple", quarter)
            analyzer.extract_balance_sheet("Apple", quarter)
