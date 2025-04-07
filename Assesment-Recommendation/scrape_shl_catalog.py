import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

URL = "https://www.shl.com/solutions/products/product-catalog/"
base_url = "https://www.shl.com"

response = requests.get(URL)
html_content = response.content

soup = BeautifulSoup(html_content, "html.parser")
pagination = soup.find("ul", class_="pagination")

assessments = []
if pagination:
    page_links = pagination.find_all("a")
    page_numbers = []

    for link in page_links:
        try:
            number = int(link.text.strip())
            page_numbers.append(number)
        except:
            continue

    total_pages = max(page_numbers) if page_numbers else 1
else:
    total_pages = 1

for page in range(1, total_pages+1):
    start = (page - 1) * 10
    url = f"{URL}?start={start}&type=2"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    for item in soup.find_all("tr", attrs={"data-course-id": True}):
        a_tag = item.find("a")
        name = a_tag.text.strip() if a_tag else "N/A"
        
        # assessment link
        link = a_tag["href"] if a_tag and a_tag.has_attr("href") else "N/A"
        
        # remote testing
        tds = item.find_all("td", class_="custom__table-heading__general")
        remote_testing = "-yes" in tds[0].find("span", class_="catalogue__circle").get("class", []) if len(tds) > 0 and tds[0].find("span") else False
        
        # adaptive/IRT support
        adaptive = "-yes" in tds[1].find("span", class_="catalogue__circle").get("class", []) if len(tds) > 1 and tds[1].find("span") else False
        
        # Test type
        key_cell = item.find("td", class_="product-catalogue__keys")
        test_type = [span.text.strip() for span in key_cell.find_all("span", class_="product-catalogue__key")] if key_cell else []
        
        # duration
        full_link = base_url + link
        details_res = requests.get(full_link)
        detail_soup = BeautifulSoup(details_res.content, "html.parser")
        
        duration_tag = detail_soup.find("p", string=lambda text: text and "Approximate Completion Time" in text)
        match = re.search(r"= (\d+)", duration_tag.text) if duration_tag else None
        duration = int(match.group(1)) if match else "N/A"
        
        assessments.append({
            "Name": name,
            "Assessment Link" : base_url + link,
            "Remote testing" : remote_testing,
            "Adaptive/IRT" : adaptive,
            "Test Type": test_type,
            "Duration (min)" : duration,
        })

df = pd.DataFrame(assessments)
df.to_csv("shl_assessments.csv", index=False)

print("Scraping completed! Data saved to shl_assessments.csv")
