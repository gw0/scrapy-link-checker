scrapy-link-checker
===================

Spider for checking broken links in Scrapy v1.


Usage
-----

Run spider manually:

```bash
## setup environment
$ python3 -m venv venv
$ . venv/bin/activate
$ pip3 install -r requirements.txt

## run spider1 manually
$ mkdir ./logs/
$ scrapy crawl spider1 -o ./logs/spider1-log.csv
```

Run spider with Scrapyd:

```bash
## run Scrapyd in another terminal
$ docker run -it --rm -e USERNAME=super -e PASSWORD=links123 -p 6800:6800 -v scrapyd-volume:/scrapyd gw000/scrapyd-authenticated

## run spider1 with Scrapyd
$ vi scrapy.cfg
$ scrapyd-deploy -a
$ curl --user super:links123 http://localhost:6800/schedule.json -d project=bot -d spider=spider1

## open http://localhost:6800/
```
