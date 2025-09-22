import requests
import os

# Your Unsplash API access key
ACCESS_KEY = ""



def download_images(directory, query="sneakers", per_page=10, pages=3):
    # Directory to save images
    SAVE_DIR = directory
    os.makedirs(SAVE_DIR, exist_ok=True)
    count = 1
    for page in range(1, pages + 1):
        url = f"https://api.unsplash.com/search/photos?page={page}&per_page={per_page}&query={query}&client_id={ACCESS_KEY}"
        response = requests.get(url).json()
        for result in response["results"]:
            img_url = result["urls"]["regular"]
            img_data = requests.get(img_url).content
            filename = os.path.join(SAVE_DIR, f"{query}_{count}.jpg")
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"Downloaded {filename}")
            count += 1

download_images(directory="sandals", query="sandals", per_page=30, pages=15)  # 450 images
