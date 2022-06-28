# Reference https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
# TODO: read-args-from-stdin
from os.path import exists
from pdfkit import from_url
from random import shuffle
from slugify import slugify
import concurrent.futures
import logging


def save_pdf(url):
    global current_count
    global total_count
    current_count += 1
    url = url.strip()
    out = get_out(url)

    logging.info("[%s] saving %s", total_count - current_count, url)

    try:
        from_url(url, out, options={"footer-center": url})
    except OSError:
        logging.info("  error: %s", url)
        with open("errors.txt", "a") as error_file:
            error_file.write(url + "\n")
        return

    with open("processed.txt", "a") as the_file:
        the_file.write(url + "\n")


def get_out(url):
    return "out/" + slugify(url) + ".pdf"


if __name__ == "__main__":
    _urls = open("urls.txt", "r").readlines()

    # prevent retrying errors
    _errors = []
    if exists("errors.txt"):
        _errors = open("errors.txt", "r").readlines()

    # prevent retrying processed
    _processed = []
    if exists("processed.txt"):
        _processed = open("processed.txt", "r").readlines()

    urls = []
    for url in _urls:
        url = url.strip()
        out = get_out(url)
        if url in _processed or url in _errors or exists(out):
            continue
        urls.append(url)

    current_count = 0
    total_count = len(urls)

    shuffle(urls)
    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S"
    )
    logging.info("%s total urls", total_count)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_pdf, urls)
