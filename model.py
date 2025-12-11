import requests
import time

def fetch_huggingface_models(limit=1000, sort="downloads"):
    """
    Fetch models from Hugging Face API
    
    Args:
        limit: Number of models to fetch (default: 1000)
        sort: Sort method - "downloads", "likes", "trending", "createdAt"
    """
    
    print(f"Fetching {limit} models from Hugging Face...")
    print(f"Sort by: {sort}\n")
    
    models = []
    page = 0
    per_page = 100  # API limit per request
    
    while len(models) < limit:
        try:
            # Hugging Face API endpoint
            url = "https://huggingface.co/api/models"
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
                print("No more models found.")
                break
            
            for model in batch:
                model_id = model.get('id') or model.get('modelId')
                if model_id:
                    models.append({
                        'id': model_id,
                        'url': f"https://huggingface.co/{model_id}",
                        'downloads': model.get('downloads', 0),
                        'likes': model.get('likes', 0)
                    })
                
                if len(models) >= limit:
                    break
            
            page += 1
            print(f"Fetched {len(models)}/{limit} models...")
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"Error: {e}")
            break
    
    return models[:limit]

def save_to_file(models, filename="models.txt"):
    """Save models to file in bot format"""
    
    print(f"\nSaving {len(models)} models to {filename}...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("# Humanoid Network Training Models\n")
        f.write("# Auto-generated from Hugging Face API\n")
        f.write(f"# Total models: {len(models)}\n")
        f.write("# Format: fileName|fileUrl\n\n")
        
        for i, model in enumerate(models, 1):
            f.write(f"{model['id']}|{model['url']}\n")
            
            # Add separator every 100 models
            if i % 100 == 0:
                f.write(f"\n# --- {i} models ---\n\n")
    
    print(f"✓ Successfully saved to {filename}")
    print(f"✓ Total models: {len(models)}")

def main():
    print("=" * 60)
    print("Hugging Face Model Fetcher")
    print("Auto-generate models.txt for Humanoid Network Bot")
    print("=" * 60)
    print()
    
    # Configuration
    LIMIT = 1000  # Change this to fetch more/less models
    SORT_BY = "downloads"  # Options: downloads, likes, trending, createdAt
    
    # Fetch models
    models = fetch_huggingface_models(limit=LIMIT, sort=SORT_BY)
    
    if not models:
        print("No models fetched!")
        return
    
    # Show sample
    print("\n" + "=" * 60)
    print("Sample of fetched models (first 10):")
    print("=" * 60)
    for i, model in enumerate(models[:10], 1):
        print(f"{i}. {model['id']}")
        print(f"   Downloads: {model['downloads']:,} | Likes: {model['likes']}")
    print()
    
    # Save to file
    save_to_file(models, "models.txt")
    
    print("\n" + "=" * 60)
    print("Done! You can now use models.txt with your bot.")
    print("=" * 60)

if __name__ == "__main__":
    main()
