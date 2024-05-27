import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.1a.lv/c/datortehnika-preces-birojam/austinas-mikrofoni-un-datoru-skalruni/austinas/2tx?page="
SLEEP_INTERVAL = 5

def get_product_urls():
    product_urls = []
    page_number = 1

    while len(product_urls) < 500:
        catalog_url = BASE_URL + str(page_number)
        response = requests.get(catalog_url)
        soup = BeautifulSoup(response.content, "html.parser")

        container = soup.find('div', class_='catalog-taxons-products-container')
        if container:
            product_names = container.find_all('a', class_='catalog-taxons-product__name')
            for product_name in product_names:
                product_urls.append("https://www.1a.lv" + product_name['href'])
                if len(product_urls) >= 500:
                    break
        
        page_number += 1
        time.sleep(SLEEP_INTERVAL)

    return product_urls

# Function for parsing a product page
def parse_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Getting price
    try:
        price = soup.find('div', {'class': 'product-controls'})['data-price']
    except (TypeError, KeyError):
        price = 'N/A'
    
    # Getting attributes from block "full-info-block simple-content"
    odd_attrlist = []
    even_attrlist = []
    full_info_block = soup.find('div', class_='full-info-block simple-content')
    if full_info_block:
        dd_tags = full_info_block.find_all('td')
        filtered_dd_tags = [tag for tag in dd_tags if not tag.get('colspan')]
        for i, tag in enumerate(filtered_dd_tags):
            # Removing <span> tags
            for span in tag.find_all('span'):
                span.decompose()
            text = tag.text.strip()
            if text and text != price:
                if i % 2 == 0:
                    odd_attrlist.append(text)
                else:
                    even_attrlist.append(text)
    
    return odd_attrlist, even_attrlist, price

# Main function
def main():
    # Get links to products from the catalog
    PRODUCT_URLS = get_product_urls()

    max_even_attrs_count = 0

    # We get the maximum number of even attributes
    for url in PRODUCT_URLS:
        _, even_attrs, _ = parse_product_page(url)
        max_even_attrs_count = max(max_even_attrs_count, len(even_attrs))

    # Generating headers for even attributes
    even_attr_headers = [f"Attr {i}" for i in range(1, max_even_attrs_count + 1)]

    # Open the file for writing in UTF-8 encoding
    with open('products1a2024.csv', 'w', encoding='UTF-8', newline='') as file:
        writer = csv.writer(file)

        # Write headers for even attributes
        writer.writerow(['Nr'] + even_attr_headers)

        for urlcount, url in enumerate(PRODUCT_URLS, start=1):
            percentage = round((urlcount / len(PRODUCT_URLS)) * 100, 2)
            print(f"{urlcount} of {len(PRODUCT_URLS)} - {percentage}%")
            try:
                odd_attrs, even_attrs, price = parse_product_page(url)
                print("Odd attributes:")
                for attr in odd_attrs:
                    print(attr)
                print("\nEven attributes:")
                for attr in even_attrs:
                    print(attr)
                print(f"\nPrice: {price}\n{'-'*40}\n")

                # Write even attributes to a CSV file
                if even_attrs:
                    # Fill in the missing values ​​with an empty line
                    even_attrs.extend(['' for _ in range(max_even_attrs_count - len(even_attrs))])
                    row = [urlcount] + even_attrs
                    writer.writerow(row)
            except Exception as e:
                print(f"Error processing {url}: {e}")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
