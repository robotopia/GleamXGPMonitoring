(viewdocumentation)=

# View the documentation

The documentation for this app is available in two places:

- As html (once built) in the folder `docs/_build/index.html`
- On [Read The Docs](https://gleamxgpmonitoring.readthedocs.io/en/latest/)

Both of these are built from the one set of documents which are in the `docs` folder.

(updatedocumentation)=

## Update the documentation

All the documentation for this project is stored in `docs/`.
The documentation is being build using [Sphinx](https://www.sphinx-doc.org/en/master/).
The `conf.py` file holds the configuration for Sphinx.

The docs are stored as a set of `.md` files.
See [these docs](https://myst-parser.readthedocs.io/en/latest/index.html) for an intro to this format and what Sphinx supports.

### NOTE

An editor like [VSCode](https://code.visualstudio.com/) is recommended for editing the docs as it understands the `.md`` format and will help you avoid common mistakes. Pressing <kbd>Ctrl</kbd>+<kbd>Shift</kbd>+<kbd>V</kbd> will open a live render of your document.

## Building the docs

Building an html version of the documentation is easy:

```bash
cd docs
make html
```

If you see red warnings about "document isn’t included in any toctree", this is not fatal and can be ignored.
Similarly, complaints about "Non-consecutive header level increase" can be ignored.

### NOTE

Sphinx doesn’t rebuild pages that it doesn’t think have changed. If the docs aren’t updating when you rebuild them then run `make clean` to delete all the rendered docs and then `make html` to do a full rebuild.
