import os
import re
import json
from datetime import datetime
import shutil

patterns_bad = [
    r'\[Set\s\d+\]',
    r'\(.*?hack.*?\)',
    r'\[Doujin & Homebrew\]',
    r'\[extras\]',
    r'\[Compilation\]',
    r'\[Utility\]',
    r'\[OS\]',
    r'\[BIOS\]',
    r'\[Miscellaneous\]',
    r'\(Doujin\)',
    r'\[null\]',
    r'/hack \[',
    r'\bdemo\b',
] 

regex_mapping = {
    r'\(.*?hack.*?\)': "Unlicensed",
    r'/hack \[': "Unlicensed",    
    r'\[Doujin & Homebrew\]': "Unlicensed",
    r'\(Doujin\)': "Unlicensed",    
    r'\[extras\]': "Add-Ons",
    r'\[Compilation\]': "Add-Ons",
    r'\[Utility\]': "Applications",
    r'\[OS\]': "Applications",
    r'\[BIOS\]': "BIOS",
    r'\[Miscellaneous\]': "Applications",
    r'\[null\]': "Preproduction",
    r'\bdemo\b': "Demos",
    r'\bDocs\b': "Manuals"
}

priority_mapping = {
    # for future pinball
    r'\bBAM\b': -1,
    r'\bphysics\b': -1,
    r'\bDOFLinx\b': -1,
    r'\bFP Physics\b': -2,
    r'\bTerryRed\b': -3,
    r'\bSLAMT1LT\b': -4,    
    r'\bUltra\b': -10,
    r'\bUltimate\b': -11,
    r'\bUltimate Pro\b': -12,

    # for visual pinball
    r'VP5': -10,
    r'VP6': -11,
    r'VP7': -12,
    r'VP8': -13,
    r'VP9': -14,
    r'VPX01': -20,
    r'VPX02': -21,
    r'VPX03': -22,
    r'VPX04': -23,
    r'VPX05': -24,
    r'VPX06': -25,
    r'VPX07': -26,
    r'DT\+FS': -1,
    
    r'PuP': -5,
    r'req. PuP': 5, # don't prefer PuP
}

def get_files_in_folder(folder_path, regex_pattern):
    categories = []
    file_list = []

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for root, dirs, files in os.walk(folder_path):

            regex = re.compile(regex_pattern, re.IGNORECASE)
            if not regex.search(root):
                continue
            
            # skip any folder that matches the bad pattern, e.g. BIOS, Misc, OS]
            if len(files) == 0:
                continue
            
            for file_name in files:
                # check for filename if it matches any Retool Category (BIOS, Unlicensed, Add-ons, etc.)
                filepath = os.path.join(root, file_name)
                (matched, description) = search_pattern_and_get_category(regex_mapping, filepath)
                if matched:
                    # extract only the last part till the first (
                    filename_noext = os.path.splitext(os.path.basename(os.path.normpath(file_name)))[0]
                 
                    json_data = {
                        "searchTerm": filename_noext,
                        "nameType": "full",
                        "categories": [description]
                    }                    
                    
                    # add to category JSON array if found
                    categories.append(json_data)

                    # but don't add it to the game list
                    continue
                
                # the filename doesn't match any of Retool Category, so we add it to the game list
                else:
                    name, extension = os.path.splitext(file_name)
                    file_list.append(name)
        
        # print(json.dumps(categories, indent=4))

        return (file_list, categories)
    else:
        print("The specified folder path does not exist or is not a directory.")
        return None
    
    
def group_filenames_by_pattern(file_list, pattern):
    grouped_files = {}
    regex_matches = {}

    for file_name in file_list:
        match = re.match(pattern, file_name)
        if match:
            key = match.group()
            if key not in grouped_files:
                grouped_files[key] = []
                regex_matches[key] = pattern.findall(file_name)
            grouped_files[key].append(file_name)

    print("Groups:")
    for key, value in grouped_files.items():
        print(f"Group: {key}")
        print("Matches:", value)
        print("Regex matches:", regex_matches[key])
        print("-----------------------------")

    return grouped_files

def generate_json_template(grouped_files, categories):
    variants = []

    for key, value in grouped_files.items():
        variant = {
            "group": key.strip(),
            "titles": []
        }
        for match in value:
            variant["titles"].append({
                "searchTerm": match,
                "nameType": "full"
            })
        variants.append(variant)

    # JSON template
    json_template = {
        "description": {
            "name": DAT_NAME,
            "lastUpdated": datetime.now().strftime('%Y-%m-%d'),
            "minimumVersion": "2.00",
            "romSourceName": ROM_SOURCE_NAME,
            "romSourceUrl": ROM_SOURCE_URL,
            "romVersion": ROM_VERSION,
            "author": AUTHOR_NAME,
            "authorEmail": AUTHOR_EMAIL
        },
        "categories": categories,
        "removes": retool_clonelist_removes_json_data,
        "overrides": retool_clonelist_overrides_json_data,
        "variants": variants
    }

    return json_template

def override_manual(json_data, json_data_manual):
    data = json_data

    for obj2 in json_data_manual:
        for obj1 in json_data['variants']:
            if obj1['group'] == obj2['group']:
                for title2 in obj2['titles']:
                    for idx, title1 in enumerate(obj1['titles']):
                        if title1['searchTerm'] == title2['searchTerm']:
                            # Replace the object in json1 with object in json2
                            obj1['titles'][idx] = title2
       
    return data    

# Priority assignment
# CD: 10
# HD: 20
# FD: 30
# CT: 40
# DVD: 50  <-- not supported by emulator most likely, so we won't use it if CD is availalbe
# other: 99
def prioritize_search_terms(json_data):
    patterns_bad = [
        r'\[Set\s\d+\]',
        r'\(.*?hack.*?\)',
        r'\[Doujin & Homebrew\]',
        r'\[extras\]',
        r'\[Compilation\]',
        r'\[Utility\]',
        r'\[OS\]',
        r'\[BIOS\]',
        r'\[Miscellaneous\]',
        r'\(Doujin\)',
        r'\[null\]',
        r'/hack \[',
        r'\bdemo\b',
    ] 

    patterns_cd = [
        r'\[CD.*?\]'
    ]  

    patterns_hd = [
        r'\[HD.*?\]'
    ]  

    patterns_fd = [
        r'\[FD.*?\]',
        r'\bFloppy\b'
    ]      

    patterns_ct = [
        r'\[CT.*?\]',
        r'\bCartridge\b'
    ]         

    patterns_dvd = [
        r'\[DVD.*?\]'
    ]     

    patterns_pinball_bam = [
        r'\bBAM\b'
    ]        

    data = json_data

    for variant in data['variants']:
        fd_exists = False
        fd_set_exists = False

        if len(variant['titles']) == 1: # don't add 'prioirty' attribute if that title len is only 1
            print("Skip adding prio because len=1")
            continue

        # Check for presence of [FD] and [FD] [Set]
        for title in variant['titles']: 
            priority = search_pattern_and_get_priority(priority_mapping, title['searchTerm'])

            if priority == 0:
                pass

            else:
                title['priority'] = priority
            # if search_pattern(patterns_bad, title['searchTerm']):
            #     title['priority'] = 99

            # elif search_pattern(patterns_cd, title['searchTerm']):
            #     title['priority'] = 10

            # elif search_pattern(patterns_hd, title['searchTerm']):
            #     title['priority'] = 20

            # elif search_pattern(patterns_fd, title['searchTerm']):
            #     title['priority'] = 30

            # elif search_pattern(patterns_ct, title['searchTerm']):
            #     title['priority'] = 40         

            # elif search_pattern(patterns_dvd, title['searchTerm']):
            #     title['priority'] = 50    

            # # for pinball tables
            # elif search_pattern(patterns_pinball_bam, title['searchTerm']):
            #     title['priority'] = -1                                    

        # # Add 'priority': -1 to searchTerm without [FD] [Set]
        # if fd_exists and not fd_set_exists:
        #     for title in variant['titles']:
        #         if "[FD]" in title['searchTerm'] and "[FD] [Set]" not in title['searchTerm']:
        #             title['priority'] = -1

    return data

def search_pattern(patterns, text):
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            print(f"Pattern: {pattern}")
            print(f"Matches: {matches}")
            print(f"Text: {text}")
            return True

def search_pattern_and_get_category(patterns, text):
    for pattern, description in patterns.items():
        #print(f"Matching '{description}':")
        if re.findall(pattern, text):
            print(f"    '{text}' matches pattern '{pattern}'") 
            return (True, description) 

    return (False, "")  

def search_pattern_and_get_priority(patterns, text):
    priority_assigned = 0 # store the computed priority
    for pattern, priority in patterns.items():
        if re.findall(pattern, text, flags=re.IGNORECASE):
            print(f"    '{text}' matches pattern '{pattern}'") 
            priority_assigned += priority
            
    return priority_assigned

def copy_clonelist_to_retool_folder(source_folder, destination_folder):
    # Check if the source folder exists and is a directory
    if os.path.exists(source_folder) and os.path.isdir(source_folder):
        # Get a list of all JSON files in the source folder
        json_files = [file for file in os.listdir(source_folder) if file.endswith('.json')]

        # Copy each JSON file to the destination folder
        for file in json_files:
            source_file_path = os.path.join(source_folder, file)
            destination_file_path = os.path.join(destination_folder, file)
            shutil.copy2(source_file_path, destination_file_path)
            
        print("JSON files copied successfully.")
    else:
        print("Source folder does not exist or is not a directory.")

def load_json(filepath):
    if filepath != "":
        try:
            with open(filepath, 'r') as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"File '{filepath}' not found.")
            exit(1)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in '{filepath}'.")
            exit(1)
    else:
        pass

# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
if __name__ == "__main__":

    # Read JSON data from the file
    with open('.\clonelists-generator\config.json', 'r') as file:
        json_data = json.load(file)

    AUTHOR_NAME = json_data['author_name']
    AUTHOR_EMAIL = json_data['author_email']
    OUTPUT_1G1R_DAT_DIR = json_data['output_1g1r_dat_dir']

    # Iterate through each element in "platforms"
    for platform in json_data['platforms']:
        if platform['enabled'] == False:
            print("Skipping rom_dir: {}", platform['rom_dir'])
            continue

        print("ROM Directory:", platform['rom_dir'])
        print("Headers:")
        for key, value in platform['headers'].items():
            print(f"  {key}: {value}")
        print("-------------------")

        FOLDER_PATH = platform['rom_dir']
        
        DAT_NAME = platform['headers']['dat_name']
        ROM_SOURCE_NAME = platform['headers']['rom_source_name']
        ROM_SOURCE_URL = platform['headers']['rom_source_url']
        ROM_VERSION = platform['headers']['rom_version']

        # load JSON from folder
        retool_clonelist_removes_json_data = load_json(platform['removes']) 
        retool_clonelist_overrides_json_data = load_json(platform['overrides']) 
        retool_clonelist_variants_json_data = load_json(platform['variants'])   

        FOLDER_FILTER_REGEX = platform['folder_filter_regex']

        folder_path = FOLDER_PATH
        (files_array, categories) = get_files_in_folder(folder_path, FOLDER_FILTER_REGEX)

        # regex_pattern = r'^[^(]+' # capture starting from the first letter till the first ( it sees
        # regex_pattern = r'^[^[]+'
        regex_pattern = r'^[^[(]+'
        grouped_files = group_filenames_by_pattern(files_array, re.compile(regex_pattern))

        result_json = generate_json_template(grouped_files, categories)

        # Print the resulting JSON
        print(json.dumps(result_json, indent=4))

        # save the clonelist.json 
        out_1g1r_dat_filepath = os.path.join(OUTPUT_1G1R_DAT_DIR, '{}.json'.format(DAT_NAME))

        # Write JSON to a file
        # with open(out_1g1r_dat_filepath, 'w') as json_file:
        #     json.dump(result_json, json_file, indent=4)

        # add priority
        result_json = prioritize_search_terms(result_json)
        print(result_json)

        override_manual(result_json, retool_clonelist_variants_json_data)

        # Sort the variants array alphabetically by 'group' key
        result_json['variants'].sort(key=lambda x: x['group'])

        # out_1g1r_dat_filepath = os.path.join(OUTPUT_1G1R_DAT_DIR, '{}-{}.json'.format(DAT_NAME, '+prio'))
        out_1g1r_dat_filepath = os.path.join(OUTPUT_1G1R_DAT_DIR, '{}.json'.format(DAT_NAME))
        with open(out_1g1r_dat_filepath, 'w') as json_file:
            json.dump(result_json, json_file, indent=4)

            

        # if files_array:
        #     print("List of files in the folder:", files_array)



    # FOLDER_PATH = 's:\\roms-translated-1g1r\\archive-org-nintendo-snes'
    # LAST_UPDATED = '1 December 2023'

    # DAT_NAME = 'Nintendo - Super Nintendo Entertainment System (Translated En)'
    # ROM_SOURCE_NAME = 'English Translation ROMs Collection (2023)'
    # ROM_SOURCE_URL = 'https://archive.org/details/En-ROMs'
    # AUTHOR_NAME = 'dsync89'
    # AUTHOR_EMAIL = 'dsync89@yahoo.com'

    # addon
    # copy the json to retool clonelist
    source_folder_path = '.'  # Replace with your source folder path
    destination_folder_path = 'c:\\Programs\\Project ROM DAT\\retool-2.01.5-win-x86-64\\clonelists'  # Replace with your destination folder path
    print("Copy *.json to {}".format(destination_folder_path))
    copy_clonelist_to_retool_folder(source_folder_path, destination_folder_path)

