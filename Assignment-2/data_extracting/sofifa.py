import pandas as pd

html_file = r"C:\Users\sukuh\Downloads\AIML\assignment_2\fifaranking.html"
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()
tables = pd.read_html(html_content)
fifa_table = tables[0]
fifa_table.to_csv('fifaranking.csv', index=False)

