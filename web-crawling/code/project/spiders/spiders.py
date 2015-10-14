from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

# Importer la classe de l'item par defaut
from project.items import Product

# Definition de la classe Spider pour le site seLoger
class seLogerSpider(CrawlSpider):
    
    #Nom
    name = "seLogerSpider"
    
    # Domaine
    allowed_domains = ["seloger.com"]
    
    # Url par laquelle commence la fouille
    start_urls = [
        "http://www.seloger.com/immobilier/achat/immo-paris-6eme-75/",
    ]
    
    # La regle de fouille consiste a tourner les pages
    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//a[@class="pagination_next active"]',)), callback="parse_url", follow= True),
    )

    # Sur chaque page fouillee, on obtenient les url des pages qui
    # correspondent a des biens immobiliers, sur chacune desquelles le 
    # callback |parse_item| s'execute.
    def parse_url(self, response):
        
        # Voir la syntaxe standard XPATH
        sel = Selector(response)
        sites = sel.xpath('//div[@class="price "]')

        for site in sites:
            s_url = site.xpath('a/@href').extract()[0]
            yield Request(s_url, callback = self.parse_item)
    
    # Pour chaque page (bien immobilier), |parse_item| permet d'obtenir les 
    # details de l'annonce : url de la page, prix, texte de l'annonce ..., qui
    # vont nous servir pour l'extraction des caracteristiques du bien
    # immobilier.
    def parse_item(self, response):
        
        sel = Selector(response)
        
        # Le bien immobilier pour la page analysee est decrit par un objet
        # de type |Product()|, dont les attributs sont declares dans le fichier
        # |items.py|.
        item = Product()
        
        # Attribut url : url de la page analysee
        item['url'] = response.url
        
        # Cherche la description sur la page : texte de l'annonce
        s_description = sel.xpath('//p[@class="description"]/text()').extract()[0]
        
        # Cherche la description contenue dans le tableau : infos
        # additionnelles, separees par des sauts de ligne
        li_items = sel.xpath('//ol[@class="description-liste"]/li')
        s_description_liste = '';
        
        for li in li_items:
            s_li = li.xpath('@title').extract()[0]
            # supprime les espaces en fin de string
            s_li = s_li.strip()
            # concatene la string extraite apres une virgule seulement si elle
            # est non vide
            if s_li:
                s_description_liste = s_description_liste.strip() + ' ' + s_li + ','
               
        # enlever la derniere virgule
        s_description_liste = s_description_liste[:-1]
        
        # Attributs description et infos : le texte de l'annonce et les infos
        # aditionnelles
        item['description'] = s_description
        item['infos'] = s_description_liste
        
        # Attribut titre : titre de l'annonce
        item['titre'] = sel.xpath('//h1[@class="detail-title"]/text()').extract()[0]
        
        # Attribut prix : prix d'annonce
        item['prix'] = sel.xpath('//span[@id="price"]/text()').extract()[0]
        
        # Renvoie l'objet ainsi cree
        return item
        
# Definition de la classe Spider pour le site explorImmo
class exploreimmoSpider(CrawlSpider):
    
    #Nom
    name = "explorimmoSpider"
    
    # Domaine
    allowed_domains = ["explorimmo.com"]
    
    # Url par laquelle commence la fouille
    start_urls = [
        "http://www.explorimmo.com/immobilier-vente-bien-paris.html",
    ]
    
    # La regle de fouille consiste a tourner les pages
    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//a[@class="sprEI fw"]',)), callback="parse_url", follow= True),
    )

    # Sur chaque page fouillee, on obtenient les url des pages qui
    # correspondent a des biens immobiliers, sur chacune desquelles le 
    # callback |parse_item| s'execute.
    def parse_url(self, response):
        
        # Voir la syntaxe standard XPATH
        sel = Selector(response)
        sites = sel.xpath('//h2[@itemprop="name"]')

        for site in sites:
            s_url = site.xpath('a/@href').extract()[0]
            s_url = 'http://www.explorimmo.com' + s_url
            yield Request(s_url, callback = self.parse_item)
    
    # Pour chaque page (bien immobilier), |parse_item| permet d'obtenir les 
    # details de l'annonce : url de la page, prix, texte de l'annonce ..., qui
    # vont nous servir pour l'extraction des caracteristiques du bien
    # immobilier.
    def parse_item(self, response):
        
        sel = Selector(response)
        
        # Le bien immobilier pour la page analysee est decrit par un objet
        # de type |Product()|, dont les attributs sont declares dans le fichier
        # |items.py|.
        item = Product()
        
        # Attribut url : url de la page analysee
        item['url'] = response.url
        
        # Cherche la description sur la page : texte de l'annonce
        s_description = sel.xpath('//div[@itemprop="description"]/p/text()').extract()[0]
        
        # Cherche la description contenue dans le tableau : infos
        # additionnelles, separees par des sauts de ligne
#        li_items = sel.xpath('//div[@itemprop="description"]/li')
        s_description_liste = '';
        
#        for li in li_items:
#            s_li = li.xpath('text()').extract()[0]
#            # supprime les espaces en fin de string
#            s_li = s_li.strip()
#            # concatene la string extraite apres une virgule seulement si elle
#            # est non vide
#            if s_li:
#                s_description_liste = s_description_liste.strip() + ' ' + s_li + ','
#               
#        # enlever la derniere virgule
#        s_description_liste = s_description_liste[:-1]
        
        # Attribut description : le texte de l'annonce et les infos
        # aditionnelles
        item['description'] = s_description
        
        # Attribut titre : titre de l'annonce
        item['titre'] = sel.xpath('//h1[@itemprop="name"]/text()').extract()[0]
        
        # Attribut prix : prix d'annonce
        item['prix'] = sel.xpath('//span[@class="price"]/text()').extract()[0]
        
        # Renvoie l'objet ainsi cree
        return item    
