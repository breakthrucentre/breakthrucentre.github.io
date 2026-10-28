# Breakthrough Centre website

The website for Breakthrough Centre and Breakthrough Centre Academy, Etete, Groutville.
It is plain HTML, CSS and JavaScript, so it runs free on GitHub Pages.

- `docs/`: the live website (GitHub Pages publishes this folder)
- `tools/build.py`: all the page text lives here; running `python3 tools/build.py` rebuilds every page in `docs/`
- `tools/prep_images.py`: makes web-sized photos from the originals

## GitHub Pages settings

Settings → Pages → Build and deployment → **Deploy from a branch** → branch **main**, folder **/docs** → Save.
The site is published at https://breakthrucentre.github.io/

## Making changes

Ask Claude in the Breakthrough Centre project (with GitHub connected) to change text, photos or pages.
Claude edits `tools/build.py`, rebuilds `docs/`, and pushes to GitHub; the live site updates within a few minutes.

## After it is live

- Add the site to Google Search Console and submit `sitemap.xml`.
- Put the website address on your Google Business Profile and both Facebook pages.
- If you later buy a domain (for example breakthroughcentre.co.za), change `BASE_URL`
  at the top of `tools/build.py`, rebuild, and set the domain under Settings → Pages.
