import csv
import requests
from bs4 import BeautifulSoup

def scrape_site(url):
    rooms = []
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    products = soup.select(".product_pod")
    
    for item in products[:5]:
        title = item.h3.a["title"]
        price = item.select_one(".price_color").text
        
        rooms.append([title, price])
        
    return rooms

hotel1_url = "https://booking-hotels2.tiiny.site/"
hotel2_url = "https://hotel1.tiiny.site/"

hotel1_data = scrape_site(hotel1_url)
hotel2_data = scrape_site(hotel2_url)

csv_filename = "hotel_prices.csv"

with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Hotel", "Room Name", "Price"])
    
    for room in hotel1_data:
        writer.writerow(["Hotel A", room[0], room[1]])
        
    for room in hotel2_data:
        writer.writerow(["Hotel B", room[0], room[1]])
        
print(f" Data saved in {csv_filename}")

print("\n Retrieved Data from CSV:\n")

with open(csv_filename, "r", encoding="utf-8") as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)            