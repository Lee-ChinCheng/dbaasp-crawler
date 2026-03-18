import csv, os
import pandas as pd
#from tabulate import tabulate


###=== setting ======

file_name = 'breast' #'breast'#'Cryptococcus' #'Microsporum' #'mentagrophyte' #'fumigatus' #'albicans'


# file_name and relative key words for searching
keyword_dict={
    'albicans':('albicans',), #念珠菌
    'fumigatus':('fumigatus', 'fumigata', 'fumigatum'), #煙麴菌
    'mentagrophyte':('mentagrophyte', 'Trichophyton', 'Arthroderma'), #毛癬菌
    'Microsporum':('Microsporum','Microsporon','Grubyella','Achorion'), #小孢子菌
    'Cryptococcus':('Cryptococcus','neoforman'), #隱球菌

    'breast':('breast',)
}


inp_folder='/home/cclee/DBAASP/mono10-50aa'
op_folder='/home/cclee/DBAASP/dbaasp-crawler/output_csv/'
#=======================================================



fli = [f for f in os.listdir(inp_folder) if f.endswith('.csv')] #print(len(fli)) #18460
all_results=[]
dbid_d, seq_d , sid = {},{}, 0
gram_add = gram_minus = gram_both =0
kw_list = [kw.lower() for kw in keyword_dict[file_name]]
print(kw_list)

for csvf in fli :
    dbid=csvf.split('.')[0]  
    with open(inp_folder+'/'+csvf, newline="") as f:
        switch=0
        reader = csv.reader(f)
        for row in reader:
            seq_id = row[0]
            sequence = row[2]
            length = row[4]
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
    #---------------------------------------
print(len(all_results), len(dbid_d), len(seq_d), gram_add , gram_minus , gram_both) #data, unique ID, unique seq



header = [
    'Seq_ID','Seq','DB_ID','Target Species', 'Activity Measure', 'Activity',
    'Unit', 'pH', 'Ionic Strength mM', 'Salt Type',
    'Medium', 'CFU', 'Note','Gram'
]
with open(f'{op_folder}{file_name}.csv', "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(all_results)


# 5409 2856 2577 4445 5402 4439 #baumannii
# 16418 8906 8008 14418 16393 14404 #aeruginosa
# 6600 3695 3313 5703 6591 5698 #Klebsiella
# 24393 11836 10749 24313 22765 22698 # golden staph
# 4741 2981 2751 4728 4404 4395 #VRE



'''
 name                   all_rows    dbaasp_ID    unique_seq    gram+    gram-    gram both
-------------------  ----------  -----------  ------------  -------  -------  -----------
mentagrophyte毛癬菌         167          112           108      145      140          140
microsporum小孢子菌          64           22            22       64       61           61
albicans念珠菌             6232         4283          3971     5484     5413         5337
fumigatus煙麴菌             293          248           225      242      240          236
Cryptococcus隱球菌          835          594           559      713      705          696
'''










#for k,v in seq_d.items():
#    seq_d[k] = set(v)
#for k,v in seq_d.items():
#    print(k,v)
#    break #KVvvKWVvKvVK {'DBAASPR_8', 'DBAASPR_75'}

### case: same seq w/ different ID
#DBAASPR_75,KVvvKWVvKvVK,Acinetobacter baumannii ATCC 19606,MIC,>100,µM,,,,LBB,1E6,
#DBAASPR_8, KVvvKWVvKvVK,Acinetobacter baumannii ATCC 19606,MIC,>100,µM,,,,LBB,1E6,


#after checking all 18460 files contain, Prosite & InterPro information

# time.sleep(np.random.uniform(1.0, 1.5))



# git add <filename> # or use . for all
# git add .   #set working path in the github project folder 
# git commit -m "update readme"          
# git push origin main

