import requests
from bs4 import BeautifulSoup
import csv
import time
from tqdm import tqdm

start = time.time()
with open('tout.csv', 'w', encoding = 'utf-8') as csv_file:
    write_csv = csv.writer(csv_file, delimiter = ',')
    write_csv.writerow(['product_page_url', 'universal_product_code (upc)', 'title', 'price_including_tax',
                        'price_excluding_tax', 'number_avaliable', 'category', 'review_rating', 'image_url',
                        'product_description'])

    site = "https://books.toscrape.com/"
    request = requests.get(site)

    soupe = BeautifulSoup(request.content, 'html.parser')

    category_names = [html.text.split()[0] for html in soupe.find('ul', {'class': 'nav nav-list'}).find_all('a')][1:]
    category_links = [
                           f"{site}{html['href']}" for html in soupe.find('ul', {'class': 'nav nav-list'}).find_all('a')
                       ][1:]

    pbar = tqdm(total = 1000)
    for category in category_links:

        books_links = [
            f"https://books.toscrape.com/catalogue/{book.find('a')['href'][9:]}" for book in
            BeautifulSoup(requests.get(category).content, 'html.parser').find_all('div', {'class': 'image_container'})
        ]

        for book_link in books_links:
            book_soup = BeautifulSoup(requests.get(book_link).content, 'html.parser')

            book_resume = [texte.text for texte in book_soup.find_all('p')][3][:-8]

            book_category = book_soup.find('ul', {'class': 'breadcrumb'}).find_all('li')[-2].text.split()[0]
            url_image = f"https://books.toscrape.com/{book_soup.find('div', {'class': 'item active'}).find('img')['src'][6:]}"
            book_title = book_soup.find('div', {'class': 'col-sm-6 product_main'}).find('h1').text
            books_avaliables = book_soup.find('p', {'class': 'instock availability'}).text.split()[2].replace('(', '')

            books_stats_table = book_soup.find('table', {'class': 'table table-striped'}).find_all('td')
            upc_livre = books_stats_table[0].text
            prix_sans_taxes = books_stats_table[2].text
            prix_avec_taxes = books_stats_table[3].text

            book_rating = [texte for texte in book_soup.find_all('p')][2]['class'][1]
            if book_rating == 'One':
                note_livre = 1
            elif book_rating == 'Two':
                note_livre = 2
            elif book_rating == 'Three':
                note_livre = 3
            elif book_rating == 'Four':
                note_livre = 4
            else:
                note_livre = 5

            write_csv.writerow([book_link, upc_livre, book_title, prix_avec_taxes, prix_sans_taxes,
                                books_avaliables, book_category, note_livre, url_image,
                                book_resume.replace('"', "'")])
            pbar.update()

        category_soup = BeautifulSoup(requests.get(category).content, 'html.parser')

        if test := category_soup.find('li', {'class': 'next'}):
            if 'index.html' in category:
                category = category.replace('index.html', test.find('a')['href'])
            elif 'page-' in category:
                category = category[:-6].replace('page-', test.find('a')['href'])

            category_links.append(category)
    pbar.close()

print()
print(f"Done in {round(time.time() - start, 2)} seconds")
