import os
from bs4 import BeautifulSoup

# Define the folder path
folder_path = 'eating_clubs/data'

# Walk through all the files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith('.html'):
        html_file_path = os.path.join(folder_path, filename)

        # Read the HTML file
        with open(html_file_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

        # Parse the HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        text_content = soup.get_text()

        # Define the text file path
        text_file_path = os.path.join(folder_path, f"{os.path.splitext(filename)[0]}.txt")

        # Write the extracted text to a new .txt file
        with open(text_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text_content)

        # Delete the original HTML file
        os.remove(html_file_path)

print("Conversion complete, HTML files deleted.")
