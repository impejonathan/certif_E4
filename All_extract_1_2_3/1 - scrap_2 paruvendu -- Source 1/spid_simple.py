# # import scrapy
# # import csv

# # class AutoSpider(scrapy.Spider):
# #     name = 'auto_spider'
    
# #     # URL de départ
# #     start_urls = [
# #         'https://www.paruvendu.fr/fiches-techniques-auto/dacia-sandero/sce-75-urban-stepway-4-cv-essence/10217805/'
# #     ]

# #     def parse(self, response):
# #         # Extraction des données
# #         titre = response.xpath('/html/body/div[3]/div[1]/div[3]/div[1]/div/div[1]/h1/text()').get()
# #         energie = response.xpath('/html/body/div[3]/div[1]/div[5]/div[3]/div[1]/ul/li[2]/span/text()').get()
# #         pneumatiques = response.xpath('//*[@id="auto_pv_ongOn0TAB"]/div/div/table/tbody/tr[8]/td[2]/span/text()').get()

# #         # Création du dictionnaire de données
# #         data = {
# #             'titre': titre.strip() if titre else '',
# #             'energie': energie.strip() if energie else '',
# #             'pneumatiques': pneumatiques.strip() if pneumatiques else ''
# #         }

# #         # Sauvegarde dans un fichier CSV
# #         with open('resultats.csv', 'w', newline='', encoding='utf-8') as f:
# #             writer = csv.DictWriter(f, fieldnames=['titre', 'energie', 'pneumatiques'])
# #             writer.writeheader()
# #             writer.writerow(data)

# #         return data
