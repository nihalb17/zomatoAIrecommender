
import requests
import json
import time

def test_api():
    url = "http://127.0.0.1:8000/recommend"
    payload = {
        "min_price": 200,
        "max_price": 800,
        "locality": "BTM",
        "min_rating": 4.0,
        "desired_cuisines": ["North Indian", "Biryani"]
    }
    
    print(f"Testing API at {url}...")
    try:
        response = requests.post(url, json=payload, timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("API Response received successfully!")
            print(f"Preferences used: {data['preferences']}")
            print(f"Number of recommendations: {len(data['recommendations'])}")
            for i, rec in enumerate(data['recommendations'][:2]):
                print(f"Rec {i+1}: {rec['restaurant']['name']} - {rec['reason'][:100]}...")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Give the server a moment to start just in case
    time.sleep(2)
    test_api()
