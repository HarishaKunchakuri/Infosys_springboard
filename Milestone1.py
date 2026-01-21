# Task 7: Same-Domain Crawling Only
# Objective:
# For now, only crawl pages from the same domain as the seed URL.

# Task 8: Save visited URLs to a File
# Objective:
# After the crawl finishes, write all visited URLs into visited.txt.

# Task 9: Add Retry Logic for Failed URLs (Advanced)
# Objective:
# If a URL fails due to temporary issue (network error, timeout), try again a limited number of times.


import requests
import re
import os
import time
from urllib.parse import urljoin, urlparse


# Extracts domain name from a URL
def get_domain(url):
    """
    This function extracts the domain name from a URL.

    - urlparse() splits the URL into components
    - netloc gives the domain name
    - lower() ensures case-insensitive comparison
    """
    return urlparse(url).netloc.lower()


# Downloads a webpage with error classification
def fetch_page(url, timeout=5):
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "WebScourCrawler/1.0"}
        )
        status_code = resp.status_code

        if status_code == 200:
            return resp.text, "ok"

        # Server-side errors (retry possible)
        if 500 <= status_code < 600:
            return None, "transient"

        # Client-side or other errors (do not retry)
        return None, "permanent"

    # Network issues such as timeout or connection error
    except requests.exceptions.RequestException:
        return None, "transient"


# Extracts clean, unique hyperlinks
def extract_links(html, base_url):
    pattern = r'href=["\'](.*?)["\']'
    raw_links = re.findall(pattern, html)

    found = set()

    for link in raw_links:
        link = link.strip()

        # Skip empty links
        if not link:
            continue

        # Skip non-navigational links
        if link.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        # Convert relative URL to absolute
        abs_link = urljoin(base_url, link)

        # Remove fragment (#section) from URL
        abs_link = urlparse(abs_link)._replace(fragment="").geturl()

        # Remove trailing slash
        abs_link = abs_link.rstrip("/")

        # Accept only HTTP/HTTPS links
        if abs_link.startswith("http://") or abs_link.startswith("https://"):
            found.add(abs_link)

    return list(found)

seed_url = "https://scrapelead.io/blog/13-most-popular-websites-to-scrape-in-2025/"
max_pages = 20          # Maximum number of pages to crawl
max_retries = 3         # Retry limit for transient errors
retry_delay = 0.5         # Delay between retries (seconds)

# Create directory to store downloaded pages
os.makedirs("pages", exist_ok=True)

seed_domain = get_domain(seed_url)

queue = [seed_url.rstrip("/")]  # BFS queue
visited = []                    # List to store visited URLs (ordered)
visited_set = set()             # Set for fast duplicate checking
retries = {}                    # Dictionary to track retry count per URL
failed = set()                  # Set to store failed URLs
page_id = 1                     # File counter

start_time = time.time()


# Main crawling loop
while queue and len(visited) < max_pages:

    # Get next URL from queue
    url = queue.pop(0)

    # Skip if already visited
    if url in visited_set:
        continue

    # Fetch page
    html, status = fetch_page(url)

    # Case 1: Successful fetch
    if status == "ok" and html is not None:

        # Save HTML content to file
        filename = os.path.join("pages", f"{page_id}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved: {filename}",f"Time: {time.time()-start_time:.2f} sec")

        page_id += 1
        visited.append(url)
        visited_set.add(url)

        # Extract and enqueue links from same domain
        links = extract_links(html, url)
        for link in links:
            if get_domain(link) != seed_domain:
                continue
            if link not in visited_set and link not in queue:
                queue.append(link)

    # Case 2: Transient failure
    elif status == "transient":
        count = retries.get(url, 0) + 1
        if count <= max_retries:
            retries[url] = count
            print(f"Transient error for {url}. Retry {count}/{max_retries}. Re-queueing.")
            time.sleep(retry_delay)
            queue.append(url)
        else:
            print(f"Failed after {max_retries} retries: {url}")
            failed.add(url)

    # Case 3: Permanent failure
    else:
        print(f"Permanent failure (skipping): {url}")
        failed.add(url)

    # Polite delay between requests
    time.sleep(0.5)


# Save visited URLs and print results
elapsed = time.time() - start_time

visited_file = os.path.join("pages", "visited.txt")
with open(visited_file, "w", encoding="utf-8") as vf:
    for u in visited:
        vf.write(u + "\n")
print()
print(f"\nSeed URL: {seed_url}")
print(f"Max pages limit: {max_pages}")
print(f"Time taken: {elapsed:.2f} seconds")
print("Total pages crawled:", len(visited))
print("Visited URLs saved to:", visited_file)
print(f"Final queue size: {len(queue)}")

if failed:
    print("Failed URLs:", len(failed))



# output:
# Saved: pages/1.html Time: 0.89 sec
# Permanent failure (skipping): https://scrapelead.io/e-commerce/ebay-listings-web-data-scraper
# Saved: pages/2.html Time: 2.51 sec
# Saved: pages/3.html Time: 3.55 sec
# Saved: pages/4.html Time: 4.17 sec
# Saved: pages/5.html Time: 5.08 sec
# Saved: pages/6.html Time: 6.08 sec
# Saved: pages/7.html Time: 7.10 sec
# Saved: pages/8.html Time: 8.16 sec
# Saved: pages/9.html Time: 9.28 sec
# Saved: pages/10.html Time: 10.25 sec
# Saved: pages/11.html Time: 11.31 sec
# Saved: pages/12.html Time: 12.33 sec
# Saved: pages/13.html Time: 13.13 sec
# Saved: pages/14.html Time: 14.27 sec
# Saved: pages/15.html Time: 14.91 sec
# Saved: pages/16.html Time: 15.87 sec
# Saved: pages/17.html Time: 16.80 sec
# Saved: pages/18.html Time: 17.84 sec
# Saved: pages/19.html Time: 19.10 sec
# Saved: pages/20.html Time: 19.72 sec


# Seed URL: https://scrapelead.io/blog/13-most-popular-websites-to-scrape-in-2025/
# Max pages limit: 20
# Time taken: 20.23 seconds
# Total pages crawled: 20
# Visited URLs saved to: pages/visited.txt
# Final queue size: 220
# Failed URLs: 1