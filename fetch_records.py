import requests
import json
import time

def fetch_all_zenodo_records(community_id, output_file="zenodo_records.json", delay=0.2):
    base_url = "https://zenodo.org/api/records"
    all_records = []
    page = 1
    size = 100  # Max allowed by Zenodo

    print(f"Fetching records from community: {community_id}")

    while True:
        print(f"Fetching page {page}...")
        params = {
            "communities": community_id,
            "size": size,
            "page": page
        }

        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        all_records.extend(hits)

        if len(hits) < size:
            break  # Last page reached

        page += 1
        time.sleep(delay)  # Be polite to the API

    print(f"Fetched {len(all_records)} records. Saving to {output_file}...")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print("Done.")

# Run it
if __name__ == "__main__":
    fetch_all_zenodo_records("emulti")