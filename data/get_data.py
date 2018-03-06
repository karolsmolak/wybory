#this script fetches data from official website, converts xls to csv and merges them together
import urllib.request
import pandas as pd
import os

def get_id(i):
    return "{:02}".format(i)

def get_url(id):
    return "http://prezydent2000.pkw.gov.pl/gminy/obwody/obw" + id + ".xls"

def get_file_path(id):
    return "obw" + id;

def get_xls_sheet(id):
    return "gl" + id

def get_progress_bar(i, size):
    progress = round(30 * i / size)
    return "[" + "#" * progress + " " * (30 - progress) + "]"

fout = open("data.csv", "a")
print("Fetching data...")
for i in range(1, 69):
    id = get_id(i)
    path = get_file_path(id)
    urllib.request.urlretrieve(get_url(id), path + ".xls")
    xls_file = pd.read_excel(path + ".xls", get_xls_sheet(id)).rename(columns=lambda x: x.strip().replace("\n", " "))
    if i == 1:
        xls_file.to_csv(path + ".csv", encoding='utf-8', index=False)
    else:
        xls_file.to_csv(path + ".csv", encoding='utf-8', index=False, header=False)
    os.remove(path + ".xls")
    f = open(path + ".csv")
    for line in f:
        fout.write(line)
    f.close()
    os.remove(path + ".csv")
    print("\r" + get_progress_bar(i, 68), end = "", flush=True)
fout.close()
print("\rFinished!")