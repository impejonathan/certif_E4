import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import csv
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import asyncio

class AutoSpider(scrapy.Spider):
    name = 'auto_spider'
    
    # Liste des marques de voitures
    marques = [
        'abarth', 'aiways', 'aleko', 'alfa-romeo', 'alpina', 'alpine', 'aro', 'aston-martin', 'audi', 'austin', 
        'auverland', 'bentley', 'bertone', 'bmw', 'buick', 'byd', 'cadillac', 'chevrolet', 'chrysler', 
        'citroen', 'corvette', 'cupra', 'dacia', 'daewoo', 'daihatsu', 'dangel', 'de-la-chapelle', 'dodge', 
        'donkervoort', 'ferrari', 'fiat', 'fisker', 'ford', 'honda', 'hummer', 'hyundai', 'ineos', 'infiniti', 
        'isuzu', 'jaguar', 'jeep', 'kia', 'lada', 'lamborghini', 'lancia', 'land-rover', 'levc', 'lexus', 'lotus', 
        'lynk-co', 'mahindra', 'maruti', 'maserati', 'maybach', 'mazda', 'mclaren', 'mega', 'mercedes', 'mg', 
        'mini', 'mitsubishi', 'morgan', 'nissan', 'opel', 'peugeot', 'pgo', 'polski-fso', 'pontiac', 'porsche', 
        'proton', 'renault', 'rolls-royce', 'rover', 'saab', 'santana', 'seat', 'shuanghuan', 'skoda', 'smart', 
        'ssangyong', 'subaru', 'suzuki', 'talbot', 'tesla', 'toyota', 'tvr', 'venturi', 'volkswagen', 'volvo', 
        'xpeng', 'zeekr'
    ]
    
    # Création de la liste des URL de départ basées sur les marques
    start_urls = [f'https://www.paruvendu.fr/fiches-techniques-auto/{marque}/' for marque in marques]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 32,  # Augmentation des requêtes simultanées
        'CONCURRENT_REQUESTS_PER_DOMAIN': 32,
        'DOWNLOAD_DELAY': 0.5,  # Réduction du délai entre les requêtes
        'COOKIES_ENABLED': False,
        # Configuration du cache
        'HTTPCACHE_ENABLED': True,
        'HTTPCACHE_EXPIRATION_SECS': 86400,
        'HTTPCACHE_DIR': 'httpcache',
        # Optimisation des performances
        'REACTOR_THREADPOOL_MAXSIZE': 20,
        'DOWNLOAD_TIMEOUT': 15,
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        # Middleware pour améliorer la vitesse
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        }
    }

    def __init__(self):
        super().__init__()
        self.urls_to_process = set()
        self.processed_urls = set()
        self.csv_file = open('resultats_autos.csv', 'w', newline='', encoding='utf-8')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=['marque', 'modele', 'annee', 'titre', 'energie', 'pneumatiques'])
        self.csv_writer.writeheader()

    def closed(self, reason):
        self.csv_file.close()

    async def process_urls_async(self, urls, callback, meta=None):
        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = []
            for url in urls:
                if url not in self.processed_urls:
                    self.processed_urls.add(url)
                    futures.append(
                        executor.submit(
                            lambda u: scrapy.Request(
                                u,
                                callback=callback,
                                meta=meta,
                                dont_filter=True
                            ),
                            url
                        )
                    )
            return [future.result() for future in futures]

    def parse(self, response):
        marque = response.url.split('/')[-2]
        modeles_urls = set()
        
        # Extraction rapide des URLs de modèles
        modeles_urls.update(
            urljoin(response.url, url) 
            for url in response.xpath('//a/@href').getall() 
            if 'fiches-techniques-auto' in url and marque in url
        )

        for url in modeles_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_modele,
                meta={'marque': marque},
                dont_filter=True
            )

    def parse_modele(self, response):
        modele = response.url.split('/')[-2]

        # Extraction rapide des années
        annees_urls = set()
        annees_urls.update(
            urljoin(response.url, url) 
            for url in response.xpath('//div[contains(@class, "annee")]//a/@href').getall()
        )

        for url in annees_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_annee,
                meta={
                    'marque': response.meta['marque'],
                    'modele': modele,
                    'annee': url.split('-')[-1].replace('/', '')
                },
                dont_filter=True
            )

    def parse_annee(self, response):
        # Extraction rapide des versions
        versions_urls = set()
        versions_urls.update(
            urljoin(response.url, url) 
            for url in response.xpath('//*[@id="cotefichehcorps"]//a/@href').getall()
        )

        for url in versions_urls:
            yield scrapy.Request(
                url,
                callback=self.parse_version,
                meta=response.meta,
                dont_filter=True
            )

    def parse_version(self, response):
        data = {
            'marque': response.meta['marque'],
            'modele': response.meta['modele'],
            'annee': response.meta['annee'],
            'titre': response.xpath('/html/body/div[3]/div[1]/div[3]/div[1]/div/div[1]/h1/text()').get('').strip(),
            'energie': response.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/div[1]/ul/li[2]/span/text()').get('').strip(),
            'pneumatiques': response.xpath('//*[@id="auto_pv_ongOn0TAB"]/div/div/table/tbody/tr[8]/td[2]/span/text()').get('').strip()
        }
        
        self.csv_writer.writerow(data)

def run_spider():
    process = CrawlerProcess(get_project_settings())
    process.crawl(AutoSpider)
    process.start()

if __name__ == '__main__':
    run_spider()
