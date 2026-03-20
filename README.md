# dbaasp-crawler
fetching and arranging peptide samples from DBAASP database



### Step by step download this repo

1. recommand download by wget:
```bash
wget https://github.com/Lee-ChinCheng/dbaasp-crawler/archive/refs/heads/main.zip
```

2. decompress the zip file:
```bash
unzip main.zip
```

3. access the repo folder:
```bash
cd dbaasp-crawler-main
```

4. decompress monomer10-50.tar.xz, it will output a folder contains multi csv files.
```bash
tar -xf monomer10-50.tar.xz
```
5. execute step1_arrange.py, it will pop up a UI for user inputs.
```bash
streamlit run step1_arrange.py
```

---
