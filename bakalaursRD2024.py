import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://www.rdveikals.lv/categories/lv/203/sort/5/filter/0_0_0_0/page/"
SLEEP_INTERVAL = 5
attrlist = []

def get_product_urls():
    product_urls = []
    page_number = 1

    while len(product_urls) < 500:
        catalog_url = BASE_URL + str(page_number)+"/Austi%C5%86as.html"
        response = requests.get(catalog_url)
        soup = BeautifulSoup(response.content, "html.parser")

        container = soup.find('div', class_='catalog-taxons-products-container')
        if container:
            product_names = container.find_all('a', class_='catalog-taxons-product__name')
            for product_name in product_names:
                product_urls.append("https://www.rdveikals.lv/" + product_name['href'])
                if len(product_urls) >= 500:
                    break
        print(len(product_urls))
        page_number += 1
        time.sleep(SLEEP_INTERVAL)

    return product_urls

# Function for parsing a product page
def parse_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Getting price
    try:
        price = soup.find('p', class_='price').text.strip()
    except (TypeError, KeyError):
        price = 'N/A'
    
    # Getting attributes from block "full-info-block simple-content"
    full_info_block = soup.find('div', class_='full-info-block simple-content')
    if full_info_block:
        dd_tags = full_info_block.find_all('dd')
        for i in range(len(dd_tags)):
                try:
                    attr=(dd_tags[i]).a.text.strip()
                    if attr==price:
                        continue
                    else:
                        # print(attr)
                        attrlist.append(attr)
                except:
                    try:
                        attr=(dd_tags[i]).text.strip()
                        if attr==price:
                            continue
                        else:
                            # print(attr)
                            attrlist.append(attr)
                    except:
                        # print("error")
                        attrlist.append("error")
    
    return attrlist, price

# Main function
def main():
    # Get links to products from the catalog
    PRODUCT_URLS = get_product_urls()

    max_attrs_count = 0

    # We get the maximum number of even attributes
    for url in PRODUCT_URLS:
        _, _attrs, _ = parse_product_page(url)
        max_attrs_count = max(max_attrs_count, len(_attrs))

    # Generating headers for even attributes
    _attrs_headers = [f"Attr {i}" for i in range(1, max_attrs_count + 1)]

    # Open the file for writing in UTF-8 encoding
    with open('productsRD2024.csv', 'w', encoding='UTF-8', newline='') as file:
        writer = csv.writer(file)

        # Write headers for even attributes
        writer.writerow(['Nr'] + _attrs_headers)

        for urlcount, url in enumerate(PRODUCT_URLS, start=1):
            percentage = round((urlcount / len(PRODUCT_URLS)) * 100, 2)
            print(f"{urlcount} of {len(PRODUCT_URLS)} - {percentage}%")
            try:
                odd_attrs, attrs, price = parse_product_page(url)
                print("Odd attributes:")
                for attr in odd_attrs:
                    print(attr)
                print("\nEven attributes:")
                for attr in attrs:
                    print(attr)
                print(f"\nPrice: {price}\n{'-'*40}\n")

                # Write even attributes to a CSV file
                if attrs:
                    # Fill in the missing values ​​with an empty line
                    attrs.extend(['' for _ in range(max_attrs_count - len(attrs))])
                    row = [urlcount] + attrs
                    writer.writerow(row)
            except Exception as e:
                print(f"Error processing {url}: {e}")
            time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()
