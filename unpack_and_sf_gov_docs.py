import os 
import zipfile
import subprocess
import shutil
import time
from collections import Iterator
from threading import Lock, active_count, Thread


### this is the root folder for the yaml files - will create its own subfolders per zip
dst_folder = "yamls"

### number of threads - not tested at any other setting than 25. 
max_threads = 25

### this is where the zip files are found
zips_folder = r"govdocs_zips"

### this is a folder that python can see. Used to unpack the zip files while process in flight. 
dst_root = r"temp_data"

if not  os.path.exists(dst_folder):
    os.makedirs(dst_folder)

def get_zips(folder = ""):
    """returns all the zip files in the given folder. If no folder given, looks in its own root"""
    zips = [os.path.join(folder, x) for x in os.listdir(folder) if x.endswith(".zip")]
    return zips

def make_folder_and_unzip(root, counter, my_zip):
    """takes a path to a zip, and the file counter. Makes a destination folder, and unzips the zip. returns the dst folder"""
    with zipfile.ZipFile(my_zip, 'r') as zip_ref:
        zip_ref.extractall(root)
    return os.path.join(root, os.listdir(root)[0])


def do_sf(my_f, yaml_path):
        """this is the per item / thread work - any actions on an item should be in here
        sets up the sf call with the target file, and the output (yaml) file path, and evokes sf.exe"""
        sf_command = f"E:/tools/siegfried/sf.exe {my_f} > {yaml_path}"
        subprocess.call(sf_command, shell=True)


def run_sf_against_folder(source_folder, counter):
    """works at the folder level.
    takes the dst folder from the upzipper, and process each file in the zip.
    Is a little flakey - the threading isn't elegant so if something goes wrong it an run away - should stop at end of folder/files. 
    look for 0b or 1b sized yaml files as indicator something went wrong
    makes one yaml per file - two reasons:
        sf seems to die abruptly when it encounters a problem. Was seeing around %40 attrition of files processed due to early termination
        corp anti-malware silently removes files, so this might also disrupt sf.

    to combat the added overhead of file by file processing, theading is used.""" 

    threads = []
    yamls_folder = r"C:\Repos\gov_docs_data\yamls"+f"\{str(counter).zfill(3)}"
    if not os.path.exists(yamls_folder):
        os.makedirs(yamls_folder)

    for f in os.listdir(source_folder):
        my_f = os.path.join(source_folder, f)
        try:
            yaml_name, __ = f.rsplit(".", 1)
            yaml_name += ".yaml"
            yaml_path = os.path.join(yamls_folder, yaml_name)
            has_file = True
        except ValueError:
            has_file = False

        if has_file:
            t = Thread(target=do_sf, args=[my_f, yaml_path]).start()
            threads.append(t)

    threads = [ x for x in threads if x != None]
    
    for x in threads:
        x.start()

    for x in threads:
        x.join()


    return True

def delete_zip_folder(source_folder):
    """ waits for a carefully selected amount of time before deleting the files folder 
    this allows the threads to catch up. If you're seeing PermissionErrors, increase the sleep length. 
    You might get a faster turn over by reducing the sleep length
    time.sleep(30)"""
    try:
        shutil.rmtree(source_folder)
    except PermissionError:
        print ("tried to delete zip too soon...")
        quit()


for i, my_zip in enumerate(get_zips(zips_folder)):
    yaml_folder = os.path.join("yamls", f"{str(i).zfill(3)}")
    try:
        done_files_in_folder = len(os.listdir(yaml_folder))
    except FileNotFoundError:
       done_files_in_folder = 0 

    if done_files_in_folder < 950:
        print (f"Working on: {i} - {my_zip}")
        my_folder = make_folder_and_unzip(dst_root, i, my_zip)
        run_sf_against_folder(my_folder, i)
        delete_zip_folder(my_folder)
    else:
        print (f"Skippping {yaml_folder}")

