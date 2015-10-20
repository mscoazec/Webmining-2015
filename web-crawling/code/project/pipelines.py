import unicodedata
from scrapy import signals
from scrapy.exceptions import DropItem

# nettoyage des chaines de caractere

class FilterPipeline(object):

    def process_item(self, item, spider):
        
        if 'prix' in item:
            # suppression des points
            item['prix'] = ''.join(item['prix'].split("."))
            # suppression des espaces
            item['prix'] = item['prix'].strip()
            item['prix'] = ''.join(item['prix'].split())
            # traitement des caracteres unicode
            if isinstance(item['prix'], unicode):
                item['prix'] = item['prix'].replace(u"\u00A0", "")
                item['prix'] = item['prix'].replace(u"\u20ac", "")
                
        if 'url' in item:
            if isinstance(item['url'], unicode):
                item['url'] = item['url'].replace(u"\u00A0", "")
        
        for champs in ['description', 'titre', 'metro',
                       'infos', 'localisation', 'agence']:
            if champs in item:
                # suppression des espaces multiples
                item[champs] = ' '.join(item[champs].split())
                #unicode
                if isinstance(item[champs], unicode):
                    item[champs] = unicodedata.normalize('NFKD',
                                   item[champs]).encode('ascii','ignore')
            
        return item

# gestion des doublons

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['url'])
            return item