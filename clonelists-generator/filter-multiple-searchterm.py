import os
import re
import json
from datetime import datetime
import shutil

# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
if __name__ == "__main__":

    file_path = input("Enter the file path: ")
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)            
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")   
        exit(1)


    # Filter groups with more than one element in 'titles'
    filtered_variants = [variant for variant in json_data['variants'] if len(variant['titles']) > 1]

    # Sort the filtered variants alphabetically by 'group' key
    filtered_variants.sort(key=lambda x: x['group'])

    # Create a new dictionary with filtered variants
    filtered_data = {
        "description": json_data["description"],
        "categories": json_data["categories"],
        "removes": json_data["removes"],
        "overrides": json_data["overrides"],
        "variants": filtered_variants
    }


    # Get the file name without extension from the original file path
    file_name_without_extension = os.path.splitext(file_path)[0]

    # Create a new file name by adding '-multiplesearchterm' before the extension
    new_file_name = f"{file_name_without_extension}-multiplesearchterm.json"

    # Save the filtered and sorted data to a new JSON file with the new file name
    with open(new_file_name, 'w') as outfile:
        json.dump(filtered_data, outfile, indent=4)
        print("Saved filtered json as: {}".format(new_file_name))
    