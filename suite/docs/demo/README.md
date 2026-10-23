# Reproduce the documentation screenshots

These images use real current page templates and synthetic fixtures only. No router, NAS, SMTP account, database or user log is contacted. The SMB image renders the actual shell menu using stubbed read-only configuration/status providers.

Requires Python 3, PHP CLI, Node.js with Playwright and a usable Chrome/Chromium executable. On GitHub the dedicated screenshot workflow creates PNGs, checks rendering, compresses the images and records checksum inventories.

```sh
python3 suite/docs/demo/download_vendor.py /tmp/keentool-doc-vendor
KT_DOC_VENDOR=/tmp/keentool-doc-vendor KT_DOC_PHP=/usr/bin/php8.3 python3 suite/docs/demo/build_demo.py /tmp/keentool-doc-preview
KT_DOC_BROWSER=/usr/bin/google-chrome node suite/docs/demo/render.cjs /tmp/keentool-doc-preview suite/docs/screenshots
```

Run from the KeenTool repository root; install Playwright in your Node environment first. Vendor dependencies are fetched from pinned public package versions into a temporary directory, not installed on a router. The browser routes all page/API requests to local fixtures. `render-report.json` records JavaScript rendering errors. Review the generated images before publication. The screenshot workflow quantizes PNGs with Pillow to keep documentation lightweight.
