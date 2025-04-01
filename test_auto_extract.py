from financial_analyzer import FinancialAnalyzerLocal

def test_auto_extraction():
    print("✅ Testing quarter detection...")
    analyzer = FinancialAnalyzerLocal()
    quarters_by_year = analyzer.extract_quarters()

    assert isinstance(quarters_by_year, dict), "Quarters should be returned as a dict"
    assert all(isinstance(k, str) and isinstance(v, list) for k, v in quarters_by_year.items()), "Each year should map to a list of quarters"

    print("✅ Quarter extraction test passed.")

    # Now actually extract and print the JSONs
    for year, quarters in quarters_by_year.items():
        print(f"\n📅 Year: {year}")
        for q in quarters:
            quarter = f"{q} {year}"
            print(f"\n--- {quarter} ---")
            analyzer.extract_financials("Apple", quarter)
            analyzer.extract_balance_sheet("Apple", quarter)

if __name__ == "__main__":
    test_auto_extraction()
