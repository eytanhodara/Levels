from financial_analyzer import FinancialAnalyzerLocal

def test_extract_financials():
    analyzer = FinancialAnalyzerLocal()
    print("🔍 Testing Level 1 Financials (Income Statement)...\n")
    analyzer.extract_financials("Apple", "Q4 2024")

def test_extract_balance_sheet():
    analyzer = FinancialAnalyzerLocal()
    print("\n🔍 Testing Level 2 Balance Sheet...\n")
    analyzer.extract_balance_sheet("Apple", "Q4 2024")

if __name__ == "__main__":
    test_extract_financials()
    test_extract_balance_sheet()
