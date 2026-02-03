#!/usr/bin/env python3
"""
Scraper for https://books.toscrape.com
Extracts book titles, prices, and star ratings from the homepage
and saves the results to books.csv.
"""

from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup


def scrape_books(url: str) -> pd.DataFrame:
    """
    Download the page and extract book data into a DataFrame.

    Args:
        url: The page URL to scrape.

    Returns:
        A pandas DataFrame with columns: title, price, rating.
    """
    # Map star rating words to numeric values
    rating_map = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    # Send an HTTP GET request to download the page content
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all book containers on the page
    book_containers = soup.find_all("article", class_="product_pod")

    books = []

    # Extract title, price, and star rating for each book
    for book in book_containers:
        # Title is stored in the <a> tag's title attribute
        title_tag = book.find("h3").find("a")
        title = title_tag.get("title", "N/A").strip()

        # Price is in a <p> with class 'price_color'
        price_tag = book.find("p", class_="price_color")
        price_text = price_tag.get_text(strip=True) if price_tag else "£0.00"
        # Some environments decode the pound sign as "Â£", so strip both
        cleaned_price = price_text.replace("Â", "").replace("£", "").strip()
        price = float(cleaned_price)

        # Rating is encoded as a class name on <p class="star-rating ...">
        rating_tag = book.find("p", class_="star-rating")
        rating_classes = rating_tag.get("class", []) if rating_tag else []
        rating_word = rating_classes[1] if len(rating_classes) > 1 else None
        rating = rating_map.get(rating_word, 0)

        books.append({
            "title": title,
            "price": price,
            "rating": rating,
        })

    # Convert the list of dicts to a DataFrame
    return pd.DataFrame(books)


def main() -> None:
    """Run the scraper and save results to books.csv."""
    url = "https://books.toscrape.com"

    # Scrape the page into a DataFrame
    df = scrape_books(url)

    # Save the DataFrame to a CSV file in the same directory as this script
    output_path = Path(__file__).with_name("books.csv")
    df.to_csv(output_path, index=False)

    # Print a short summary of the result
    print(f"Saved {len(df)} books to {output_path}")


if __name__ == "__main__":
    main()
