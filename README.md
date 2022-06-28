# pdfmarks
Download a list of urls into pdfs (bookmarking).

```shell
mkdir out
touch urls.txt
cp config.default.ini config.ini


poetry install
poetry run python pdfmarks.py
```

After waiting for a day capturing pdfs of 8k webpages I can say the following:
- finder doesn't like 8k files in a folder, so there is a configuration option take the first X letters of the domain name and create subfolders
- mac user interface has main thread issues all over, it doesn't like you moving a thousand files with the mouse
- the ux of searching for a phrase in loads of files is pretty dire, it gives me a list of slugified pdfs and i need to open each to see if that's the page im looking for.
- 8k pdfs are 7GB 

But please go ahead if you want to play with this!
