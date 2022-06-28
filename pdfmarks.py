# Reference https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
from os.path import exists
from pdfkit import from_url
from random import shuffle
from slugify import slugify
import concurrent.futures
import logging

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

    logging.info("[%s] saving %s", total_count - current_count, _url)

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


def get_out(_url):
    return "out/" + slugify(_url) + ".pdf"


if __name__ == "__main__":
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
    shuffle(urls)

    current_count = 0
    total_count = len(urls)

    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S"
    )
    logging.info("%s total urls", total_count)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_pdf, urls)
