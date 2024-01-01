import os
import re

root_folder = 'c:\\Programs\\Project ROM DAT\\DAT Files (1G1R output from Retool)\\fullset\\Visual Pinball'

# Walk through the directory tree
for root, _, files in os.walk(root_folder):
    for file in files:
        if file.endswith('.xml'):
            file_path = os.path.join(root, file)
            
            # Read the content of the XML file
            with open(file_path, 'r') as f:
                content = f.readlines()

            # Replace lines containing '<machine' with '<game' and '</machine' with '</game'
            modified_content = [re.sub(r'<\/?machine', lambda match: '</game' if match.group() == '</machine' else '<game', line) for line in content]

            # Create the new file path with the .dat extension
            new_file_path = os.path.splitext(file_path)[0] + '.dat'

            # Write the modified content to the new file with .dat extension
            with open(new_file_path, 'w') as f:
                f.writelines(modified_content)