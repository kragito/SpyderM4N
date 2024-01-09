import requests
from bs4 import BeautifulSoup
import csv

def normalize(text):
    """ Normalize text for comparison """
    return text.strip().lower()

def fetch_course_details(course_url):
    """ Fetch and parse individual course details from the course URL """
    headers = {'User-Agent': 'Mozilla/5.0...'}
    try:
        response = requests.get(course_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting product name
        product_name_tag = soup.find('div', class_='product-name').h1
        product_name = product_name_tag.get_text(strip=True) if product_name_tag else 'Not found'

        # Extracting rating
        rating_meta = soup.find('meta', itemprop='ratingValue')
        rating = rating_meta['content'] if rating_meta else 'Not found'

        # Extracting short description
        short_description_div = soup.find('div', class_='short-description')
        if short_description_div:
            short_description_text = short_description_div.get_text(separator='\n', strip=True)
            course_brochure_index = short_description_text.find("Course Brochure")
            short_description = short_description_text[:course_brochure_index] if course_brochure_index != -1 else short_description_text
        else:
            short_description = 'Not found'

        # Extracting SKU
        sku_span = soup.find('div', class_='sku').find('span', class_='value')
        sku = sku_span.get_text(strip=True) if sku_span else 'Not found'

        # Extracting price
        price_span = soup.find('span', class_='price')
        price = price_span.get_text(strip=True) if price_span else 'Not found'

        # Extracting course dates
        select_elements = soup.find_all('select', class_='required-entry product-custom-option')
        dates = []
        for select in select_elements:
            for option in select.find_all('option'):
                if option.get('value'):
                    dates.append(option.get_text().strip())

        # Extracting course topics
        panel_section = soup.find('div', class_='panel')
        topics = []
        topic_name = None  # Initializing topic_name
        topic_points = []  # Initializing topic_points

        if panel_section and 'Course Details' in panel_section.get_text():
            all_elements = panel_section.find_all(['strong', 'ul'])
            for element in all_elements:
                if element.name == 'strong':
                    # If there was a previous topic, append it to topics
                    if topic_name is not None:
                        topics.append({'topic': topic_name, 'points': topic_points})

                    topic_name = element.get_text(strip=True)
                    topic_points = []  # Reset topic_points for new topic

                elif element.name == 'ul':
                    for li in element.find_all('li'):
                        topic_points.append(li.get_text(strip=True))

            # Adding the last topic
            if topic_name is not None:
                topics.append({'topic': topic_name, 'points': topic_points})


        # Storing extracted data in a dictionary
        course_details = {
            'Product Name': product_name,
            'Rating': rating,
            'Short Description': short_description,
            'SKU': sku,
            'Price': price,
            'Course Dates': dates,
            'Course Details': topics
        }

        return course_details

    except requests.RequestException as e:
        print(f"Error fetching URL {course_url}: {e}")
        return {}

def fetch_and_parse(cat_url):
    """ Scrape course url from a given category URL """
    headers = {'User-Agent': 'Mozilla/5.0...'}
    product_urls = []

    try:
        response = requests.get(cat_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        buttons = soup.find_all('button', {'onclick': True})
        
        for button in buttons:
            try:
                onclick_text = button['onclick']
                start = onclick_text.find("('") + 2  # Adjust indices based on actual format
                end = onclick_text.find("')")
                url = onclick_text[start:end]
                if url not in product_urls:
                    product_urls.append(url)
            except Exception as e:
                print(f"Error processing course container: {e}")

    except requests.RequestException as e:
        print(f"Error fetching URL {cat_url}: {e}")

    return product_urls


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
        href = link['href']
        if href.startswith('https://www.tertiarycourses.com.sg'):
            category_urls.append(href)

    return category_urls

def save_results_to_csv(filename, data):
    """ Save the scraped data to a CSV file """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ['Product Name', 'Rating', 'Short Description', 'SKU', 'Price', 'Course Dates', 'Course Details']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for course in data:
            writer.writerow(course)

def main():
    base_url = 'https://www.tertiarycourses.com.sg'
    category_urls = fetch_category_urls(base_url)
    all_courses = []
    count = 0

    for cat_url in category_urls:
        print(f"Scraping category URL: {cat_url}")
        course_urls = fetch_and_parse(cat_url)
        for course_url in course_urls:
            course_details = fetch_course_details(course_url)
            if course_details:
                all_courses.append(course_details)

    save_results_to_csv('NewDetails_courses.csv', all_courses)

if __name__ == "__main__":
    main()
