# this script fetches data from official website, converts xls to csv and merges them together
import urllib.request
import pandas as pd
import os


def get_district_id(district_no):
    return "{:02}".format(district_no)


def get_url(district_id):
    return "http://prezydent2000.pkw.gov.pl/gminy/obwody/obw" + district_id + ".xls"


def get_file_path(district_id):
    return "obw" + district_id


def get_xls_sheet(district_id):
    return "gl" + district_id


def get_progress_bar(iteration, max_iterations):
    progress = round(30 * iteration / max_iterations)
    return "[" + "#" * progress + " " * (30 - progress) + "]"


output_file = open("data.csv", "a")
print("Fetching data...")
for i in range(1, 69):
    district_id = get_district_id(i)
    path = get_file_path(district_id)
    urllib.request.urlretrieve(get_url(district_id), path + ".xls")
    xls_file = pd.read_excel(path + ".xls", get_xls_sheet(district_id)).rename(
        columns=lambda x: x.strip().replace("\n", " "))
    xls_file.to_csv(path + ".csv", encoding='utf-8', index=False, header=True if i == 1 else False)
    os.remove(path + ".xls")
    for line in open(path + ".csv"):
        output_file.write(line)
    os.remove(path + ".csv")
    print("\r" + get_progress_bar(i, 68), end="", flush=True)
output_file.close()
print("\rFinished!")
