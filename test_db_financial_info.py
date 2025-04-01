
from financial_analyzer import DB_FILE, init_db, insert_financial_data


import sqlite3

def get_data(company, year, quarter, category, subfield):
    conn = sqlite3.connect("financial_data.db")
    c = conn.cursor()
    c.execute("""
        SELECT value FROM financial_info 
        WHERE company = ? AND year = ? AND quarter = ? AND category = ? AND subfield = ?
    """, (company, year, quarter,category, subfield))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Example usage
print("Revenue in Q3 2024:", get_data("Apple", "2024", "Q1","ebitda","margin"))
