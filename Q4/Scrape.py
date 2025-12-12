import csv
import requests
from bs4 import BeautifulSoup

def scrape_site(url):
    books = []
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    products = soup.select(".product_pod")
    
    for item in products[:5]:
        title = item.h3.a["title"]
        price = item.select_one(".price_color").text
        
        books.append([title, price])
        
    return books

book1_url = "https://books.toscrape.com/catalogue/category/books/travel_2/index.html"
book2_url = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"

book1_data = scrape_site(book1_url)
book2_data = scrape_site(book2_url)

csv_filename = "hotel_prices.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Book", "Book Name", "Price"])
    
    for book in book1_data:
        writer.writerow(["Book A", book[0], book[1]])
        
    for book in book2_data:
        writer.writerow(["Book B", book[0], book[1]])
        
print(f" Data saved in {csv_filename}")

print("\n Retrieved Data from CSV:\n")

with open(csv_filename, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)            