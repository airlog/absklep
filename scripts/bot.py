from urllib.request import urlopen
from bs4 import BeautifulSoup	
import random

import absklep
from absklep.models import Product, Property

def parsePage(app, category, address):
    with urlopen(address) as f:
        txt = f.read()
        soup = BeautifulSoup(txt)

        p = {}
        for div in soup.find_all('div'):
            if div.get('class') == ['product-list-box']:
                for h2 in div.find_all('h2'):
                    for a in h2.find_all('a'):
                        p['name'] = a.get_text()
                for span in div.find_all('span'):
                    if span.get('class') == ['price']:
                        p['price'] = span.get_text().replace('\xa0', "").replace(',',".")
                        
                p['photo'] = '/static/images/nophoto.png'
                for div2 in div.find_all('div'):
                    if div2.get('class') == ['image-color-container']:
                        for img in div2.find_all('img'):
                            p['photo'] = img.get('src')
                            
                for ul in div.find_all('ul'):
                    p['properties'] = []
                    for li in ul.find_all('li'):
                        value = li.get_text().split(': ')
                        p['properties'].append({ 'key': value[0], 'value': value[1] } )
                
                if p != {}:
                    if '.' in p['price']:
                        price = int(p['price'].replace('.',''))
                    else:
                        price = int(p['price'])*100
                        
                    product = Product(p['name'], price, random.randint(0, 15), description='Ten produkt nie posiada jeszcze opisu.')
                    product.set_photo(p['photo'])
                    for prop in p['properties']:
                        property = Property\
                            .query\
                            .filter(Property.key== prop['key'], Property.value==prop['value'])\
                            .first()
                        if property is None:
                            property = Property(prop['key'],prop['value'])
                        product.properties.append(property)
                    
                    property = Property\
                            .query\
                            .filter(Property.key== 'Kategoria', Property.value==category)\
                            .first()
                    if property is None:
                        property = Property('Kategoria',category)
                    product.properties.append(property)

                    app.db.session.add(product)
                    app.db.session.commit()             
    
def get_vobis_database(app):	
    print('Notebooki')
    for i in [2,3]:
        parsePage(app,"Notebooki","http://www.vobis.pl/wszystkie-kategorie/notebooki/notebooki-3-787.html?str={}".format(i))
    print('Tablety')
    for i in [2,3]:
 	   parsePage(app,"Tablety","http://www.vobis.pl/wszystkie-kategorie/tablety/z-systemem-android-3-844.html?str={}".format(i))
    print('Procesory')
    parsePage(app,"Procesory","http://www.vobis.pl/wszystkie-kategorie/komputery/podzespoly-pc/procesory-3-989.html")
    print('Monitory')
    parsePage(app,"Monitory","http://www.vobis.pl/wszystkie-kategorie/peryferia-i-akcesoria/monitory-3-812.html")
    print('Karty graficzne')
    parsePage(app,"Karty graficzne","http://www.vobis.pl/wszystkie-kategorie/komputery/podzespoly-pc/karty-graficzne-3-990.html")
    print('Klawiatury')
    parsePage(app,"Klawiatury","http://www.vobis.pl/wszystkie-kategorie/peryferia-i-akcesoria/klawiatury-myszki-i-kontrolery/klawiatury-3-1356.html")
    print('Myszki')
    parsePage(app,"Myszki","http://www.vobis.pl/wszystkie-kategorie/peryferia-i-akcesoria/klawiatury-myszki-i-kontrolery/myszki-3-1359.html")
    print('Płyty główne')
    parsePage(app,"Płyty główne","http://www.vobis.pl/wszystkie-kategorie/komputery/podzespoly-pc/plyty-glowne-3-988.html")

if __name__ == '__main__':
    from sys import exit
    
     get_vobis_database(absklep.app)

    exit(0)

