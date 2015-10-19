from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

# Importer la classe de l'item par defaut
from project.items import Product

# Sauvegarde des explorations dans des fichiers texte
debug = 1

###############################################################################
# -- to do
# * crawler d'autres sites
# * gestion des items doublons
# * eviter les redondances du code qui suit !
###############################################################################

###############################################################################
# Definition de la classe CrawlSpider pour seloger.com
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
        
        for el in zone_description:
            item['description'] += el
        
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
# Definition de la classe CrawlSpider pour explorimmo.com
###############################################################################

class explorimmoSpider(CrawlSpider):
    
    name = "explorimmoSpider"
    allowed_domains = ["explorimmo.com"]
    
    # Url par lesquelles commence la fouille
    
    start_urls = []
    
    for i in range(1,10):
        
        start_urls.append("http://www.explorimmo.com/"
        +"immobilier-vente-bien-paris+7500"+str(i)+".html")
        
        for n_page in range(1,30):
            start_urls.append("http://www.explorimmo.com/"+
            "immobilier-vente-bien-paris+7500"+str(i)+"-"+str(n_page)+".html")
    
    for i in range(10,21):
        
        start_urls.append("http://www.explorimmo.com/"+
        "immobilier-vente-bien-paris+750"+str(i)+".html")
        
        for n_page in range(1,30):
            start_urls.append("http://www.explorimmo.com/"+
            "immobilier-vente-bien-paris+7500"+str(i)+"-"+str(n_page)+".html")
    
    # Ouverture de toutes les annonces
    
    def parse_start_url(self, response):
        
        if debug:
            f = open('debug_crawling_explorimmo.txt', 'a')
            f.write(response.url+'\n')
        
        sel = Selector(response)
        sites = sel.xpath('//div[@class="bloc-item  js-bloc-vue "]'+
		'/div[@class="bloc-item-header"]/h2[@itemprop="name"]')

        for site in sites:
        
            zone_url = site.xpath('a/@href').extract()
            
            if zone_url:
                s_url = 'http://www.explorimmo.com' + zone_url[0]
                yield Request(s_url, callback = self.parse_item)
            
        if debug:
            f.close()
    
    # Analyse des annonces
    
    def parse_item(self, response):

        sel = Selector(response)
        item = Product()
        
        # Attribut url
        
        item['url'] = response.url
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//div[@itemprop="description"]'+
        '/p/text()').extract()
        
        for el in zone_description:
            item['description'] += el

        # Attribut infos

        item['infos'] = ''
        zone_items = sel.xpath('//div[@class="features clearfix"]/ul/li')
        
        for li in zone_items:
            zone_item_name = li.xpath('span[@class="name"]/text()').extract()
            zone_item_value = li.xpath('span[@class="value"]/text()').extract()
            
            if zone_item_name and zone_item_value:
                s_li = zone_item_name[0] + ' : ' + zone_item_value[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
        
        zone_oth_items = sel.xpath('//div[@class="energy-consumption"]/ul/li')
        
        for li in zone_oth_items:
            zone_item_name = li.xpath('text()').extract()
            zone_item_value = li.xpath('span/text()').extract()
            
            if zone_item_name and zone_item_value:
                s_li = zone_item_name[0] + ' : ' + zone_item_value[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
               
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-1]

        # Attribut titre

        item['titre'] = ''
        zone_titre = sel.xpath('//h1[@itemprop="name"]/text()').extract()
        
        if zone_titre:
            item['titre'] = zone_titre[0]
            
        # Attribut agence
            
        item['agence'] = ''
        zone_agence = sel.xpath('//p[@class="agency-name"]/text()').extract()
        
        if zone_agence:
            item['agence'] = zone_agence[0]
        
        # Attribut localisation
        
        item['localisation'] = ''
        zone_loc = sel.xpath('//span[@class="informations-localisation"]'+
        '/text()').extract()
        
        if zone_loc:
            item['localisation'] = zone_loc[0]
		
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
        "immobilier/vente/appartement/paris-750"+str(i)+"/")

    for i in range(1,10):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/maison/paris-7500"+str(i)+"/")

    for i in range(10,21):
        start_urls.append("http://www.paruvendu.fr/"+
        "immobilier/vente/maison/paris-750"+str(i)+"/")
        
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
            yield Request(s_url, callback = self.parse_item)
    
        if debug:
            f.close()
    
    # Analyse des annonces

    def parse_item(self, response):

        sel = Selector(response)        
        item = Product()
        
        # Attribut url
        
        item['url'] = response.url
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//div'+
        '[@class="im12_txt_ann im12_txt_ann_auto"]')
        
        # traiter les cas : paruvendu.fr/n/programme-neuf/appartements-neufs
        if not zone_description:
            zone_description = sel.xpath('//div[@class="detailneuf_'+
            'txtjustif"]/p')
        
        if zone_description:
            
            for el in zone_description.xpath('text()'):
                
                if el.extract():
                    item['description'] = item['description'] + el.extract()
            
        # Attribut infos

        item['infos'] = ''
        zone_items = sel.xpath('//ul[@class="imdet15-infoscles"]/li')
        
        for li in zone_items:
            zone_item_name = li.xpath('strong/text()').extract()
            zone_item_value = li.xpath('text()').extract()
            
            if zone_item_name:
                s_li = zone_item_name[0]
                
                if len(zone_item_value)>1:
                     s_li = s_li + zone_item_value[1]
                     
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
                    
        zone_oth_items = sel.xpath('//dl[@class="im11_col_enr"]/dd')
        
        for el in zone_oth_items:
            zone_item = el.xpath('text()').extract()
            
            if zone_item:
                s_li = zone_item[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
        
        zone_oth_items = sel.xpath('//div[@class="DPE_effSerreTxt"]')
        
        for el in zone_oth_items:
            zone_item_name = el.xpath('text()').extract()
            zone_item_value = el.xpath('span/text()').extract()
            
            if zone_item_name and zone_item_value:
                s_li = zone_item_name[0] + ' : ' + zone_item_value[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
            
        zone_oth_items = sel.xpath('//div[@class="DPE_consEnerTxt"]')
        
        for el in zone_oth_items:
            zone_item_name = el.xpath('text()').extract()
            zone_item_value = el.xpath('span/text()').extract()
            
            if zone_item_name and zone_item_value:
                s_li = zone_item_name[0] + ' : ' + zone_item_value[0]
                s_li = s_li.strip()
                
                if s_li:
                    item['infos'] = item['infos'].strip() + ' ' + s_li + ','
               
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-1]
        
        # Attribut titre

        item['titre'] = ''
        zone_titre = sel.xpath('//h1[@class="im12_hd im12immo_hd"]')
        
        # traiter quelques cas
        if not zone_titre:
            zone_titre = sel.xpath('//div[@class="im12_hd im12immo_hd"]'+
            '/div[@class="im12_hd im12immo_hd"]')
        
        # traiter les cas : paruvendu.fr/n/programme-neuf/appartements-neufs
        if not zone_titre:
            zone_titre = sel.xpath('//div[@class="im12_hd im12immo_hd"]/h1')
        
        if zone_titre:
            
            for el in zone_titre:
                    
                zone_1 = el.xpath('span/text()').extract()
                zone_2 = el.xpath('strong/text()').extract()
                zone_3 = el.xpath('text()').extract()
                
                if zone_1:
                    item['titre'] += zone_1[0]
                if zone_2:
                    item['titre'] += zone_2[0]
                if len(zone_3) > 2:
                    item['titre'] += zone_3[2]
                
        # Attribut agence
            
        item['agence'] = ''
        zone_agence = sel.xpath('//p[@class="parttel_coordagence"]'+
        '/strong/text()').extract()
        
        # traiter les cas : paruvendu.fr/n/programme-neuf/appartements-neufs
        if not zone_agence:
            zone_agence = sel.xpath('//div[@class="dhead14-contactvend"]'+
            '/strong')
        
        if zone_agence:
            item['agence'] += zone_agence[0]
            
        zone_particulier = sel.xpath('//div[@class="flol contact_infospart"]'+
        '/text()').extract()
        
        if zone_particulier:
            item['agence'] += zone_particulier[0]
        
        # Attribut localisation
        
        item['localisation'] = ''
        zone_loc = sel.xpath('//span[@class="auto2010_detTophead1Txt3"]'+
        '/text()').extract()
        
        # traiter les cas : paruvendu.fr/n/programme-neuf/appartements-neufs
        if not zone_loc:
            zone_loc = sel.xpath('//div[@class="im12_txt_ann"]/p/strong'+
        '/text()').extract()
        
        if zone_loc:
            item['localisation'] += zone_loc[0]
		
        # Attribut prix
  
        item['prix'] = ''
        zone_prix = sel.xpath('//div[@id="autoprix"]/text()').extract()
        
        if zone_prix:
            item['prix'] += zone_prix[0]

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
    
    for i in range(1,10):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-maison-paris-"+
        str(i)+"e-arrondissement-7500"+str(i)+".htm")

    for i in range(10,21):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-maison-paris-"+
        str(i)+"e-arrondissement-750"+str(i)+".htm")
    
    for i in range(1,10):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-parking-paris-"+
        str(i)+"e-arrondissement-7500"+str(i)+".htm")

    for i in range(10,21):
        start_urls.append("http://www.fnaim.fr/"+
        "liste-annonces-immobilieres/17-acheter-parking-paris-"+
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
            yield Request(s_url, callback = self.parse_item)
        
        if debug:
            f.close()
    
    # Analyse des annonces
    
    def parse_item(self, response):

        sel = Selector(response)
        item = Product()
        item['url'] = response.url
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//p[@itemprop="description"]'+
        '/text()').extract()
        
        for el in zone_description:
            item['description'] += el
        
        # Attribut infos
        
        item['infos'] = ''
        
        zone_items = sel.xpath('//div[@class="contentOnglet"]/ul/li/ul/li')
            
        for li in zone_items:
            zone_item_name = li.xpath('label/text()').extract()
            zone_item_value = li.xpath('text()').extract()
            
            if zone_item_name:
                item['infos'] += zone_item_name[0].strip() + ' '
                
                for val in zone_item_value:
                    item['infos'] += val.strip()
                    
                item['infos'] += ', '
                    
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-2]
        
        zone_ot_items = sel.xpath('//div[@class="dpeValue"]/text()').extract()
        
        if zone_ot_items:
            item['infos'] += ', Consommation energetique : '
            item['infos'] += zone_ot_items[0] + ' Kwh/m2/an'
        
        # Attribut localisation
        
        item['localisation'] = ''
        zone_loc = sel.xpath('//div[@itemprop="address"]/p/text()').extract()
        
        if zone_loc:
            item['localisation'] += zone_loc[0]
        
        # Attribut titre
        
        item['titre'] = ''
        zone_titre = sel.xpath('//h2[@itemprop="name"]/text()').extract()
            
        if zone_titre:
            item['titre'] += zone_titre[0]
            
        # Attribut agence
            
        item['agence'] = ''
        zone_agence = sel.xpath('//p[@class="voirSite"]/span/text()').extract()
        
        zone_adr = sel.xpath('//div[@itemprop="address"]' +
        '/meta[@itemprop="streetAddress"]/@content').extract()
        
        if zone_agence:
            
            for el in zone_agence:
                item['agence'] += el
            
            if zone_adr:
                item['agence'] += ', ' + zone_adr[0]
        
        # Attribut prix
        
        item['prix'] = ''
        zone_prix =  sel.xpath('//span[@itemprop="price"]/text()').extract()
        
        if zone_prix:
            item['prix'] = zone_prix[0]
        
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
        Rule(SgmlLinkExtractor(allow=(),
                               restrict_xpaths=('//li[@class="next"]/a',)),
                               callback="parse_start_url",
                               follow= True),
    )

    # Ouverture de toutes les annonces

    def parse_start_url(self, response):

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
      
        sel = Selector(response)
        item = Product()
        
        # Attribut url
        
        item['url'] = response.url
        
        # Attribut titre
        
        item['titre'] = ''
        zone_titre = sel.xpath('//span[@class="title"]/text()').extract()
        
        if zone_titre:
            item['titre'] += zone_titre[0]
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//div[@class="text-annonce-container"]'+
        '/p/text()').extract()
        
        for el in zone_description:
            item['description'] += el
            
        # Attribut localisation
        
        item['localisation'] = ''
        zone_description = sel.xpath('//div[@class="text-annonce-container"]'+
        '/h2/text()').extract()
        
        for el in zone_description:
            item['localisation'] += el
            
        # Attribut metro
            
        item['metro'] = ''
        zone_metro = sel.xpath('//div[@class="metro"]/ul/li')
        
        for el in zone_metro:
            station_name = el.xpath('span/text()').extract()
            
            if station_name:
                item['metro'] += station_name[0] + ', '
        
        # enleve la derniere virgule
        item['metro'] = item['metro'][:-2]
                
        # Attribut infos
        
        item['infos'] = ''
        zone_items = sel.xpath('//div[@class="footer-descriptif clearfix"]'+
        '/ul/li')
        
        for el in zone_items:
            zone_item_name = el.xpath('span/text()').extract()
            zone_item_value = el.xpath('text()').extract()
            
            if zone_item_name:
                    item['infos'] += zone_item_name[0].strip() + ' : '
                    
                    for val in zone_item_value:
                        item['infos'] += val.strip()
                        
                    item['infos'] += ', '
                    
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-2]
        
        # Attribut prix : prix d'annonce
        
        item['prix'] = ''
        zone_prix = sel.xpath('//span[@class="prix"]/strong/text()').extract()
        
        if zone_prix:
            item['prix'] += zone_prix[0]
        
        return item
    
###############################################################################
# Definition de la classe Spider pour le site laforet.com
###############################################################################

class laforetSpider(CrawlSpider):
    
    name = "laforetSpider"
    allowed_domains = ["laforet.com"]
    
    # Url par laquelle commence la fouille
    
    start_urls = []

    for i in range(1,10):
        start_urls.append("http://immobilier.laforet.com/"+
        "annonce-achat_paris-0"+str(i)+".html")
        
    for i in range(10,21):
        start_urls.append("http://immobilier.laforet.com/"+
        "annonce-achat_paris-"+str(i)+".html")
    
    # La regle de fouille consiste a tourner les pages
    rules = (
        Rule(SgmlLinkExtractor(allow=(),
                            restrict_xpaths=('//a[@title="Page suivante"]',)),
                            callback="parse_start_url",
                            follow=True),
    )

    # Ouverture de toutes les annonces

    def parse_start_url(self, response):

        if debug:
            f = open('debug_crawling_laforet.txt', 'a')
            f.write(response.url+'\n')

        sel = Selector(response)
        sites = sel.xpath('//div[@class="annonce_contentbis"]')
        
        for site in sites:
            s_url = site.xpath('a/@href').extract()[0]
            yield Request(s_url, callback = self.parse_item)
            
        if debug:
            f.close()
    
    # Analyse des annonces
    
    def parse_item(self, response):
      
        sel = Selector(response)
        item = Product()
        
        # Attribut url
        
        item['url'] = response.url
        
        # Attribut titre
        
        item['titre'] = ''
        zone_titre = sel.xpath('//h1[@class="page-header"]/text()').extract()
        
        if zone_titre:
            item['titre'] += zone_titre[0]
        
        # Attribut description
        
        item['description'] = ''
        zone_description = sel.xpath('//div[@class="description-detail"]'+
        '/h2/text()').extract()
        
        for el in zone_description:
            item['description'] += el
        
        zone_description = sel.xpath('//div[@class="description-detail"]'+
        '/p/text()').extract()
        
        for el in zone_description:
            item['description'] += el
                
        # Attribut infos
        
        item['infos'] = ''
        zone_items = sel.xpath('//div[@class="caracteristiques-detail"]'+
        '/ul/li')
        
        for el in zone_items:
            zone_item_name = el.xpath('span[@class="detail-title"]'+
            '/text()').extract()
            zone_item_value = el.xpath('span[@class="detail-description"]'+
            '/text()').extract()
            
            if zone_item_name and zone_item_value:
                
                    value = ''
                    for val in zone_item_value:
                        value += val.strip()
                        
                    if value and not value == '-':
                        item['infos'] += zone_item_name[0].strip() + ' : '
                        item['infos'] += value + ', '
                    
        # enleve la derniere virgule
        item['infos'] = item['infos'][:-2]
        
        zone_o_items = sel.xpath('//span[@class="dpe-value"]/text()').extract()
        
        if zone_o_items:
            item['infos'] += ', Consommation energetique : '
            item['infos'] += zone_o_items[0] + ' Kwh/m2/an'
            
        # Attribut prix
            
        # a priori pas d'autre methode que d'aller le chercher dans le titre
        item['prix'] = item['titre'].split('-')[-1]
        
        return item