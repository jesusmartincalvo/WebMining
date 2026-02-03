#!/usr/bin/env python3
"""
Web scraper for durex.co.uk
Extracts relevant content including products, categories, and information.
"""

import csv
import requests
from bs4 import BeautifulSoup
import time


def get_page_content(url):
    """
    Fetch and parse a webpage
    
    Args:
        url: The URL to fetch
    
    Returns:
        BeautifulSoup object or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def scrape_products(base_url):
    """
    Scrape product information from durex.co.uk
    
    Args:
        base_url: The base URL to scrape
    
    Returns:
        List of dictionaries containing product data
    """
    products = []
    
    print("Fetching main page...")
    soup = get_page_content(base_url)
    
    if not soup:
        print("Failed to fetch main page")
        return products
    
    # Find product links and information
    # Note: The exact selectors may need adjustment based on the actual website structure
    product_elements = soup.find_all(['article', 'div'], class_=lambda x: x and any(
        keyword in str(x).lower() for keyword in ['product', 'item', 'card']
    ))
    
    print(f"Found {len(product_elements)} potential product elements")
    
    for idx, element in enumerate(product_elements, 1):
        # Extract product name
        title_elem = element.find(['h1', 'h2', 'h3', 'h4'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['title', 'name', 'product']
        ))
        if not title_elem:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4'])
        
        title = title_elem.get_text(strip=True) if title_elem else 'N/A'
        
        # Extract description
        desc_elem = element.find(['p', 'div'], class_=lambda x: x and any(
            keyword in str(x).lower() for keyword in ['description', 'desc', 'summary']
        ))
        description = desc_elem.get_text(strip=True) if desc_elem else 'N/A'
        
        # Extract link
        link_elem = element.find('a', href=True)
        link = link_elem['href'] if link_elem else 'N/A'
        if link != 'N/A' and not link.startswith('http'):
            link = base_url.rstrip('/') + '/' + link.lstrip('/')
        
        # Extract category/type if available
        category_elem = element.find(class_=lambda x: x and 'category' in str(x).lower())
        category = category_elem.get_text(strip=True) if category_elem else 'N/A'
        
        if title != 'N/A' or description != 'N/A':
            products.append({
                'title': title,
                'description': description[:200] if description != 'N/A' else 'N/A',
                'category': category,
                'link': link
            })
            
            if idx <= 5:  # Print first few for debugging
                print(f"  - {title}")
        
        # Be respectful with rate limiting
        if idx % 10 == 0:
            time.sleep(0.5)
    
    return products


def scrape_page_content(url):
    """
    Extract general content from the page including headings, links, and text
    
    Args:
        url: The URL to scrape
    
    Returns:
        Dictionary with page content
    """
    print(f"\nAnalyzing page structure...")
    soup = get_page_content(url)
    
    if not soup:
        return {}
    
    content = {
        'title': '',
        'headings': [],
        'main_text': [],
        'links': [],
        'meta_description': ''
    }
    
    # Page title
    if soup.title:
        content['title'] = soup.title.get_text(strip=True)
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc and meta_desc.get('content'):
        content['meta_description'] = meta_desc['content']
    
    # Main headings
    for heading in soup.find_all(['h1', 'h2', 'h3'], limit=20):
        text = heading.get_text(strip=True)
        if text and len(text) > 3:
            content['headings'].append(text)
    
    # Main content paragraphs
    for p in soup.find_all('p', limit=30):
        text = p.get_text(strip=True)
        if text and len(text) > 20:
            content['main_text'].append(text[:150])
    
    # Navigation links
    for link in soup.find_all('a', href=True, limit=50):
        href = link['href']
        text = link.get_text(strip=True)
        if text and href and not href.startswith('#'):
            if not href.startswith('http'):
                href = url.rstrip('/') + '/' + href.lstrip('/')
            content['links'].append({'text': text, 'url': href})
    
    return content


def save_products_to_csv(products, filename='durex_products.csv'):
    """
    Save product data to CSV
    
    Args:
        products: List of product dictionaries
        filename: Output filename
    """
    if not products:
        print("No products to save.")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'description', 'category', 'link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(products)
    
    print(f"\nSuccessfully saved {len(products)} products to {filename}")


def save_content_summary(content, filename='durex_content.txt'):
    """
    Save page content summary to a text file
    
    Args:
        content: Dictionary with page content
        filename: Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== DUREX.CO.UK CONTENT ANALYSIS ===\n\n")
        
        if content.get('title'):
            f.write(f"PAGE TITLE: {content['title']}\n\n")
        
        if content.get('meta_description'):
            f.write(f"META DESCRIPTION: {content['meta_description']}\n\n")
        
        if content.get('headings'):
            f.write("MAIN HEADINGS:\n")
            for idx, heading in enumerate(content['headings'], 1):
                f.write(f"  {idx}. {heading}\n")
            f.write("\n")
        
        if content.get('main_text'):
            f.write("MAIN CONTENT EXCERPTS:\n")
            for idx, text in enumerate(content['main_text'][:10], 1):
                f.write(f"  {idx}. {text}...\n")
            f.write("\n")
        
        if content.get('links'):
            f.write("KEY LINKS:\n")
            for idx, link in enumerate(content['links'][:20], 1):
                f.write(f"  {idx}. {link['text']} -> {link['url']}\n")
            f.write("\n")
    
    print(f"Content summary saved to {filename}")


def main():
    """Main function to run the scraper"""
    base_url = "https://www.durex.co.uk"
    
    print("Starting Durex UK content scraper...")
    print(f"Target: {base_url}\n")
    
    # First, analyze the page structure and content
    content = scrape_page_content(base_url)
    
    if content:
        print(f"\nPage Title: {content.get('title', 'N/A')}")
        print(f"Found {len(content.get('headings', []))} headings")
        print(f"Found {len(content.get('main_text', []))} text sections")
        print(f"Found {len(content.get('links', []))} links")
        
        save_content_summary(content, 'durex_content.txt')
    
    # Try to scrape products
    print("\n" + "="*50)
    products = scrape_products(base_url)
    
    if products:
        save_products_to_csv(products, 'durex_products.csv')
        print(f"Total products/items found: {len(products)}")
    else:
        print("\nNote: No products found with default selectors.")
        print("The website structure may require custom parsing.")
        print("Check durex_content.txt for general page content.")


if __name__ == "__main__":
    main()
