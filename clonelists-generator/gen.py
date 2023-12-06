import os
import re
import json

def get_files_in_folder(folder_path):
    file_list = []

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files = os.listdir(folder_path)
        
        for file_name in files:
            name, extension = os.path.splitext(file_name)
            file_list.append(name)
        
        return file_list
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

def generate_json_template(grouped_files):
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
            "lastUpdated": LAST_UPDATED,
            "minimumVersion": "2.00",
            "romSourceName": ROM_SOURCE_NAME,
            "romSourceUrl": ROM_SOURCE_URL,
            "author": AUTHOR_NAME,
            "authorEmail": AUTHOR_EMAIL
        },
        "variants": variants
    }

    return json_template

# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
if __name__ == "__main__":

    # Read JSON data from the file
    with open('config.json', 'r') as file:
        json_data = json.load(file)

    AUTHOR_NAME = json_data['author_name']
    AUTHOR_EMAIL = json_data['author_email']
    OUTPUT_1G1R_DAT_DIR = json_data['output_1g1r_dat_dir']

    # Iterate through each element in "platforms"
    for platform in json_data['platforms']:
        print("ROM Directory:", platform['rom_dir'])
        print("Headers:")
        for key, value in platform['headers'].items():
            print(f"  {key}: {value}")
        print("-------------------")

        FOLDER_PATH = platform['rom_dir']
        LAST_UPDATED = platform['headers']['last_updated']
        
        DAT_NAME = platform['headers']['dat_name']
        ROM_SOURCE_NAME = platform['headers']['rom_source_name']
        ROM_SOURCE_URL = platform['headers']['rom_source_url']

        folder_path = FOLDER_PATH
        files_array = get_files_in_folder(folder_path)

        regex_pattern = r'^[^(]+' # capture starting from the first letter till the first ( it sees
        grouped_files = group_filenames_by_pattern(files_array, re.compile(regex_pattern))

        result_json = generate_json_template(grouped_files)

        # Print the resulting JSON
        print(json.dumps(result_json, indent=4))

        out_1g1r_dat_filepath = os.path.join(OUTPUT_1G1R_DAT_DIR, '{}.json'.format(DAT_NAME))

        # Write JSON to a file
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