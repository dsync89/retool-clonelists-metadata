import re

# Dictionary mapping regex pattern to a string
regex_mapping = {
    r'\[Set\s\d+\]': "Applications",
    r'\(.*?hack.*?\)': "Applications",
    r'\[Doujin & Homebrew\]': "Applications",
    r'\[extras\]': "Add-ons",
    r'\[Compilation\]': "Add-ons",
    r'\[Utility\]': "Applications",
    r'\[OS\]': "Applications",
    r'\[BIOS\]': "BIOS",
    r'\[Miscellaneous\]': "Applications",
    r'\(Doujin\)': "Applications",
    r'/\[null\]': "Applications",
    r'/hack \[': "Applications",
    r'\bdemo\b': "Demo",
}

# Test strings to match against the regex patterns
test_strings = [
    "12345",
    "HelloWorld",
    "test@example.com",
    "ABC123"
]

# Loop through each regex pattern and test strings
for pattern, description in regex_mapping.items():
    print(f"Matching '{description}':")
    for test_string in test_strings:
        if re.match(pattern, test_string):
            print(f"    '{test_string}' matches pattern '{pattern}'")
