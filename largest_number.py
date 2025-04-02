import pdfplumber
import os
import sys


# surpress pdfplumber warnings to stderr
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

def is_num(s):
    """ Args: 
            s (str): a string of any characters.
        Returns:
            True if `s` is a number, false otherwise.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def to_num(s):
    """ Args: 
        s (str): String of any characters.
    Returns:
        float(`s`) if `s` is a number, otherwise `s`.
    """
    try:
        cleaned_s = s.replace(',','')
        return float(cleaned_s)
    except ValueError:
        return s

big_nums = {
    'thousand' : 1000,
    'million' : 1000000,
    'billion' : 1000000000
}

def page_max(page):
    """Args: 
        page (pdfplumber.page.Page object) : A page from the pdf to be scanned.
    Returns:
        max number found on page. Will convert numbers such as '10 million' to 10_000_000 or '50 thousand' to 50_000. 
    """        
    text = page.extract_text()
    words = text.split()
    cleaned_words = [w.strip("():$") for w in words]
    with_nums = [to_num(s) for s in cleaned_words]
    last_val = None
    for i, val in enumerate(with_nums):
        if val in big_nums and is_num(last_val):
            with_nums[i-1] = last_val * big_nums[val]
        last_val = val
    try:
        m = max([n for n in with_nums if is_num(n)])
    except ValueError: # There are no numbers on the page, so `max` raises an Error. 
        m = 0
    return m

def multiplier(page):
    """Args: 
        page (pdfplumber.page.Page object) : A page from the pdf to be scanned.
    Returns:
        int: 1 million if "Dollars in Millions" or "$ IN MILLIONS" is on the page.
        int: 1 thousand if "Dollars in Thousands" is on the page.
        int: 1 otherwise. 
    """
    text = page.extract_text()
    if "Dollars in Millions" in text or "$ IN MILLIONS" in text:
        return 1_000_000
    elif "Dollars in Thousands" in text or "$ IN THOUSANDS" in text:
        return 1_000
    else:
        return 1

def tables_max(page):
    """Args:
        page (pdfplumber.page.Page object) : A page from the pdf to be scanned.
    Returns: 
        float: maximum value found in a table.    
    """
    tables = page.extract_tables()
    if not tables: # `page` does not have tables
        return 0
    max = 0
    for table in tables:
        for row in table:
            for cell in row: 
                if cell: # Assert `cell` is not None
                    clean_cell = cell.strip("():$ ").replace(',', '')
                    if is_num(clean_cell):
                        cell_val = to_num(clean_cell) * multiplier(page)
                        if cell_val > max:
                            max = cell_val
    return max

def scan(pdf):
    """
    `scan` looks for the highest number found in text, the highest number found in the tables, 
    and prints the max of all. Adjusts for text occurences of 'millions' and 'thousands'.
    Also prints the page number that the value was found on.  
    
    Args:
        pdf (pdfplumber.pdf.PDF object) : The pdf to be scanned.
    Returns: None
    """ 
    table_maxes = [(p.page_number, tables_max(p)) for p in pdf.pages]
    page_maxes = [(p.page_number, page_max(p)) for p in pdf.pages]
    page_num, val = max(page_maxes + table_maxes, key=lambda x : x[1])
    
    print(f"The largest number found was {val}.")
    print(f"The number was found on page {page_num}.")
    

if __name__ == "__main__":
    with pdfplumber.open('FY25 Air Force Working Capital Fund.pdf') as pdf:
        scan(pdf)
        pdf.close()
    

