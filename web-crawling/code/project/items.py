from scrapy.item import Item, Field
    
class Product(Item):
    url = Field()
    titre = Field()
    prix = Field()
    description = Field()
    infos = Field()