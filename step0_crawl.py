import time, random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


# -----------------------
# Setting
# -----------------------
target_source = './dbaasp_dw/Monomer_10-50aa.csv'
output_folder = './mono10-50aa'
error_log = './log.txt'




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
            return str(e)

        page_source = driver.page_source
    finally:
        driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')


    # The data is likely in a sibling grid or table. 
    # Since we don't have the exact structure, we'll try to find all 'cards' or rows.
    # We will look for elements that contain "Target Species" and our specific bacteria.
    
    # Search for all elements that might be a 'row' or 'card'.
    # A robust way is to find the text "Target Species" and traverse up to its container.
    
    cols = (
        "Target Species", "Activity Measure", "Activity", "Unit", 
        "pH", "Ionic Strength mM", "Salt Type", "Medium", 
        "CFU", "Note")
    
    
    data_rows = [] #catch target information
    all_rows = soup.find_all('tr')
    all_rows=all_rows[4:-1]
    
    for row in all_rows:
            #example_cells = row.find_all(['td', 'th'], recursive=False)
            data_cells = row.find_all('td', recursive=False)
            #print(type(data_cells), len(data_cells)) #<class 'bs4.element.ResultSet'>
     
            #if not data_cells: #len(data_cells)==0
            #    continue

            if len(data_cells)>=2: 
                extracted_data = {}
                for i, col in enumerate(cols):
                    val = ""
                    if i < len(data_cells):
                        val = data_cells[i].get_text(" ", strip=True)
                    extracted_data[col] = val     
                data_rows.append(extracted_data)
                
            #collect empty rows as separater for 3 main sections:
            # 1.Activity Against Target Species 2.Hemolytic and Cytotoxic Activities 3. Synergy Between Current Peptide and Antimicrobials
            elif len(data_cells)==0:
                extracted_data = {}
                for i, col in enumerate(cols):
                    val = ""
                    if i < len(data_cells):
                        extracted_data[col] = val  
                data_rows.append(extracted_data)
                
    df = pd.DataFrame(data_rows)
    df.to_csv(f"{output_folder}/{sid}.csv", sep=",", index=False)
    print(f'save {sid}.csv')




if __name__ == "__main__":

    
    idli=[] #ex idli=['DBAASPR_8','DBAASPR_16493','DBAASPR_12']
  
    with open(target_source, 'r') as f:
        for l in f:
            l=l.strip().split(',')
            sid = l[0].lstrip('"').rstrip('"')
            if sid[0]=='I': continue
            idli.append('DBAASPR_'+sid)
    print(len(idli)) #18460

    with open(error_log, 'w') as f:
        for sid in idli:
            #print('doing',sid)
            error_catcher = get_dbaasp_data(sid) 

            if error_catcher:  
                f.write(f"sid: {sid}, Error: {error_catcher}\n")
            time.sleep(random.uniform(0.5, 0.9))
        



