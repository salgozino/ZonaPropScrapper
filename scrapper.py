# -*- coding: utf-8 -*-

import cloudscraper
from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_headers import Headers
import re

header = Headers(
    browser="chrome",  # Generate only Chrome UA
    os="win",  # Generate only Windows platform
    headers=False,  # generate misc headers
)
customUserAgent = header.generate()['User-Agent']


class Scrapper():
    def __init__(self, url):
        self.scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
        self.url = url
        # loading web page
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument(f"user-agent={customUserAgent}")
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.driver.get(self.url)

    def _get_attribute(self, value, by=By.CLASS_NAME):
        return self.driver.find_element(by=by, value=value)

    def _get_attributes(self, value, by=By.CLASS_NAME):
        return self.driver.find_elements(by=by, value=value)

    def get_property(self):
        price = self.get_price()
        expensas = self.get_expensas()
        barrio, direccion = self.get_ubicacion()
        features = self.get_features()
        visitas = self.get_users_views()
        return {'precio': price,
                'expensas': expensas,
                'barrio': barrio,
                'direccion': direccion,
                **features,
                **visitas}

    def get_price(self):
        try:
            price = self._get_attribute('price-items')
        except Exception:
            return 'Not Found'
        return price.text

    def get_expensas(self):
        try:
            expensas = self._get_attribute('block-expensas')
            value = int(re.search(r'\d{1,3}(?:\.\d{3})*', expensas.text).group().replace('.', ''))
        except Exception:
            return 'Not Found'
        return value

    def get_ubicacion(self):
        try:
            location = self._get_attribute('title-location')
        except Exception:
            return 'Not Found', 'Not Found'
        barrio = ', '.join(location.text.split('\n')[1].split(', ')[1:3])
        direccion = location.text.split(',')[0]
        return barrio, direccion

    def get_features(self):
        
        features = {
            'superficie_total': None,
            'superficie_cubierta': None,
            'superficie_semi_cubierta': None,
            'balcon': None,
            'superficie_descubierta': None,
            'n_banos': None,
            'antiguedad': None,
            'otros': None,
            'n_dormitorios': None,
            'disposicion': None}
        try:
            attributes = self._get_attribute('section-icon-features')
            items = attributes.find_elements(By.TAG_NAME, "li")
            otros = ""
            for item in items:
                text = item.text
                if 'Total' in text:
                    features['superficie_total'] = text.split(' Total')[0]
                elif 'Cubierta' in text:
                    features['superficie_cubierta'] = text.split(' Cubierta')[0]
                elif 'Baño' in text:
                    features['n_banos'] = text.split(' Baño')[0]
                elif 'Dormitorio' in text:
                    features['n_dormitorios'] = text.split(' Dormitorio')[0]
                elif 'Antiguedad' in text or 'Antigüedad' in text:
                    features['antiguedad'] = text.split(' ')[0]
                elif 'Frente' in text or 'Contrafrente' in text:
                    features['disposicion'] = text
                else:
                    otros.join(text + ', ')
            # remuevo el ultimo ", " de otros si habia algo agregado.
            features['otros'] = otros if len(otros) == 0 else otros[:-2]
            if features['disposicion'] is None:
                features = self.get_disposicion_from_description(features)
        except Exception:
            pass
        return features

    def get_disposicion_from_description(self, features):
        """
        Seartch for Disposicio in the description of the article.
        To be used only of the value is not present in the features field.
        """
        # read long description
        description = self._get_attribute('longDescription')
        if ' contrafrente ' in description.text.lower():
            features['disposicion'] = 'Contrafrente'
        elif ' frente ' in description.text.lower():
            features['disposicion'] = 'Frente'

        return features

    def get_users_views(self):
        try:
            views = self._get_attribute(value='user-views', by=By.ID)
            items = views.find_elements(By.TAG_NAME, 'p')
            publicado = items[0].text.split("Publicado hace ")[1]
            if len(items) == 2:
                visitas = items[1].text.split(" visualizaciones")[0]
            else:
                visitas = "Not Found"
        except Exception:
            return {'publicado_antiguedad': 'Not Found', 'visitas': 'Not Found'}
        return {'publicado_antiguedad': publicado, 'visitas': visitas}


def main(url):
    scrapper = Scrapper(url)

    features = scrapper.get_property()
    print(features)


if __name__ == "__main__":
    url = 'https://www.zonaprop.com.ar/propiedades/impecable-depto-de-2-amb.-a-la-venta-en-recoleta.-47562496.html'
    main(url)
