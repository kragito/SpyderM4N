# SpyderM4N

A Python web scraper that crawls the i-intelligence open-enrolment course catalogue, keeps only course pages, removes duplicate links, and saves each course's name, introduction, outline and details.

**Output:** a CSV file with one row per course (example: `I-Int_courses.csv`).

## Prerequisites
- Python installed and added to PATH
- A Python IDE

## Running the script
1. `python3 -m pip install beautifulsoup4`
2. `python3 -m pip install requests`
3. `python3 SpyderV2.py`
