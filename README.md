# PESTO Webmining 2015
Code et fichiers du projet 2015 du PESTO Webmining.

#### Please
* Essayez de décrire ce que vous faites lors des _commits_ pour pouvoir revenir à une version ancienne du projet plus facilement.
* Contribuez au `README.md` en expliquant comment exécuter vos codes.

Thxs !

## 1. Web crawling

Le dossier `web-crawling` est dédié à l'implémentation d'un projet de fouille de données `Scrapy` pour `Python`, dont l'objet est de récupérer

* le prix de vente
* la description
* les caractéristiques éventuelles

des biens immobiliers présentés sur les principaux sites d'annonces.

La documentation de l'environnement utilisé est disponible à http://doc.scrapy.org/. L'architecture du code, qui est dans `web-crawling\code`, s'inspire de l'exemple du tutoriel et est détaillée plus loin. Les données extraites lors de la fouille sont quant à elles sauvegardées dans des fichiers au format `.json`, que l'on a choisi de stocker dans un dossier à part, nommé `web-crawling\output`.

### Architecture et implémentation

Le code est structuré pour l'implémentation de méthodes de fouille de données, développées pour l'extraction de classes d'objets particuliers : des produits, ici des biens immobiliers en vente.

Le fichier `items.py` contient la définition des classes des objets que l'on cherche à extraire. Il s'agit ici de la classe `Product`. Un objet de cette classe sera défini par les attributs suivants :

* `url` : l'adresse de l'annonce du bien immobilier en question,
* `titre` : le titre de l'annonce immobilière,
* `description` : la description du bien, c'est-à-dire le texte de l'annonce,
* `prix` :  le prix de vente sur l'annonce.

Le fichier `spider.py` est dédié à l'implémentation des différents robots d'indexation, ou encore _spiders_, qui définissent la façon dont un site (ou un groupe de sites) est fouillé. En particulier, il s'agit de rédiger des règles permettant aux robots de cliquer sur les liens d'intérêt (ceux qui correspondent effectivement à une annonce immobilère et non pas à une publicité...) et de tourner les pages des résultats. Un objet de type `Product` est enfin extrait de chacune des annonces. Chaque robot est implémenté dans une classe, identifié par un nom et dédié à une catégorie de sites particulière (parce que les différents sites ont des architectures très variables). Suit la liste des robots implémentés :

* `seLogerSpider` : fouille les ventes immobilères à Paris pour le site http://www.seloger.com/
* `explorimmoSpider` : idem pour http://www.explorimmo.com/

Le fichier `pipeline.py` permet de définir des routines de post-traitement : chaque objet de type `Product` extrait lors de la fouille est passé à la fonction `process_item`. Ce routine va en particulier effectuer la traduction des caractères du texte de ASCII vers Unicode, format mieux géré en Python. Il est à noter que cette conversion vers Unicode supprime les accents du texte.

### Exécution

Elle se fait en ligne de commande. Par exemple, exécuter dans le dossier maître `web-crawling\code` la commande suivante :

    scrapy crawl seLogerSpider -o ..\output\filename.json

lance le robot d'indexation nommé `seLogerSpider`, défini dans `spiders.py`, qui fouille une partie du site http://www.seloger.com/, en sauvegardant les objets `Product` collectés dans le fichier en sortie `..\output\filename.json`.

### Format des données

Les données extraites lors de la fouille sont sauvegardées de façon dynamique dans un fichier, en utilisant le format objet `.json`. Dans l'exemple d'exécution donné à la section précédente, il s'agit du fichier `web-crawling\output\filename.json` ; remarquez que les fichiers en sortie ne sont jamais ecrasés : les nouvelles données sont concaténées en fin de fichier. Le format `.json` est flexible, chaque objet est sauvegardé avec le nom de ses attributs ; par ailleurs ce format est facilement convertible vers `.csv` ou `.xls`.

## 2. Text analysis

## 3. Machine learning

## 4. Modèle client serveur, design
