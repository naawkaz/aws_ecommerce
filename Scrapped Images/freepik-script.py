import requests   # library for making HTTP requests (to Freepik API + image downloads)
import os         # for creating directories and handling file paths
import random     # for randomly selecting which pages to fetch

API_KEY = ""   # your Freepik API key
BASE_URL = "https://api.freepik.com/v1/resources"  # base endpoint for Freepik resources API


def download_images(directory, query, per_page=30, max_pages=15, max_page_range=50):
    # 1. Create the target folder if it doesn't already exist
    os.makedirs(directory, exist_ok=True)

    count = 1  # image counter for filenames
    headers = {"x-freepik-api-key": API_KEY}  # Freepik requires API key in headers
    downloaded_ids = set()  # to track unique Freepik image IDs


    # 2. First request: fetch page 1 to inspect metadata (pagination info)
    params = {
        "term": query,                       # search query, e.g. "boots"
        "per_page": per_page,                # number of results per page
        "page": 1,                           # request the first page
        "filters[content_type][photo]": 1    # restrict results to photos only
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    data = response.json()

    # 3. Check if response contains both results and metadata
    if "data" not in data or "meta" not in data:
        print("No data found in response:", data)
        return

    # 4. Extract total available pages and results
    last_page = data["meta"]["last_page"]   # reported total number of pages
    total_results = data["meta"]["total"]   # reported total number of matching results

    # 5. Restrict search space: 
    #    only look at the first `max_page_range` pages 
    #    (to avoid irrelevant or invalid high page numbers)
    page_limit = min(last_page, max_page_range)

    # 6. Randomly select which pages to visit (no duplicates because `random.sample` is used)
    pages_to_visit = random.sample(range(1, page_limit + 1), min(max_pages, page_limit))

    print(
        f"Total results: {total_results}, Pages available: {last_page}, "
        f"Randomly visiting {len(pages_to_visit)} pages (1–{page_limit})"
    )

    # 7. Loop through each chosen page
    for page in pages_to_visit:
        params["page"] = page
        response = requests.get(BASE_URL, headers=headers, params=params)

        if response.status_code != 200:
            # if a request fails (e.g. invalid page), print error and skip
            print(f"Page {page} failed: {response.status_code} {response.text[:200]}")
            continue

        data = response.json()

        # 8. Loop through each image item in the response
        for item in data.get("data", []):
            img_id = item.get("id")
            if not img_id or img_id in downloaded_ids:
                continue  # skip duplicates

            downloaded_ids.add(img_id)  # mark as seen

            # Try to extract a usable image URL
            img_url = (
                item.get("image", {}).get("source", {}).get("url")       # main source image
                or item.get("image", {}).get("preview", {}).get("url")   # fallback preview image
                or item.get("image", {}).get("thumbnails", [{}])[0].get("url")  # last resort thumbnail
            )

            if not img_url:
                print("⚠️ No image URL found for item:", item.get("id"))
                continue

            # 9. Build filename and download the image
            filename = os.path.join(directory, f"{query}_{count}.jpg")

            try:
                img_data = requests.get(img_url).content  # fetch image binary
                with open(filename, "wb") as f:           # save to file
                    f.write(img_data)
                print(f"Downloaded {filename} (from page {page})")
                count += 1
            except Exception as e:
                print(f"Failed to download {img_url}: {e}")

    # 10. Final report
    print(f"Done. Downloaded {count-1} images.")


# Example run
download_images(directory="violins", query="violin", per_page=30, max_pages=15, max_page_range=30)
