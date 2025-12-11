import requests
import time

def fetch_huggingface_datasets(limit=1000, sort="downloads"):
    """
    Fetch datasets from Hugging Face API
    
    Args:
        limit: Number of datasets to fetch (default: 1000)
        sort: Sort method - "downloads", "likes", "trending", "createdAt"
    """
    
    print(f"Fetching {limit} datasets from Hugging Face...")
    print(f"Sort by: {sort}\n")
    
    datasets = []
    page = 0
    per_page = 100  # API limit per request
    
    while len(datasets) < limit:
        try:
            # Hugging Face API endpoint untuk DATASETS
            url = "https://huggingface.co/api/datasets"
            params = {
                "limit": per_page,
                "skip": page * per_page,
                "sort": sort,
                "direction": -1  # Descending
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            batch = response.json()
            
            if not batch:
                print("No more datasets found.")
                break
            
            for item in batch:
                dataset_id = item.get('id')
                if dataset_id:
                    datasets.append({
                        'id': dataset_id,
                        # URL dataset biasanya memiliki format /datasets/nama_dataset
                        'url': f"https://huggingface.co/datasets/{dataset_id}", 
                        'downloads': item.get('downloads', 0),
                        'likes': item.get('likes', 0)
                    })
                
                if len(datasets) >= limit:
                    break
            
            page += 1
            print(f"Fetched {len(datasets)}/{limit} datasets...")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return datasets[:limit]

def save_to_file(datasets, filename="datasets.txt"):
    """Save datasets to file in bot format"""
    
    print(f"\nSaving {len(datasets)} datasets to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Humanoid Network Training Datasets\n")
        f.write("# Auto-generated from Hugging Face API\n")
        f.write(f"# Total datasets: {len(datasets)}\n")
        f.write("# Format: datasetName|datasetUrl\n\n")
        
        for i, dataset in enumerate(datasets, 1):
            f.write(f"{dataset['id']}|{dataset['url']}\n")
            
            # Add separator every 100 items
            if i % 100 == 0:
                f.write(f"\n# --- {i} datasets ---\n\n")
    
    print(f"✓ Successfully saved to {filename}")
    print(f"✓ Total datasets: {len(datasets)}")

def main():
    print("=" * 60)
    print("Hugging Face Dataset Fetcher")
    print("Auto-generate datasets.txt for Humanoid Network Bot")
    print("=" * 60)
    print()
    
    # Configuration
    LIMIT = 1000  # Change this to fetch more/less datasets
    SORT_BY = "downloads"  # Options: downloads, likes, trending, createdAt
    
    # Fetch datasets
    datasets = fetch_huggingface_datasets(limit=LIMIT, sort=SORT_BY)
    
    if not datasets:
        print("No datasets fetched!")
        return
    
    # Show sample
    print("\n" + "=" * 60)
    print("Sample of fetched datasets (first 10):")
    print("=" * 60)
    for i, dataset in enumerate(datasets[:10], 1):
        print(f"{i}. {dataset['id']}")
        print(f"   Downloads: {dataset['downloads']:,} | Likes: {dataset['likes']}")
    print()
    
    # Save to file
    save_to_file(datasets, "datasets.txt")
    
    print("\n" + "=" * 60)
    print("Done! You can now use datasets.txt with your bot.")
    print("=" * 60)

if __name__ == "__main__":
    main()
