# Style Atlas

A responsive visual reference gallery: choose a picture, then say “use style 17.”
The current default is **MJ-S008 — Olive Kitchen Chronicle**.

## One source, desktop and phone

`data/catalog.json` owns the 29 style records and default. `src/styles.css` and
`src/app.js` are shared by both screen sizes. `tools/build.py` produces a normal
static HTTPS site and a self-contained offline edition from the same data.
There are no runtime API calls, external fonts, accounts, analytics or secrets.

Every card, thumbnail, attribution and full recipe exists in the initial HTML.
JavaScript enhances search, family filters, copying and enlarging; it does not
create the core content. This repairs the former empty-gallery failure when a
phone's downloaded-file preview restricts scripts. The exact phone viewer was
not independently reproduced.

CSS and JavaScript filenames include content hashes, so a changed release does
not reuse a browser's cached copy of old controls or layout.

## Update once

1. Edit `data/catalog.json`; preserve existing IDs, names and recipes unless an
   intentional catalog edit is requested. Add reference JPEGs to
   `assets/thumbnails/` for new entries. Keep source job ID, image index, observed
   creator label and link together.
2. Run `python tools/build.py`, `python tools/check.py` and
   `node tests/logic.cjs`.
3. Commit and push to `main`. The Pages workflow builds, checks and publishes
   the shared site. Failed checks prevent publication. Both phone and desktop
   receive the same release.

Use GitHub's **Run workflow** action to rebuild after an external setting change.
The workflow uses GitHub's short-lived job token; no extra persistent credential
is required. Public GitHub Pages hosting is used without a paid service.

## Reference imagery

The 29 original source thumbnails are labeled reference images, with source
links and observed creator labels on each card. No ownership of those images is
claimed. The recipes describe rendering traits for fresh subjects, rather than
copying the depicted identities or exact scenes. Camera, lighting, art-medium
and material terms are descriptive inferences, not verified production metadata.

Source associations for **MJ-S021 Chromatic Salon** and **MJ-S022 Contourwave**
are corrected and tested; the stable style numbers and names are preserved.

## Verification

The build tests assert 29 cards and recipes in both generated HTML editions
before any JavaScript executes, 29 unique thumbnail images, correct job/image
associations, and no local paths or private Library identifiers. JavaScript tests
cover all style numbers and names, all seven families and the current default.
