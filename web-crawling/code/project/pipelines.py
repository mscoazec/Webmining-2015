import unicodedata

class FilterPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase

    def process_item(self, item, spider):
        
        if isinstance(item['prix'], unicode):
            item['prix'] = item['prix'].replace(u"\u00A0", "")
            item['prix'] = item['prix'].replace(u"\u20ac", "")
            item['prix'] = item['prix'].strip()
            
        if isinstance(item['url'], unicode):
            item['url'] = item['url'].replace(u"\u00A0", "")
        
        for champs in ['description', 'titre', 'infos']:
            # suppression des espaces multiples
            item[champs] = ' '.join(item[champs].split())
            #unicode
            if isinstance(item[champs], unicode):
                item[champs] = unicodedata.normalize('NFKD',item[champs]).encode('ascii','ignore')
            
        return item
