import streamlit as st
import os, csv
from aliasLLM import ask_ollama

# command: streamlit run step1_arrange.py

# -----------------------
# Setting
# -----------------------
inp_folder = './mono10-50aa'
#inp_folder = '/home/cclee/DBAASP/mono10-50aa_new' #loacl testing
op_folder = './output_csv'






# -----------------------------
# Core filtering function
# -----------------------------
def csvfilter(inp_folder, kw_list):
    all_results=[]
    dbid_d, seq_d , sid = {},{}, 0
    gram_add = gram_minus = gram_both =0
    d_filter=('','NA','na','-',None) #dosage information
    try:
        fli = [f for f in os.listdir(inp_folder) if f.endswith('.csv')] #print(len(fli)) #18460
        #fli = ('DBAASPR_2229.csv', 'DBAASPR_2261.csv', 'DBAASPR_22431.csv', 'DBAASPR_19645.csv', 'DBAASPR_13887.csv')

        for csvf in fli :
            dbid=csvf.split('.')[0]   
            with open(inp_folder+'/'+csvf, newline="") as f:
                switch=row_cunt=0
                reader = csv.reader(f)
                for row in reader:
                    row_cunt+=1

                    if row[0].startswith("Target Group"):        
                        gram = row[1]
                    if row[0].startswith("DBAAS"):
                        #DBAASPS_12001,"3,5 Bis-(Me)Tol",lkkklkclckllkkll,,16,,,,,
                        seq = row[2]
                    if row[0] == 'InterPro':
                        switch = 1
                        bs_row = row_cunt
                        

                    if (switch==1) and (row_cunt >= bs_row+3):

                       
                        # if row[0]=='': #display False in UI is weird. replace by if text=='':
                        text = row[0].lower()
                        if text=='':
                            switch==0 #double confirm
                            break

                        found = any(kw in text for kw in kw_list)            
                        if found: #if key word in text:
                            if row[1] in d_filter or row[2] in d_filter or row[3] in d_filter:
                                continue
                        
                            row.insert(0, dbid)
                            row.insert(0, seq)
                            row.append(gram)
                            
                            #['DBAASPR_8', 'KVvvKWVvKvVK', 'Acinetobacter baumannii ATCC 19606', 'MIC', '>100', 'µM', '', '', '', 'LBB', '1E6', '','Gram+, Gram-']
                            if len(row) != 13:
                                #print('len(row) != 13', row)
                                continue
                                                  
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
        return ( all_results, seq_d )

    except Exception as e:
        return str(e)


# -----------------------------
# Streamlit UI
# -----------------------------
st.title("DBAASP data arranger")



st.markdown(
    '<span style="color:orange; font-size:22px; font-weight:bold;">< step 1 ></span> '
    '<span style="font-size:18px;">Output file name</span>',
    unsafe_allow_html=True
)
output_filename = st.text_input("(e.g. result)", "result")

st.markdown(
    '<span style="color:orange; font-size:22px; font-weight:bold;">< step 2 (optional)></span> '
    '<span style="font-size:18px;">Search alias names for biological term</span>',
    unsafe_allow_html=True
)
alias_input = st.text_input("(e.g. Candida albicans) this step help you define the target keywords", "")


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


st.markdown(
    '<span style="color:orange; font-size:22px; font-weight:bold;">< step 3 ></span> '
    '<span style="font-size:18px;">Enter keywords (comma separated)</span>',
    unsafe_allow_html=True
)
keywords_input = st.text_input("(e.g. fumigatus,fumigata,fumigatum or ATCC,KCTC)", 
                               "")
# Convert to list
kw_list = tuple(kw.strip().lower() for kw in keywords_input.split(",") if kw)


# Run button
if st.button("Data Filtering"):
    # Check if directory exists
    if not os.path.exists(inp_folder):
        st.error(f"Directory not found: {inp_folder}")
        st.stop()
    
    # Optional: check if it's actually a directory
    if not os.path.isdir(inp_folder):
        st.error(f"Path exists but is not a directory: {inp_folder}")
        st.stop()
    
    # If everything is OK
    st.success("Datasource ./mono10-50aa exists. Proceeding with data filtering...")
    
    if not output_filename:
        st.error("Please enter output_filename.")
    elif not kw_list:
        st.error("Please enter at least one keyword of Target Species.")
    else:

        # Run filter     
        opli = csvfilter(inp_folder, kw_list)  
        all_result_list = opli[0]
        data_am = len(all_result_list)
        data_am-=1
        seq_am = len(opli[1])

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
