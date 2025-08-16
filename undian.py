import pandas as pd
import numpy as np
import streamlit as st
import random as rd

# Extract & Transform Data
spreadsheet = "https://docs.google.com/spreadsheets/d/1NKT3lM1zkw2g-CkCaR5F_HTm1vvlYmw4EFjQmkBr6Fw/export?format=csv&gid=1788211216"
df = pd.read_csv(spreadsheet)
df_backup = df.copy()

# TOKENIZER

jabatan_token = {
    'CREW' : 0,
    'IT' : 3,
    'TSM' : 4,
    'MD' : 1,
    'ACOS' : 1,
    'WH' : 3,
    'SM' : 7,
    'OPR' : 4,
    'COS' : 2,
    'PD' : 4,
    'LND' : 3
}

df['Jabatan Numerik'] = df.Jabatan.map(jabatan_token)
df = df[df['Jabatan Numerik'] < 7]

# KUOTA PEMENANG
kuota_pemenang = {
    'Hadiah Utama' : 3,
    'Hadiah Kedua' : 3,
    'Hadiah Ketiga' : 10,
    'Hadiah Keempat' : 30
}

pemenang = {
    'Hadiah Utama' : [] ,
    'Hadiah Kedua' : [],
    'Hadiah Ketiga' : [],
    'Hadiah Keempat' :[],
    'Hadiah Cabang' : []
}

# -----------------
# HADIAH UTAMA
# -----------------
C1 = df[df['Point'] == df.Point.max()]
H1W = C1.sample(kuota_pemenang['Hadiah Utama'])

pemenang['Hadiah Utama'] = H1W

# -----------------
# HADIAH KEDUA
# -----------------

df = df[~df.index.isin(H1W.index)] # EXCLUDE DATA PEMENANG HADIAH UTAMA
KKM = 42

C2 = df[df['Point'] >= KKM]
H2W = C2.sample(kuota_pemenang['Hadiah Kedua'])

pemenang['Hadiah Kedua'] = H2W

# -----------------
# HADIAH KETIGA
# -----------------

df = df[(~df.index.isin(H2W.index))]
df_UnderKKM = df[df['Point'] < KKM]

# GROUPING
df_branch    = {} # nama_cabang : data_peserta
sample_branch = {} # nama_cabang : X data, dengan X = jumlah sampel

for cabang, isi in df_UnderKKM.groupby('Branch'): # df.groupby itu udah otomatis sortir dan filter
    df_branch[cabang] = isi

# SAMPLING
JUMLAH_SAMPLE = 3

for cabang, isi in df_branch.items():
    if len(isi) <= JUMLAH_SAMPLE:
        sample_branch[cabang] = isi
    else:
        sample_branch[cabang] = isi.sample(JUMLAH_SAMPLE)

# MERGE
C3 = pd.concat(sample_branch.values())
H3W = C3.sample(kuota_pemenang['Hadiah Ketiga'])
pemenang['Hadiah Ketiga'] = H3W

# -----------------
# HADIAH KEEMPAT
# -----------------
df  = df[(~df.index.isin(H3W.index))]
H4W = df.sample(kuota_pemenang['Hadiah Keempat'])
pemenang['Hadiah Keempat'] = H4W

# -----------------
# HADIAH CABANG
# -----------------

df = df[(~df.index.isin(H4W.index))]

data_cabang = {}
kuota_cabang = {
    'Samarinda': 3,
    'Ambon': 3,
    'HO': 3,
    'Boyolali': 3,
    'Bekasi': 6,
    'Palu': 4,
    'Medan': 4,
    'Bitung': 6,
    'Kendari': 3,
    'Makassar': 4,
    'Pasuruan': 4
}
HCW = {}

for cabang, isi in df.groupby('Branch'):
    data_cabang[cabang] = isi

for cabang, isi in data_cabang.items():
    if len(isi) <= kuota_cabang[cabang]:
        HCW[cabang] = isi
    else:
        HCW[cabang] = isi.sample(kuota_cabang[cabang])

pemenang['Hadiah Cabang'] = pd.concat(HCW.values())

print("Pemenang Cabang:")
print(pemenang['Hadiah Cabang'])