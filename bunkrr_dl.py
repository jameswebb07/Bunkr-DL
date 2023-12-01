import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

# Get the directory where this script is located
script_directory = os.path.dirname(os.path.abspath(__file__))

# Set the current working directory to the script's directory
os.chdir(script_directory)

# Function to download the media file with checks
def download_media(url, file_name, headers):
    try:
        with open(file_name, "wb") as file:
            response = requests.get(url, headers=headers)
            file.write(response.content)
            
            # Check file size after download
            if os.path.getsize(file_name) >= (2 * 1024):  # Only print successful downloads if file size is >= 2KB
                print(f"Downloaded '{file_name}'")
                print("--------------")
            else:
                os.remove(file_name)
                #print(f"Deleted '{file_name}' due to small file size.")
    except Exception as e:
        print(f"Failed to download '{file_name}'")
        if os.path.exists(file_name):
            os.remove(file_name)
            #print(f"Deleted '{file_name}' due to failed download.")
            print("--------------")


# URL of the live webpage
url = "https://bunkrr.su/a/FDEuLMIe"

# Parse the URL to extract the folder name
parsed_url = urlparse(url)
folder_name = parsed_url.path.strip('/').split('/')[-1]

# Create a folder for downloads based on the extracted folder name
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Send a GET request to the webpage
response = requests.get(url)

if response.status_code == 200:
    # Parse the HTML content of the webpage
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all 'grid-images_box' divs
    grid_images_boxes = soup.find_all('div', class_='grid-images_box')

    if grid_images_boxes:
        with ThreadPoolExecutor(max_workers=5) as executor:  # Adjust max_workers as needed
            for box in grid_images_boxes:
                # Extract img src
                img_src = box.find('img')['src']
                #print("Image Source:", img_src)

                # Extract the first paragraph text and grab file extension
                first_paragraph = box.find('p').text.strip()
                file_extension = os.path.splitext(first_paragraph)[1]
                #print("File Extension:", file_extension)

                # Modify the download URL
                modified_url = img_src.replace('/thumbs/', '/').rsplit('.', 1)[0] + file_extension
                print("Download URL:", modified_url)

                # Generate a random User-Agent header using fake-useragent
                user_agent = UserAgent()
                headers = {
                    "User-Agent": user_agent.random
                }

                # Download the media file into the folder
                file_name = os.path.basename(modified_url)
                file_path = os.path.join(folder_name, file_name)
                executor.submit(download_media, modified_url, file_path, headers)
                
                time.sleep(10)  # Add a slight delay between downloads if needed
    else:
        print("Couldn't find any 'grid-images_box' divs on the webpage.")
else:
    print("Failed to fetch the webpage. Status code:", response.status_code)
