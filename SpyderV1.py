import requests
from bs4 import BeautifulSoup
import csv

def normalize(text):
    """ Normalize text for comparison """
    return text.strip().lower()

def fetch_and_parse(url):
    """ Scrape course data from a given category URL """
    headers = {'User-Agent': 'Mozilla/5.0...'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

    courses = []
    course_containers = soup.find_all('div', class_='product-shop grid12-5 mobile-grid-half')

    for container in course_containers:
        course = {}
        course['name'] = container.find('h2', class_='product-name').get_text().strip() if container.find('h2', class_='product-name') else 'No name available'
        course['description'] = container.find('div', class_='desc std').get_text().strip() if container.find('div', class_='desc std') else 'No description available'
        price_container = container.find_next_sibling('div', class_='right-column grid12-3 mobile-grid-half')
        course['gst_price'] = price_container.find('div', class_='gst_tax').find('span', class_='price').get_text().strip() if price_container and price_container.find('div', class_='gst_tax') else 'No GST price available'
        courses.append(course)
    
    return courses

def fetch_category_urls(url):
    """ Fetch and parse category URLs from the main page """
    headers = {'User-Agent': 'Mozilla/5.0...'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching main URL {url}: {e}")
        return []

    category_urls = []
    for link in soup.select('.block-content a[href]'):
        category_urls.append(link['href'])

    return category_urls

def save_results_to_csv(filename, data):
    """ Save the scraped data to a CSV file """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'description', 'gst_price'])
        writer.writeheader()
        for course in data:
            writer.writerow(course)

def main():
    base_url = 'https://www.tertiarycourses.com.sg'
    try:
        category_urls = fetch_category_urls(base_url)
    except Exception as e:
        print(f"An error occurred while fetching category URLs: {e}")
        return

    all_courses = []
    for url in category_urls:
        print(f"Scraping category URL: {url}")
        category_data = fetch_and_parse(url)
        all_courses.extend(category_data)

    save_results_to_csv('aggregated_courses.csv', all_courses)

if __name__ == "__main__":
    main()
