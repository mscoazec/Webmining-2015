import unicodedata

class FilterPipeline(object):
    """A pipeline for filtering out items which contain certain words in their
    description"""

    # put all words in lowercase

    def process_item(self, item, spider):
        item['prix'] = item['prix'].replace(u"\u00A0", "")
        item['prix'] = item['prix'].replace(u"\u20ac", "")
        item['prix'] = item['prix'].strip()
        item['url'] = item['url'].replace(u"\u00A0", "")
        # suppression des espaces multiples
        item['description'] = ' '.join(item['description'].split())
        item['description'] = unicodedata.normalize('NFKD',item['description']).encode('ascii','ignore')
        item['titre'] = ' '.join(item['titre'].split())
        item['titre'] = unicodedata.normalize('NFKD',item['titre']).encode('ascii','ignore')
        item['infos'] = ' '.join(item['infos'].split())
        item['infos'] = unicodedata.normalize('NFKD',item['infos']).encode('ascii','ignore')
        return item
