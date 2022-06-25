import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import click
from datetime import date, datetime
import os

HEADERS={
    'Referrer-Policy':'origin-when-cross-origin',
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.61 Safari/537.36"
}

@click.command()
def main():
    click.echo("This is the Grab Scraper 🐳🐳🐳")
    click.echo('Enter the URL below. It should be similar to https://food.grab.com/my/en/restaurant/burger-king-plaza-low-yat-delivery/1-CYUVMB3DUEABUE')
    url = click.prompt('URL',type=str)
    click.echo('Running the Scraper')
    scrape(url)

def dt_now():
    return datetime.now().strftime('%d-%m-%y-%H-%M')

def scrape(url):

    req = requests.get(url,headers = HEADERS)
    if req.status_code != 200:
        raise ConnectionError('Unable to access URL')
    soup = BeautifulSoup(req.text, 'html.parser')
    click.secho("Webpage Accessed",fg='cyan')
    
    menu_div = soup.find('div',class_=re.compile('menuContentWrapper*'))# 4 is the index of the container
    categories = menu_div.find_all('div',class_=re.compile('category*'))
    
    click.secho("Categories Identified",fg='cyan')
    
    df = []
    for cat in categories:
        category_name = cat.find('h2',class_=re.compile('categoryName'))
        if category_name: # Some weird interaction which creates duplicatess
            category_name =category_name.text
        else:
            continue
        menu_items = cat.find_all('div',class_=re.compile("menuItemWrapper*"))
        for item in menu_items:

            item_name = item.find('h3').text
            item_desc = item.find('h6',class_=re.compile('itemDescription*'))
            item_desc = item_desc.text if item_desc else ""
            
            item_price = float(item.find('h6',class_=re.compile('discountedPrice*')).text)
            
            
            dis_div = item.find('div',class_=re.compile('ant-row itemDiscount*'))
            if dis_div:
                print(f'Discounted Price found for {item_name}')

            info = {
                'name':item_name, 
                'category': category_name,
                'price': item_price,
                'description': item_desc,
            }

            df.append(info)

    df = pd.DataFrame.from_dict(df)
    restaurant_name = url.split('/')[-2]
    df = df.drop_duplicates()
    if not os.path.isdir('output'):
        os.mkdir('output')
    df.to_csv(f'output/{restaurant_name}_{dt_now()}.csv',index=False)
    click.secho("Data Saved",fg='cyan')

    
if __name__ == "__main__":
    main()