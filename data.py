import os
import pandas as pd
from bs4 import BeautifulSoup

def list_html_files():
    """Return a list of .html files in the current directory."""
    return [f for f in os.listdir('.') if f.endswith('.html') and not f.startswith('.')]

def load_player_data(filename='All_Players.html'):
    """Load and parse the given HTML file (default: All_Players.html)"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        table = soup.find('table')
        
        if not table:
            return pd.DataFrame()
        
        # Extract headers
        headers = []
        header_row = table.find('tr', bgcolor="#EEEEEE")
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
        
        # Extract data rows
        data_rows = []
        for row in table.find_all('tr', bgcolor="#EEEEEE")[1:]:  # Skip header row
            cells = row.find_all('td')
            if len(cells) == len(headers):
                row_data = [cell.get_text(strip=True) for cell in cells]
                data_rows.append(row_data)
        
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Convert numeric columns
        numeric_columns = ['Aer A/90', 'Asts/90', 'Blk/90', 'Ch C/90', 'Clr/90', 'Crs A/90', 
                          'Cr C/90', 'Dist/90', 'Drb/90', 'xA/90', 'Hdrs L/90', 'Hdrs W/90',
                          'Sprints/90', 'Int/90', 'K Hdrs/90', 'K Ps/90', 'K Tck/90', 'NP-xG/90',
                          'OP-Crs A/90', 'OP-Crs C/90', 'OP-KP/90', 'Ps A/90', 'Ps C/90',
                          'Poss Lost/90', 'Poss Won/90', 'Pres A/90', 'Pres C/90', 'Pr passes/90',
                          'Shots Outside Box/90 ', 'ShT/90', 'Shot/90', 'Tck/90', 'xG']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].replace(['-', '', 'nan', 'NaN'], '0')
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame() 