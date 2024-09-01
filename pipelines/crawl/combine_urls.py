import os

def collect_urls_from_files(folder_path):
    urls = set()  # Using a set to avoid duplicates

    # Iterate over all files in the specified folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            
            with open(file_path, 'r') as file:
                for line in file:
                    url = line.strip()
                    if url:  # Ignore empty lines
                        urls.add(url)

    return urls

def write_urls_to_file(urls, output_file):
    with open(output_file, 'w') as file:
        for url in sorted(urls):
            file.write(url + '\n')

def main():
    folder_path = 'urls_out'  # Replace with your folder path
    output_file = 'all_urls.txt'  # Output file for the combined URLs

    # Collect URLs from all .txt files in the folder
    urls = collect_urls_from_files(folder_path)

    # Write the unique URLs to the output file
    write_urls_to_file(urls, output_file)

    print(f'Collected {len(urls)} unique URLs and saved them to {output_file}')

if __name__ == '__main__':
    main()
