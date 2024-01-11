import csv
import requests
from bs4 import BeautifulSoup

def extract_course_links(html_content):
    """
    Extracts course page URLs from HTML content, allowing only specific URLs and removing duplicates.

    :param html_content: HTML content as a string
    :return: List of unique course URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    
    # Allow only URLs that start with the specified prefix and remove duplicates using a set
    allowed_prefix = 'https://i-intelligence.eu/courses'
    course_urls = {link['href'] for link in links if link['href'].startswith(allowed_prefix)}

    return list(course_urls)

def fetch_course_details(url):
    """
    Fetches and extracts course details such as name, introduction, outline, and additional details from a course page URL.

    :param url: URL of the course page
    :return: Dictionary containing course details
    """
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        course_details = {}

        # Extract course name
        course_name = soup.find('h1')
        course_details['name'] = course_name.get_text().strip() if course_name else 'No Course Name Found'

        # Extract course introduction
        # Assuming the introduction is in a specific div or paragraph - adjust the selector as needed
        intro_section = soup.find('div', class_='course-intro') 
        course_details['introduction'] = intro_section.get_text().strip() if intro_section else 'No Introduction Found'

        # Extract course outline
        # Assuming the outline is in a specific section - adjust the selector as needed
        outline_section = soup.find('div', class_='course-outline')
        if outline_section:
            outline_items = outline_section.find_all('li')
            course_details['outline'] = [item.get_text().strip() for item in outline_items]
        else:
            course_details['outline'] = 'No Outline Found'

        # Extract additional course details
        # Adjust the selector based on the actual structure of your course pages
        details_section = soup.find('div', class_='course-details')
        course_details['details'] = details_section.get_text().strip() if details_section else 'No Additional Details Found'

        return course_details

    return None

def save_results_to_csv(filename, data):
    """
    Save the scraped data to a CSV file.

    :param filename: Name of the file to save data
    :param data: List of dictionaries containing course data
    """
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        for course in data:
            writer.writerow(course)

def main():
    base_url = 'https://i-intelligence.eu/training/open-enrolment-courses'  # Replace with your actual base URL
    response = requests.get(base_url)
    category_urls = extract_course_links(response.text)
    all_courses = []

    for url in category_urls:
        print(f"Scraping course URL: {url}")
        course_details = fetch_course_details(url)
        if course_details:
            all_courses.append(course_details)

    save_results_to_csv('I-Int_courses.csv', all_courses)

if __name__ == "__main__":
    main()
