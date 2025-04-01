import os
import json
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI

class FinancialAnalyzerLocal:
    def __init__(self):
        # Step 1: Choose LLM
        self.llm = OpenAI(
            model="gpt-3.5-turbo",  # or "gpt-4" / "gpt-4o-mini", etc.
            max_tokens=512
        )
        
        # Step 2: Connect to LlamaCloudIndex
        self.index = LlamaCloudIndex(
            name="Apple",
            project_name="Default",
            organization_id="64ca1621-fce5-4052-971f-524e394a3008",
            api_key=os.getenv("LLAMA_CLOUD_API_KEY")
        )
        
        # Step 3: Build Level 1 retriever (Income Statement)
        retriever_lvl1 = self.index.as_retriever(
            retrieval_mode="chunks",
            rerank_top_n=5
        )
        self.engine_lvl1 = RetrieverQueryEngine.from_args(
            retriever_lvl1,
            llm=self.llm,
            response_mode="tree_summarize"
        )
        
        # Step 4: Build Level 2 retriever (Balance Sheet)
        retriever_lvl2 = self.index.as_retriever(
            retrieval_mode="chunks",
            rerank_top_n=5
        )
        self.engine_lvl2 = RetrieverQueryEngine.from_args(
            retriever_lvl2,
            llm=self.llm,
            response_mode="tree_summarize"
        )

    def extract_financials(self, company: str, quarter: str):
        """Level 1: Income Statement"""
        prompt = f"""
        Look at Apple's official 10-Q for {quarter} and provide the following JSON:
        {{
          "revenue": {{"value": ..., "growth_percentage": ...}},
          "gross_profit": {{"value": ..., "margin": ...}},
          "ebitda": {{"value": ..., "margin": ...}},
          "net_income": {{"value": ..., "margin": ...}}
        }}
        All values should be numeric in millions USD.
        Percentages as raw numbers (no '%').
        If data is missing, use "-".
        """
        
        response = self.engine_lvl1.query(prompt)
        
        # Print the first chunk
        if response.source_nodes:
            print("\n🔎 [Level 1] First retrieved chunk:\n")
            print(response.source_nodes[0].text)
        
        # Attempt to parse JSON
        try:
            data = json.loads(str(response))
            print("\n✅ Level 1 Financials:")
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print("\n❌ Failed to parse JSON from response:\n", response)

    def extract_balance_sheet(self, company: str, quarter: str):
        """Level 2: Balance Sheet with 14 categories (each category has 'value' + sub-items)"""
        prompt = f"""
        Look at Apple's official 10-Q for {quarter} and return the balance sheet as JSON
        with the following structure (each category has a total 'value' plus optional sub-items):

        {{
          "cash_cash_equivalents_sti": {{
            "value": "...",
            "cash_equivalents": "...",
            "st_investments": "..."
          }},
          "accounts_notes_receiv": {{
            "value": "...",
            "accounts_receivable_net": "...",
            "notes_receivable_net": "..."
          }},
          "inventories": {{
            "value": "...",
            "raw_materials": "...",
            "work_in_process": "...",
            "finished_goods": "...",
            "other_inventory": "..."
          }},
          "other_st_assets": {{
            "value": "...",
            "prepaid_expenses": "...",
            "derivative_hedging_assets": "...",
            "misc_st_assets": "..."
          }},
          "total_current_assets": "...",
          "property_plant_equip_net": {{
            "value": "...",
            "property_plant_equip": "...",
            "accumulated_depreciation": "..."
          }},
          "lt_investments_receivables": {{
            "value": "...",
            "lt_receivables": "..."
          }},
          "other_lt_assets": {{
            "value": "..."
          }},
          "total_intangible_assets": {{
            "value": "...",
            "goodwill": "...",
            "other_intangible_assets": "..."
          }},
          "deferred_tax_assets": {{
            "value": "..."
          }},
          "derivative_hedging_assets_noncurrent": {{
            "value": "..."
          }},
          "misc_lt_assets": {{
            "value": "..."
          }},
          "total_noncurrent_assets": "...",
          "total_assets": "..."
        }}

        For each item, return numeric values in millions USD, or "-" if missing.
        """
        
        response = self.engine_lvl2.query(prompt)
        
        # Print the first chunk
        if response.source_nodes:
            print("\n🔎 [Level 2] First retrieved chunk:\n")
            print(response.source_nodes[0].text)
        
        # Attempt to parse JSON
        try:
            data = json.loads(str(response))
            print("\n✅ Level 2 Balance Sheet:")
            print(json.dumps(data, indent=2))
        except json.JSONDecodeError:
            print("\n❌ Failed to parse JSON from response:\n", response)

if __name__ == "__main__":
    analyzer = FinancialAnalyzerLocal()
    analyzer.extract_financials("Apple", "Q4 2024")
    analyzer.extract_balance_sheet("Apple", "Q4 2024")
