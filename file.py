import requests
import pandas as pd
from lxml import etree
import os


def extract_data_from_page(url, category):
    """
    Extracts hotel details from a given hotel detail URL.

    Parameters:
        url (str): URL of the hotel detail page.
        category (str): Category of the hotel.

    Returns:
        dict: A dictionary containing extracted hotel details.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        tree = etree.HTML(response.text)

        # Extract hotel details using XPath
        hotel_name = tree.xpath('//h1[@itemprop="name"]//text()')
        hotel_name = hotel_name[0].strip() if hotel_name else "N/A"

        address = tree.xpath(
            '(//div[@class="resort-details__item"])[2]/text() | '
            '//div[@class="dive-center-infobox"]//div[@class="info"]/h5[contains(., "Address")]/following-sibling::a/p/text() |'
            '(//div[@id="highlights-description"]/div/p)[last()]/text()'
        )
        address = address[0].strip() if address else "N/A"
        address = address.split(':') if address != "N/A" else []
        address = address[-1].strip() if len(address) > 0 else 'N/A'

        website = tree.xpath(
            '//div[@class="dive-center-infobox"]//div[@class="info"]/h5[contains(., "WEBSITE")]/following-sibling::p/a/@href'
        )
        website = website[0].strip() if website else "N/A"

        phone = tree.xpath(
            '//div[@class="dive-center-infobox"]//div[@class="info"]/h5[contains(., "Phone")]/following-sibling::p/a/text()'
        )
        phone = phone[0].strip() if phone else "N/A"

        email = tree.xpath(
            '//div[@class="dive-center-infobox"]//div[@class="info"]/h5[contains(., "Email")]/following-sibling::p/a/text()'
        )
        email = email[0].strip() if email else "N/A"

        activities = tree.xpath(
            '(//div[@class="dive-center-infobox"])[1]//div[@class="info"]/h5[contains(., "Activities offered")]/following-sibling::p[1]/text()'
        )
        activities = activities[0].strip() if activities else "N/A"

        return {
            "Category": category,
            "Name": hotel_name,
            "Activities": activities,
            "Address": address,
            "Phone": phone,
            "Email": email,
            "Website": website,
            "URL": url,
        }

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed for URL: {url} | Error: {e}")
    except Exception as e:
        print(f"Error extracting data from URL: {url} | Error: {e}")

    return {}


def fetch_resort_urls(page, category):
    """
    Fetches resort data from the specified API and extracts URLs.

    Parameters:
        page (int): The page number to fetch.
        category (str): The category of the resorts.

    Returns:
        tuple: A list of resort URLs and the next page link.
    """
    if category in ['dive-trips', 'courses', 'snorkelling']:
        url = f'https://travel.padi.com/api/adventure/v1/search/continent/all/{category}/'
    else:
        url = f"https://travel.padi.com/api/v2/travel/search/continent/all/{category}/"

    querystring = {"page_size": "100", "page": str(page)}
    headers = {
        "Content-Type": "application/json",
        "Referer": f"https://travel.padi.com/s/dive-resorts/all/?page={page}",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        ),
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=30)
        response.raise_for_status()
        data = response.json()

        resorts = data.get("results", [])
        if category in ['dive-trips', 'courses', 'snorkelling']:
            urls = [ [resort.get("activityPage") , category] for resort in resorts if resort.get("activityPage")]
        else:
            urls = [ [resort.get("url") , category] for resort in resorts if resort.get("url")]

        return urls, data.get("next")

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return [], None


def save_to_excel(data, output_file):
    """
    Saves the data to an Excel file.

    Parameters:
        data (list): List of dictionaries containing the data to save.
        output_file (str): Path to the output Excel file.
    """
    try:
        df = pd.DataFrame(data)
        if os.path.exists(output_file):
            old_data = pd.read_excel(output_file)
            df = pd.concat([old_data, df], ignore_index=True)
        df.to_excel(output_file, index=False)
    except Exception as e:
        print(f"Error saving data to Excel: {e}")


if __name__ == "__main__":
    url_file = 'tarve_padi_urls.xlsx'
    output_file = 'tarve_padi_data.xlsx'
    output_backup_file = 'tarve_padi_data_backup.xlsx'
    base_url = "https://travel.padi.com"

    # Backup existing output file
    if os.path.exists(output_file):
        if os.path.exists(output_backup_file):
            os.remove(output_backup_file)
        os.rename(output_file, output_backup_file)

    categories = ['liveaboards', 'resorts', 'dive-centers', 'dive-trips', 'courses', 'snorkelling']
    all_urls = []

    for category in categories:
        page = 1
        print(f"Processing category: {category}")
        while True:
            resort_urls, next_page = fetch_resort_urls(page, category)
            if resort_urls:
                print(f'category: {category} page : {page} got urls : {len(resort_urls)}')
                all_urls.extend(resort_urls)
                page += 1
                if not next_page or (category in ['dive-centers', 'dive-trips', 'courses'] and page > 30):
                    break
            else:
                break

    print(f"Total URLs found: {len(all_urls)}")
    pd.DataFrame(all_urls, columns=['URL' , 'Category']).to_csv('all_urls.csv', index=False)

    data_urls = pd.read_csv('all_urls.csv')['URL'].to_list()
    categories = pd.read_csv('all_urls.csv')['Category'].to_list()
    all_data = []

    for i, link in enumerate(data_urls):
        try:
            print(f"Processing {i + 1}/{len(data_urls)}: { link}")
            full_url = link 
            if categories[i] == 'dive-centers':
                full_url = base_url + link
            data = extract_data_from_page(full_url ,category=categories[i] )
            if data:
                all_data.append(data)
            if i % 10 == 0 and all_data:
                save_to_excel(all_data, output_file)
                all_data = []
        except Exception as e:
            print(f"Error processing URL {link}: {e}")

    if all_data:
        save_to_excel(all_data, output_file)

    print("Script execution completed.")
