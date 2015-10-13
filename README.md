# Webmining-2015
Code et fichiers du projet webmining 2015.

* Essayez de décrire ce que vous faites lors des commits pour pouvoir revenir à une version ancienne du projet plus facilement.
* Contribuez au README en expliquant comment exécuter vos codes.


## Web crawling

Le dossier `web-crawling` contient le code des robots d'indexation. Il s'agit d'un projet `Scrapy` pour `Python`.

La commande

    scrapy crawl seLogerSpider -o output.json

lance le robot d'indexation `seLogerSpider` défini dans `spiders.py` qui fouille le site correspondant en sauvegardant les données collectées dans `output.json`.
