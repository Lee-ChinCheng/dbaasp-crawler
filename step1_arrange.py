import streamlit as st
import os, csv

# streamlit run step1_arrange.py



inp_f='/mono10-50aa'
op_folder='output_csv/'
#--------------------------------------


# -----------------------------
# Core filtering function
# -----------------------------
def csvfilter(inp_f, kw_list):
    all_results=[]
    dbid_d, seq_d , sid = {},{}, 0
    gram_add = gram_minus = gram_both =0
    try:
        fli = [f for f in os.listdir(inp_f) if f.endswith('.csv')] #print(len(fli)) #18460
        for csvf in fli :
            dbid=csvf.split('.')[0]   
            with open(inp_f+'/'+csvf, newline="") as f:
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

# File uploader
#uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Output filename input
output_filename = st.text_input("Output file name (e.g. result)", "result")

# Keywords input (comma separated)
keywords_input = st.text_input("Enter keywords (comma separated) ex: fumigatus,fumigata,fumigatum", 
                               "Cryptococcus,neoforman")

# Convert to list
kw_list = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
kw_list = tuple(kw_list)

# Run button
if st.button("Run Filtering"):
    
    if not output_filename:
        st.error("Please enter output_filename.")
    elif not kw_list:
        st.error("Please enter at least one keyword.")
    else:

        # Run filter     
        opli = csvfilter(inp_f, kw_list)
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

            st.success(f"Filtering complete!\n get {data_am} data, {seq_am} unique sequence.")


        else:
            st.error("Error")