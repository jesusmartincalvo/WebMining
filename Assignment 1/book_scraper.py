#!/usr/bin/env python3
"""
Web scraper for books.toscrape.com
Extracts book titles and prices and saves them to a CSV file.
"""

import csv
import requests
from bs4 import BeautifulSoup


def scrape_books(url, max_pages=50):
    """
    Scrape book titles, prices, and ratings from books.toscrape.com
    
    Args:
        url: The base URL to scrape
        max_pages: Maximum number of pages to scrape
    
    Returns:
        List of dictionaries containing book data
    """
    # Rating conversion mapping
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    
    books = []
    
    for page in range(1, max_pages + 1):
        # Construct the URL for each page
        page_url = f"{url}/catalogue/page-{page}.html" if page > 1 else url
        
        print(f"Scraping page {page}...")
        
        try:
            # Send GET request
            response = requests.get(page_url)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all book containers
            book_containers = soup.find_all('article', class_='product_pod')
            
            if not book_containers:
                print(f"No books found on page {page}. Stopping.")
                break
            
            # Extract book information
            for book in book_containers:
                # Extract title
                title_element = book.find('h3').find('a')
                title = title_element.get('title', 'N/A')
                
                # Extract price
                price_element = book.find('p', class_='price_color')
                if price_element:
                    price_text = price_element.text.strip()
                    # Remove £ symbol and convert to float
                    price = float(price_text.replace('£', ''))
                else:
                    price = 0.0
                
                # Extract rating
                rating_element = book.find('p', class_='star-rating')
                if rating_element:
                    rating_class = rating_element.get('class', [])
                    # The second class is the rating (e.g., 'One', 'Two', 'Three')
                    rating_text = rating_class[1] if len(rating_class) > 1 else None
                    rating = rating_map.get(rating_text, 0)
                else:
                    rating = 0
                
                books.append({
                    'title': title,
                    'price': price,
                    'rating': rating
                })
            
            print(f"Found {len(book_containers)} books on page {page}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error scraping page {page}: {e}")
            break
    
    return books


def save_to_csv(books, filename='books.csv'):
    """
    Save book data to a CSV file
    
    Args:
        books: List of dictionaries containing book data
        filename: Name of the CSV file to save
    """
    if not books:
        print("No books to save.")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'price', 'rating']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(books)
    
    print(f"\nSuccessfully saved {len(books)} books to {filename}")


def main():
    """Main function to run the scraper"""
    base_url = "https://books.toscrape.com"
    
    print("Starting book scraper...")
    print(f"Target: {base_url}\n")
    
    # Scrape books
    books = scrape_books(base_url, max_pages=50)
    
    # Save to CSV
    if books:
        save_to_csv(books, 'books.csv')
        print(f"\nTotal books scraped: {len(books)}")
    else:
        print("No books were scraped.")


if __name__ == "__main__":
    main()
