# Reference https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
from os.path import exists
from pdfkit import from_url
from random import shuffle
from slugify import slugify
import tldextract
import concurrent.futures
import logging
import configparser
import os

MODE_APPEND = "a"
MODE_READ = "r"
TXT_PROCESSED = "processed.txt"
TXT_ERRORS = "errors.txt"
TXT_URLS = "urls.txt"


def save_pdf(_url):
    global current_count
    global total_count
    current_count += 1
    _out = get_out(_url)
    _relpath= _out.replace(config['IO']['OutDirectory'] + '/', "")

    logging.info("[%s] saving %s into %s", total_count - current_count, _url, _relpath)

    try:
        from_url(_url, _out, options={"footer-center": _url})
    except OSError:
        logging.info("  error: %s", _url)
        log_url_error(_url)
        return

    log_url_processed(_url)


def log_url_error(_url):
    with open(TXT_ERRORS, MODE_APPEND) as error_file:
        error_file.write(_url + "\n")


def log_url_processed(_url):
    with open(TXT_PROCESSED, "a") as the_file:
        the_file.write(_url + "\n")

def get_domain(_url):
    result = tldextract.extract(_url)
    return result.domain


def get_out(_url):
    path = config['IO']['OutDirectory']

    if not exists(path):
        exit(path + ' does not exist!')
    chars = int(config['IO']['SubDirectoryChars'])
    domain = get_domain(_url)
    if chars > 0:
        path += '/' + domain[:chars]

    if not os.path.exists(path):
        os.mkdir(path)

    return path + "/" + slugify(_url) + ".pdf"


if __name__ == "__main__":
    # load config
    config = configparser.ConfigParser()
    try:
        config.read_file(open('config.ini'))
    except FileNotFoundError:
        exit('config.ini does not exist!')

    # prevent retrying
    store = {}
    for fn in [TXT_ERRORS,TXT_PROCESSED,TXT_URLS]:
        if not exists(fn):
            store[fn] = []
            continue

        store[fn] = open(fn, MODE_READ).read().splitlines()

    urls = []
    for url in store[TXT_URLS]:
        if url in store[TXT_PROCESSED] or url in store[TXT_ERRORS]:
            continue

        if exists(get_out(url)):
            if url not in store[TXT_PROCESSED]:
                log_url_processed(url)
            continue

        urls.append(url)

    # prevent hitting the same domain repeatedly
    shuffle(urls)

    current_count = 0
    total_count = len(urls)

    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S"
    )
    logging.info("%s total urls", total_count)
    logging.info("Saving into %s", config['IO']['OutDirectory'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_pdf, urls)
