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
    current_count += 1
    url = url.strip()
    out = "out/" + slugify(url) + ".pdf"

    if exists(out):
        return

    logging.info("[%s] saving %s", len(urls) - current_count, url)

    try:
        from_url(url, out, options={"footer-center": url})
    except OSError:
        logging.info("  error: %s", url)
        pass


if __name__ == "__main__":
    urls = open("urls.txt", "r").readlines()
    current_count = 0
    total_count = len(urls)

    shuffle(urls)
    logging.basicConfig(
        format="%(asctime)s: %(message)s", level=logging.INFO, datefmt="%H:%M:%S"
    )
    logging.info("%s total urls", len(urls))

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(save_pdf, urls)
