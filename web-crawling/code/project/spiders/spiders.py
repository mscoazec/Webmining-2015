from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
import time

# Importer la classe de l'item par defaut
from project.items import Product

# Sauvegarde des explorations dans des fichiers texte
debug = 1
delay = 0.2

###############################################################################
# Definition de la classe Spider pour le site seLoger
###############################################################################

class seLogerSpider(CrawlSpider):
	
    # Nom du robot d'indexation
    name = "seLogerSpider"
    
    # Domaine autorise lors de la fouille
    allowed_domains = ["seloger.com"]
    
    # Url par lesquelles commence la fouille

    start_urls = ["http://www.seloger.com/"+
    "immobilier/achat/immo-paris-1er-75/"]

    for i in range(2,21):
        start_urls.append("http://www.seloger.com/"+
        "immobilier/achat/immo-paris-"+str(i)+"eme-75/")
    
    # La regle de fouille consiste a tourner les pages

    rules = (
        Rule(SgmlLinkExtractor(allow=(),
             restrict_xpaths=('//a[@class="pagination_next active"]',)),
             callback="parse_start_url",
             follow=True),
    )
    
    # Ouverture de toutes les annonces :
 
    # Sur chaque page fouillee, on obtenient les url des pages qui
    # correspondent a des biens immobiliers, sur chacune desquelles le 
    # callback |parse_item| s'execute.

    def parse_start_url(self, response):
        
        # ecriture des url explorees dans un fichier texte
        if debug:
            f = open('debug_crawling_seloger.txt', 'a')
            f.write(response.url+'\n')

        # Selection des url des annonces

        sel = Selector(response)
        sites = sel.xpath('//div[@class="price "]')

        for site in sites:
            
            zone_url = site.xpath('a/@href').extract()
            
            if zone_url:
                s_url = zone_url[0]
                # execute le callback |parse_item| sur chaque annonce
                yield Request(s_url, callback = self.parse_item)
        
        # ferme le fichier d'ecriture du debug
        if debug:
            f.close()
    
    # Analyse des annonces :
    
    # Pour chaque page (bien immobilier), |parse_item| permet d'obtenir les 
    # details de l'annonce : url de la page, prix, texte de l'annonce ..., qui
    # vont nous servir pour l'extraction des caracteristiques du bien
    # immobilier.

    def parse_item(self, response):
        
        # attendre un peu pour ne pas se faire blacklister
        time.sleep(delay)
        
        sel = Selector(response)
        
        # Le bien immobilier pour la page analysee est decrit par un objet
        # de type |Product()|, dont les attributs sont declares dans le fichier
        # |items.py|.

        item = Product()
        
        # Attribut url : url de la page analysee

        item['url'] = response.url
        
        # Attribut description : texte de l'annonce

        item['description'] = ''
        zone_description = sel.xpath('//p[@class="description"]'+
        '/text()').extract()
        
        if zone_description:
            item['description'] = zone_description[0]
        
        # Attribut infos : infos du tableau

        item['infos'] = ''
        zone_items = sel.xpath('//ol[@class="description-liste"]/li')
        
        for li in zone_items:
            zone_item = li.xpath('@title').extract()
            
            if zone_item:
                s_li = zone_item[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
               
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-1]
        
        # Attribut titre : titre de l'annonce

        item['titre'] = ''
        zone_titre = sel.xpath('//h1[@class="detail-title"]/text()').extract()
        
        if zone_titre:
            item['titre'] = zone_titre[0]
        
        # Attribut prix : prix d'annonce

        item['prix'] = ''
        zone_prix = sel.xpath('//span[@id="price"]/text()').extract()
        
        if zone_prix:
            item['prix'] = zone_prix[0]
        
        # renvoie l'objet ainsi cree
        return item

###############################################################################
# Definition de la classe Spider pour le site explorimmo
###############################################################################

class explorimmoSpider(CrawlSpider):
    
    name = "explorimmoSpider"
    allowed_domains = ["explorimmo.com"]
    
    # Url par lesquelles commence la fouille
    
    start_urls = []
    
    for i in range(1,10):
        
        start_urls.append("http://www.explorimmo.com/"
        +"immobilier-vente-bien-paris+7500"+str(i)+".html")
        
        for n_page in range(1,100):
            start_urls.append("http://www.explorimmo.com/"+
            "immobilier-vente-bien-paris+7500"+str(i)+"-"+str(n_page)+".html")
    
    for i in range(10,21):
        
        start_urls.append("http://www.explorimmo.com/"+
        "immobilier-vente-bien-paris+750"+str(i)+".html")
        
        for n_page in range(1,100):
            start_urls.append("http://www.explorimmo.com/"+
            "immobilier-vente-bien-paris+7500"+str(i)+"-"+str(n_page)+".html")
    
    # Ouverture de toutes les annonces
    
    def parse_start_url(self, response):
        
        if debug:
            f = open('debug_crawling_explorimmo.txt', 'a')
            f.write(response.url+'\n')
        
        sel = Selector(response)
        sites = sel.xpath('//h2[@itemprop="name"]')

        for site in sites:
        
            zone_url = site.xpath('a/@href').extract()
            
            if zone_url:
                s_url = 'http://www.explorimmo.com' + zone_url[0]
            
                if debug:
                    f.write(s_url+'\n')
                
                yield Request(s_url, callback = self.parse_item)
            
        if debug:
            f.close()
    
    # Analyse des annonces
    
    def parse_item(self, response):
        
        time.sleep(delay)
        sel = Selector(response)
        item = Product()
        item['url'] = response.url
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//div[@itemprop="description"]'+
        '/p/text()').extract()
        
        if zone_description:
            item['description'] = zone_description[0]

        # Attribut infos

        item['infos'] = 'infos'

        # Attribut titre
        item['titre'] = ''
        zone_titre = sel.xpath('//h1[@itemprop="name"]/text()').extract()
        
        if zone_titre:
            item['titre'] = zone_titre[0]
		
        # Attribut prix
        item['prix'] = ''
        zone_prix = sel.xpath('//span[@class="price"]/text()').extract()
        
        if zone_prix:
            item['prix'] = zone_prix[0]

        return item

###############################################################################
# Definition de la classe Spider pour le site paruvendu
###############################################################################

class paruvenduSpider(CrawlSpider):
    
    name = "paruvenduSpider"
    allowed_domains = ["paruvendu.fr"]
    
    # Url par lesquelles commence la fouille
    
    start_urls = []

    for i in range(1,10):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/appartement/paris-7500"+str(i)+"/")

    for i in range(10,21):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/appartement/paris-7500"+str(i)+"/")

    for i in range(1,10):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/maison/paris-7500"+str(i)+"/")

    for i in range(10,21):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/maison/paris-7500"+str(i)+"/")
        
    # La regle de fouille consiste a tourner les pages
  
    rules = (
        Rule(SgmlLinkExtractor(allow=(),
             restrict_xpaths=('//a[@class="next_13"]',)),
             callback="parse_start_url", follow=True),
    )
    
    # Ouverture de toutes les annonces
    
    def parse_start_url(self, response):
        
        if debug:
            f = open('debug_crawling_paruvendu.txt', 'a')
            f.write(response.url+'\n')
        
        sel = Selector(response)
        sites = sel.xpath('//div[@class="lazyload_bloc annonce"]')

        for site in sites:
            s_url = site.xpath('a/@href').extract()[0]
            s_url = 'http://www.paruvendu.fr' + s_url
            
            if debug:
                f.write(s_url+'\n')
                
            yield Request(s_url, callback = self.parse_item)
    
        if debug:
            f.close()
    
    # Analyse des annonces

    def parse_item(self, response):
        
        time.sleep(delay)
        sel = Selector(response)        
        item = Product()
        item['url'] = response.url
        
        # Attribut description

        s_description = ''
        
        if sel.xpath('//div[@class="im12_txt_ann im12_txt_ann_auto"]'+
        '/text()').extract():
            
            s_description = sel.xpath('//div'+
            '[@class="im12_txt_ann im12_txt_ann_auto"]/text()').extract()[0]
            
        item['description'] = s_description
        
        # Attribut info

        item['infos'] = 'infos'
        
        # Attribut titre

        item['titre'] = sel.xpath('//h1[@class="im12_hd im12immo_hd"]'+
        '/text()').extract()[0]
        
        # Attribut prix

        item['prix'] = sel.xpath('//div[@id="autoprix"]/text()').extract()[0]

        return item

###############################################################################
# Definition de la classe Spider pour le site FNAIM
###############################################################################

class fnaimSpider(CrawlSpider):
    
    name = "fnaimSpider"
    allowed_domains = ["fnaim.fr"]
    
    # Url par laquelle commence la fouille
    start_urls = []
    for i in range(1,10):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-appartement-paris-"+
        str(i)+"e-arrondissement-7500"+str(i)+".htm")
    for i in range(10,21):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-appartement-paris-"+
        str(i)+"e-arrondissement-750"+str(i)+".htm")
    
    # La regle de fouille consiste a tourner les pages
    rules = (
        Rule(SgmlLinkExtractor(allow=(),
                               restrict_xpaths=('//a[@class="next"]',)),
                               callback="parse_start_url",
                               follow=True),
    )

    # Ouverture de toutes les annonces
    def parse_start_url(self, response):
        
        if debug:
            f = open('debug_crawling_fnaim.txt', 'a')
            f.write(response.url+'\n')
        
        sel = Selector(response)
        sites = sel.xpath('//div[@class="itemContent"]/h3')

        for site in sites:
            s_url = "http://www.fnaim.fr" + site.xpath('a/@href').extract()[0]
            
            if debug:
                f.write(s_url+'\n')
            
            yield Request(s_url, callback = self.parse_item)
        
        if debug:
            f.close()
    
    # Analyse des annonces
    def parse_item(self, response):
        
        sel = Selector(response)
        item = Product()
        item['url'] = response.url
        
        # Attribut description
        s_description = ''
        if sel.xpath('//p[@itemprop="description"]/text()').extract():
            s_description = sel.xpath('//p[@itemprop="description"]'+
            '/text()').extract()[0]
        item['description'] = s_description
        
        # Attribut infos
        item['infos'] = 'infos'
        
        # Attribut titre
        if sel.xpath('//h2[@itemprop="name"]/text()').extract():
            item['titre'] = sel.xpath('//h2[@itemprop="name"]'+
            '/text()').extract()[0]
        
        # Attribut prix
        item['prix'] = sel.xpath('//span[@itemprop="price"]'+
        '/text()').extract()[0]
        
        return item
        
###############################################################################
# Definition de la classe Spider pour le site PAP
###############################################################################

class papSpider(CrawlSpider):
    
    name = "papSpider"
    allowed_domains = ["pap.fr"]
    
    # Url par lesquelles commence la fouille
    start_urls = [
        "http://www.pap.fr/annonce/vente-appartement-maison-paris-75-g439",
    ]
    
    # La regle de fouille consiste a tourner les pages
    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//li[@class="next"]/a',)), callback="parse_start_url", follow= True),
    )

    # Ouverture de toutes les annonces
    def parse_start_url(self, response):
        
        time.sleep(0.1)
        
        if debug:
            f = open('debug_crawling_pap.txt', 'a')
            f.write(response.url+'\n')

        sel = Selector(response)
        sites = sel.xpath('//div[@class="vignette-annonce"]')
        
        for site in sites:
            s_url = response.url + site.xpath('a/@href').extract()[0]
            yield Request(s_url, callback = self.parse_item)
            
        if debug:
            f.close()
    
    # Analyse des annonces
    def parse_item(self, response):
        
        time.sleep(0.2)
        
        sel = Selector(response)
        item = Product()
        
        # Attribut url : url de la page analysee
        item['url'] = response.url
        
        item['description'] = ''
        item['infos'] = ''
        
        # Cherche la description sur la page : texte de l'annonce
        
#        if sel.xpath('//div[@class="test-annonce-container"]/text()').extract():
#            s_description = sel.xpath('//div[@class="test-annonce-container"]/p/text()').extract()[0]
#        
#        # Cherche la description contenue dans le tableau : infos
#        # additionnelles, separees par des sauts de ligne
#        
#        li_items = sel.xpath('//div[@class="footer-descriptif clearfix"]/ul/li')
#        s_description_liste = '';
#        
#        for li in li_items:
#            s_li = li.xpath('/text()').extract()[0]
#            # supprime les espaces en fin de string
#            s_li = s_li.strip()
#            # concatene la string extraite apres une virgule seulement si elle
#            # est non vide
#            if s_li:
#                s_description_liste = s_description_liste.strip() + ' ' + s_li + ','
#               
#        # enlever la derniere virgule
#        s_description_liste = s_description_liste[:-1]
#        
#        # Attributs description et infos : le texte de l'annonce et les infos
#        # aditionnelles
#        item['description'] = s_description
#        item['infos'] = s_description_liste
        
        # Attribut titre : titre de l'annonce
        item['titre'] = sel.xpath('//span[@class="title"]/text()').extract()[0]
        
        # Attribut prix : prix d'annonce
        item['prix'] = sel.xpath('//span[@class="prix"]/strong/text()').extract()[0]
        
        # Renvoie l'objet ainsi cree
        return item