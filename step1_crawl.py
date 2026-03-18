
import time, random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


def get_dbaasp_data(dbaasp_id):
    url = f"https://www.dbaasp.org/peptide-card?id={dbaasp_id}"
    print(f"Fetching data from: {url}")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # mimicking a real browser to avoid bot detection if any
    chrome_options.add_argument("user-agent=Mozilla/6.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        
        # Wait specifically for the 'Target Species' text to ensure the relevant section is loaded
        # The page is heavy, give it some time.
        wait = WebDriverWait(driver, 20)
        try:
             # Wait until the specific target string is present, or at least the section header
            wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Activity Against Target')]")))
            time.sleep(2) # Extra buffer for complete rendering
        except Exception as e:
            print(f"Timeout waiting for page to load or section not found: {e}")
            return None

        page_source = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    # Strategy: Find the header "Activity Against Target Species"
    # Then look for the container following it.
    
    # Based on general observation of such sites, key headers are often in h3, h4, or strong tags.
    # Let's find the element containing the text.
    header = soup.find(lambda tag: tag.name in ['h3', 'div', 'span'] and 'Activity Against Target' in tag.get_text())
    
    if not header:
        print("Could not find 'Activity Against Target Species' section.")
        return None

    # The data is likely in a sibling grid or table. 
    # Since we don't have the exact structure, we'll try to find all 'cards' or rows.
    # We will look for elements that contain "Target Species" and our specific bacteria.
    
    # Search for all elements that might be a 'row' or 'card'.
    # A robust way is to find the text "Target Species" and traverse up to its container.
    
    cols = [
        "Target Species", "Activity Measure", "Activity", "Unit", 
        "pH", "Ionic Strength mM", "Salt Type", "Medium", 
        "CFU", "Note"
    ]
    
    data_rows = []
    
    all_rows = soup.find_all('tr')
    all_rows=all_rows[4:-1]

    for row in all_rows:
        #row_text = row.get_text(" ", strip=True)

            #cells = row.find_all(['td', 'th'], recursive=False)
            data_cells = row.find_all('td', recursive=False)
            
            
            if not data_cells:
                continue
            #print(len(data_cells))
            #print(data_cells)
                
            #first_cell_text = data_cells[0].get_text(strip=True)
            # Loose match check to avoid partial matches if necessary, 
            # but user query is specific. 
            
            extracted_data = {}
            for i, col in enumerate(cols):
                val = ""
                if i < len(data_cells):
                    val = data_cells[i].get_text(" ", strip=True)
                extracted_data[col] = val
            
            data_rows.append(extracted_data)

    df = pd.DataFrame(data_rows)
    df.to_csv(f"/home/cclee/DBAASP/crawl2/op/{sid}.csv", sep=",", index=False)
    print(f'save {sid}.csv')







if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description='Scrape DBAASP Peptide Data')
    #parser.add_argument('--id', type=str, required=True, help='DBAASP ID (e.g., DBAASPR_3)')
    #args = parser.parse_args()
    # python DBAASP/crawl2/selen.py --id DBAASPR_3

    idli=[]
    #idli = ['DBAASPR_8','DBAASPR_11','DBAASPR_12']
    with open('DBAASP/Monomer_10-50aa.csv', 'r') as f:
        for l in f:
            l=l.strip().split(',')
            sid = l[0].lstrip('"').rstrip('"')
            if sid[0]=='I': continue
            idli.append('DBAASPR_'+sid)
    print(len(idli)) #18460
    #print(idli[:5])


    for sid in idli:
        print(sid)
        get_dbaasp_data(sid)     
        time.sleep(random.uniform(0.4, 1.0))
        
        #if df is not None and not df.empty:
        #    print(df.to_string())
        #else:
        #    print("No data found for the specified target species.")





# python DBAASP/crawl2/selen.py --id DBAASPR_3
#                    Target Species Activity Measure Activity   Unit pH Ionic Strength mM Salt Type Medium  CFU Note Reference
#0  Enterococcus faecium CCARM 5029              MIC       64  µg/ml                                   MHB  2E5  VRE         2
#1  Enterococcus faecium CCARM 5029              MIC      >64  µg/ml                  150      NaCl    MHB  2E5  VRE         2
