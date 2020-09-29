import os 
import zipfile
import subprocess
import shutil
import time

dst_folder = "yamls"

if not  os.path.exists(dst_folder):
    os.makedirs(dst_folder)

def get_zips(folder = ""):
    zips = [os.path.join(folder, x) for x in os.listdir(folder) if x.endswith(".zip")]
    return zips

def make_folder_and_unzip(root, counter, my_zip):
    with zipfile.ZipFile(my_zip, 'r') as zip_ref:
        zip_ref.extractall(root)
    return os.path.join(root, os.listdir(root)[0])


def run_sf_against_folder(source_folder, counter, yaml_path):
    sf_command = f"E:/tools/siegfried/sf.exe -coe  -multi 256 {my_folder} > {yaml_path}"
    subprocess.call(sf_command, shell=True)
    return True

def delete_zip_folder(source_folder):
    shutil.rmtree(source_folder)


zips_folder = r"C:\Users\gattusoj\Downloads\govdocs_zips"
dst_root = r"C:\Repos\gov_docs_data\temp_data"
yaml_root = "yaml"


if not os.path.exists(yaml_root):
    os.makedirs(yaml_root)

for i, my_zip in enumerate(get_zips(zips_folder)):
    yaml_file = os.path.join(yaml_root, f"{str(i).zfill(3)}.yaml")
    if not os.path.exists(yaml_file):
        my_folder = make_folder_and_unzip(dst_root, i, my_zip)
        run_sf_against_folder(my_folder, i, yaml_file)
        delete_zip_folder(my_folder)
    else:
        print (f"Skipping {i}")
