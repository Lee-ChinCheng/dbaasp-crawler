import streamlit as st
import os, csv
from aliasLLM import ask_ollama

# command: streamlit run step1_arrange.py


inp_folder = '/mono10-50aa'
#inp_folder = '/home/cclee/DBAASP/mono10-50aa' #testing
op_folder = './output_csv'
#--------------------------------------





# -----------------------------
# Core filtering function
# -----------------------------
def csvfilter(inp_folder, kw_list):
    all_results=[]
    dbid_d, seq_d , sid = {},{}, 0
    gram_add = gram_minus = gram_both =0
    try:
        fli = [f for f in os.listdir(inp_folder) if f.endswith('.csv')] #print(len(fli)) #18460
        for csvf in fli :
            dbid=csvf.split('.')[0]   
            with open(inp_folder+'/'+csvf, newline="") as f:
                switch=0
                reader = csv.reader(f)
                for row in reader:
                    if row[0].startswith("Target Group"):        
                        gram = row[1]
                    if row[0].startswith("DBAAS"):
                        #DBAASPS_12001,"3,5 Bis-(Me)Tol",lkkklkclckllkkll,,16,,,,,
                        seq = row[2]
                    if row[0] == 'InterPro':
                        switch=1
                    if switch==1:
                        text = row[0].lower()
                        found = any(kw in text for kw in kw_list)            
                        if found: #if key word in text:
                            row.insert(0, dbid)
                            row.insert(0, seq)
                            row.append(gram)
                            
                            #['DBAASPR_8', 'KVvvKWVvKvVK', 'Acinetobacter baumannii ATCC 19606', 'MIC', '>100', 'µM', '', '', '', 'LBB', '1E6', '','Gram+, Gram-']
                            if len(row) != 13:
                                print('len(row) != 13', row)
                                
                            if dbid not in dbid_d: 
                                dbid_d[dbid]=None
                            if seq not in seq_d: 
                                seq_d[seq]=[dbid]
                                sid+=1
                                row.insert(0, sid)                            
                            else:
                                seq_d[seq].append(dbid)
                                row.insert(0, sid)
                            if 'Gram+' in gram: gram_add+=1
                            if 'Gram-' in gram: gram_minus+=1
                            if ('Gram+' in gram) and ('Gram-' in gram): gram_both+=1
                            all_results.append(row)
        #print(len(all_results), len(dbid_d), len(seq_d), gram_add , gram_minus , gram_both)
        return ( all_results, len(seq_d) )

    except Exception as e:
        return str(e)


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("DBAASP data arranger")




output_filename = st.text_input("< step 1 >  Output file name (e.g. result)", "result")

alias_input = st.text_input("< step 2 (optional) >  Search alias names for biological term (e.g. Candida albicans)\n help you define the target keywords", "")


# Initialize session state so alias_search & filter_result stay independent
if "alias_result" not in st.session_state:
    st.session_state.alias_result = None


# Button 1: 
if st.button("Alias_Searching"):
    if not alias_input:
        st.error("Please enter a biological term.")
    else:
        st.session_state.alias_result = ask_ollama(alias_input)

# Display space 1
st.subheader("Alias Result")
if st.session_state.alias_result is not None:
    st.write(st.session_state.alias_result)
else:
    st.write("No alias result yet.")


# Keywords input (comma separated)
keywords_input = st.text_input("< step 3 >  Enter keywords (comma separated) ex: fumigatus,fumigata,fumigatum,ATCC,KCTC", 
                               "")
# Convert to list
kw_list = tuple(kw.strip().lower() for kw in keywords_input.split(",") if kw)


# Run button
if st.button("Data Filtering"):
    
    if not output_filename:
        st.error("Please enter output_filename.")
    elif not kw_list:
        st.error("Please enter at least one keyword.")
    else:

        # Run filter     
        opli = csvfilter(inp_folder, kw_list)
        all_result_list = opli[0]
        seq_am = opli[1]
        data_am = len(all_result_list)

        if isinstance(data_am, int):

            header = [
                'Seq_ID','Seq','DB_ID','Target Species', 'Activity Measure', 'Activity',
                'Unit', 'pH', 'Ionic Strength mM', 'Salt Type',
                'Medium', 'CFU', 'Note','Gram'
            ]

            with open(f'{op_folder}/{output_filename}.csv', "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(all_result_list)

            st.success(f"Filtering and saveing complete!\n get {data_am} data, {seq_am} unique sequence.")

        else:
            st.error("Error")
