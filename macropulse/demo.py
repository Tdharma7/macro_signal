import requests

task_id = input("Enter a task ID: ")
url = f"https://jsonplaceholder.typicode.com/todos/{task_id}"

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    data = response.json()
    print("Title:", data["title"])

except requests.exceptions.Timeout:
    print("The server took too long. Try again.")

except requests.exceptions.ConnectionError:
    print("Could not connect. Check your internet connection.")

except requests.exceptions.HTTPError:
    print("The server returned an error.")
    print("Status:", response.status_code)