import requests
import os
import multiprocessing

# Define jobs: each job has (API_KEY, directory, query, per_page, pages)
JOBS = [
    ("", "High Heels", "High Heels", 30, 15), #main api
    ("", "Boots", "Boots", 30, 15),#second api
]

def download_images(api_key, directory, query, per_page, pages):
    os.makedirs(directory, exist_ok=True)
    count = 1
    for page in range(1, pages + 1):
        url = f"https://api.unsplash.com/search/photos?page={page}&per_page={per_page}&query={query}&client_id={api_key}"
        response = requests.get(url).json()
        for result in response["results"]:
            img_url = result["urls"]["regular"]
            img_data = requests.get(img_url).content
            filename = os.path.join(directory, f"{query}_{count}.jpg")
            with open(filename, "wb") as f:
                f.write(img_data)
            print(f"[{query}] Downloaded {filename}")
            count += 1

def run_parallel_jobs():
    processes = []
    for job in JOBS:
        p = multiprocessing.Process(target=download_images, args=job)
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

if __name__ == "__main__":
    run_parallel_jobs()
