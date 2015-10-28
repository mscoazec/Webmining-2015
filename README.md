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

### Outils

Le shell permet de code interactivement, la doc est ici : http://doc.scrapy.org/en/latest/topics/shell.html. Et il s'exécuter avec 

                scrapy shell <url>

Une fois le shell ouvert, exécuter par exemple :

                from scrapy.selector import Selector
                sel = Selector(response)
                sel.xpath('//p')

pour visualiser tous les paragraphes de la page analysée.

### Architecture et implémentation

Le code est structuré pour l'implémentation de méthodes de fouille de données, développées pour l'extraction de classes d'objets particuliers : des produits, ici des biens immobiliers en vente.

Le fichier `items.py` contient la définition des classes des objets que l'on cherche à extraire. Il s'agit ici de la classe `Product`. Un objet de cette classe sera défini par les attributs suivants :

* `url` : l'adresse de l'annonce du bien immobilier en question,
* `titre` : le titre de l'annonce immobilière,
* `description` : la description du bien, c'est-à-dire le texte de l'annonce,
* `prix` :  le prix de vente sur l'annonce,
* `infos` : des informations additionnelles contenues dans des tableaux (notre convention est de les séparer par des virgules en les concaténant),
* `agence` : le nom de l'agence, si disponible,
* `localisation` : la localisation, si disponible,
* `metro` : la liste des stations de métro à proximitié (même convention avec la virgule comme séparateur), disponible uniquement pour le site d'annonces PAP.

Le fichier `spider.py` est dédié à l'implémentation des différents robots d'indexation, ou encore _spiders_, qui définissent la façon dont un site (ou un groupe de sites) est fouillé. En particulier, il s'agit de rédiger des règles (principe de sélection) permettant aux robots de cliquer sur les liens d'intérêt (ceux qui correspondent effectivement à une annonce immobilère et non pas à une publicité...) et de tourner les pages des résultats. Un objet de type `Product` est enfin extrait de chacune des annonces. Chaque robot est implémenté dans une classe `CrawlSpider`, identifié par un nom et dédié à une catégorie de sites particulière, puisque que les différents sites ont des architectures très variables. 

Pour résumer, les éléments importants à définir au sein d'une classe `CrawlSpider` sont les suivants. La liste :

        start_url

permet de déclarer les url par lesquelles commence la fouille. Ici ce sont les pages qui affichent les résultats de la recherche "ventes à Paris" : par exemple http://www.seloger.com/immobilier/achat/immo-paris-1er-75/. Des règles ultérieures de sélection sont définies par une `Rule`, ici il s'agit de tourner les pages de résultats. La méthode :

        parse_start_url

définit la façon dont ces pages sont analysées. Ici, l'on recherche sur la page http://www.seloger.com/immobilier/achat/immo-paris-1er-75/ les liens vers des url qui correspondent à une annonce : par exemple http://www.seloger.com/annonces/achat/appartement/paris-1er-75/palais-royal/103180129.htm?ci=750101&idqfix=1&idtt=2&tri=d_dt_crea&bd=Li_LienAnn_1. Enfin, sur chacun de ces pages, la méthode :

        parse_item

est exécutée. Elle définit la façon dont une page d'annonce est traitée, en extrayant les attributs d'un objet de la classe `Product`.

Suit la liste des classes de robots implémentés :

* `seLogerSpider` : fouille les ventes immobilères à Paris pour le site http://www.seloger.com/
* `explorimmoSpider` : idem pour http://www.explorimmo.com/
* `fnaimSpider` : idem pour http://www.fnaim.fr/
* `paruvenduSpider` : idem pour http://www.paruvendu.fr/
* `papSpider` : idem pour http://www.pap.fr/
* `laforetSpider` : idem pour http://www.laforet.com/

Le fichier `pipeline.py` permet de définir des routines de post-traitement : chaque objet de type `Product` extrait lors de la fouille est passé à la fonction `process_item`. Ce routine va en particulier effectuer la traduction des caractères du texte de ASCII vers Unicode, format mieux géré en Python. Il est à noter que cette conversion vers Unicode supprime les accents du texte.

Le fichier `settings.py` regroupe les valeurs de nos paramètres de fouille, en particulier le temps minimal séparant deux requêtes successives (les sites n'apprécient pas être surchargés par des requêtes automatiques...).

### Exécution

Elle se fait en ligne de commande. Par exemple, exécuter dans le dossier maître `web-crawling\code` la commande suivante :

    scrapy crawl seLogerSpider -o ..\output\filename.json

lance le robot d'indexation nommé `seLogerSpider`, défini dans `spiders.py`, qui fouille une partie du site http://www.seloger.com/, en sauvegardant les objets `Product` collectés dans le fichier en sortie `..\output\filename.json`.

### Format des données

Les données extraites lors de la fouille sont sauvegardées de façon dynamique dans un fichier, en utilisant le format objet `.json`. Dans l'exemple d'exécution donné à la section précédente, il s'agit du fichier `web-crawling\output\filename.json` ; remarquez que les fichiers en sortie ne sont jamais ecrasés : les nouvelles données sont concaténées en fin de fichier. Le format `.json` est flexible, chaque objet est sauvegardé avec le nom de ses attributs ; par ailleurs ce format est facilement convertible vers `.csv` ou `.xls`.

On adopte une convention de nommage avec la date de fouille.

### Remarques sur l'avancement

Problématiques :
* 12/10 : Certains champs de description incomplets sur seloger.com, qui terminent par "...", résolu en allant chercher sur la page l'intégralité du texte.
* 13/10 : Pour une recherche donnée, les sites affichent en général un nombre limité de résultats (750 résultats - ou encore les 100 premières pages de résultats i.e. environ 1700 résultats) :
    * cibler : au lieu de chercher toutes les ventes sur Paris, on effectue les recherches par arrondissement,
    * vérifier si ce filtre est suffisant pour accéder à tous les résultats.
* 15/10 : PAP a l'air de bien contrer les robots (ne pas se faire remarquer).
* 16/10 : exhaustivité des fonctions de type _parse_url_ et _parse_item_ ?

Points importants à aborder :
* _re-visiting_ ?

## 2. Text analysis

Le dossier Text analysis est dédié à l'analyse des textes d'annonces récupérés lors du web-crawling, pour en déduire les caractéristiques numériques des biens immobiliers décrits par les annonces.

### Entrées du module

Un ensemble de fichiers Json contenant, pour chaque annonce, les différents champs récupérés lors du crawling. Il doit y avoir obligatoirement le champ 'url'.

### Sortie du module

Un fichier .csv contenant une ligne par annonce immobilière traitée, et une colonne par feature, avec la valeur de chaque feature pour chaque bien immobilier. En cas de feature non trouvée dans le texte, la valeur de la feature est mise à zéro.

### Fichiers du dossier

Le fichier le plus important est le code python Traitement_annonces.py
Il est également indispensable d'avoir la liste des features en .csv : Liste_features.csv

Le dossier contient un sous-dossier avec les fichiers .json donnés par le web crawling.
Enfin il contient le fichier d'ouput : le .csv contenant les données d'apprentissage.

Les trois éléments : Traitement_annonces.py, Liste_features.csv, dossier de fichiers .json doivent être dans le même dossier lors de l'exécution du code.
Le fichier output est automatiquement créé au même endroit.

### Exécution du code

Le code s'exécute grâce à un environnement supportant le python. Pour l'instant le fichier Traitement_annonces.py comporte à la dernière ligne l'appel de la fonction traitant automatiquement tout un dossier contenant des fichiers Json. Il suffit de lui mettre comme argument le nom du dossier à traiter, puis de lancer l'exécution du programme Python.

### Contenu du fichier Traitement_annonces.py

#### Données globales :

tab_features : le tableau des features importé de Liste_features.csv
    L'import se fait en tout début de code, et la liste des features est donc conservée tout au long de l'exécution.      Ce tableau comprend les noms des features, si ce sont des features booléennes, et les chaînes de caractère à          rechercher dans les textes pour chacune des features.
    
feature_and_price_list : la liste simple des noms de features, avec le prix en dernière position.

num_dict : un dictionnaire permettant le passage de nombres écrits en toutes lettres en nombres écrits en chiffres.

#### Le code est ensuite divisé en sous-fonctions successives :

traitement_dossier : prend en entrée un dossier de fichiers Json, et sort un fichier .csv contenant toutes les données de toutes les annonces de tous les fichiers contenus dans le dossier.

traitement_fichier : prend en entrée un fichier Json, et sort un fichier .csv contenant toutes les données de toutes les annonces du fichier. Cette fonction peut prendre en entrée un fichier.csv où écrire les données (ceci pour pouvoir regrouper les données de plusieurs fichiers Json dans la fonction traitement_dossier).

traitement_annonce : prend en entrée une liste de string correspondant aux différents champs d'une annonce immobilière, comprenant obligatoirement le champ 'url', et sort une liste des valeurs de chaque feature.

extraction_features : prend en entrée un texte (string), et sort la liste des valeurs de chaque feature trouvée dans le texte (et 0 par défaut si une feature n'est pas mentionée dans le texte).

## 3. Machine learning

## 4. Modèle client serveur, design

Pour créer un serveur depuis votre ordinateur, placer le fichier "serveur.py" dans un nouveau répertoire. Les pages HTML fixes doivent se trouver dans le même dossier et les fichiers python que vous voudrez exécuter par la suite doivent se trouver dans un sous-répertoire "exec".

Avant tout de choses, il faut donner des droits supplémentaires à tous les fichiers pythons qui seront exécutés depuis le serveur. Pour cela, placez-vous dans le dossier contenant les fichiers (commande cd "...") puis utilisez la commande ( "chmod +x NomDuFichier.py"). Ensuite, vous pouvez simplement lancer le serveur en appelant "python serveur.py" dans le terminal de commandes.

Une fois cette opération réalisée, vous disposez d'un serveur local dont le port par défaut est 8000. Vous pouvez y accéder par l'URL http://localhost:8000. Les fichiers HMTL se trouvant dans le même répertoire que "serveur.py" peuvent être chargés simplement en rentrant l'URL suivante : http://localhost:8000/NoMduFichier.html. La syntaxe à adopter ne chnage pas par rapport à ce que nous avons vu  en cours sur ce langage.

Pour créer des pages interprétés par python, il faut utiliser un fichier .py que l'on peut charger par http://localhost:8000/exec/NomDuFichier.py. Pour que ce type de fichier affiche un code HMTL, il suffit d'utiliser la commande print en plaçant le code html sous format text. Par exemple :


hmtl =  """ <head>
        
                <body>
                
                MON TEXTE
                
                </body>
                
        </head>
""""

print (html) 


[les trois """ servent à indiquer que tout ce qui suit est à interpréter comme du texte]

La syntaxe des variables utilisées est la même que pour le PHP. Dans l'idée, la page attend un certain nombre de paramètres qui doivent être insérés dans l'URL après le symbole "?". Si vous créez un formulaire sur un fichier .html, l'utilisateur sera redirigée vers une nouvelle page, dont l'URL contiendra par exemple `?name=VALEUR&first_name=VALEUR`. Si vous laissez les champs vide, les valeurs par défaut seront None.

La commande a utiliser ensuite est `cgi.FieldStorage()`. Il s'agit d'une commande magique qui permet de récupérer toutes les variables présentes dans la page. Typiquement, on peut appeler les paramètres par la syntaxe :

`form = cgi.FieldStorage()`

`print(form["Name"].value)`

Vous pouvez bien-sur remplacer "Name" par tous les paramètres des formulaires que vous souhaitez. La syntaxe à respecter pour créer un formulaire est :

`<form action="exec/NomDuFichier.py" method="get">`

[...]

`<input type="number" class="form-control" name="NomDeLaVariable" placeholder="100">`

[...]
