# MDS

```bash
# Скрейпинг каталога
poetry run scrapy crawl catalog -O catalog.csv

# Скачивание записей
poetry run scrapy crawl audio -a utf8_tags=1 -a links=http://mds.kallisto.ru/Terri_Bisson_-_Maki.mp3,http://mds.kallisto.ru/Stiven_Bakster_-_Shiina-5.mp3

# Генерация таблицы в формате Numbers
poetry run python -m mds.cli generate-numbers-doc ./catalog.csv catalog.numbers
```
