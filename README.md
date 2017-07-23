# openbazaar-etsy-import

All you need to do is:

* Drop your export csv from etsy into this folder.
* Run the script.

```
pip install etsy-to-openbazaar
```

```
$ etsy-to-openbazaar --help
Usage: etsy-to-openbazaar [OPTIONS]

  Python application to import Etsy CSV Listings to OpenBazaar

  Example: import_listings.py -o UNITED_STATES -d UNITED_STATES -d CANADA

Options:
  -f, --file TEXT         Filename to import
  -s, --server TEXT       OpenBazaar server
  -P, --port TEXT         Port for OpenBazaar server
  -u, --user TEXT         Username for OpenBazaar server
  -p, --pass TEXT         Password for OpenBazaar server
  -o, --origin TEXT       Shipping Origin Country to use
  -d, --destination TEXT  Shipping Countries to use (use multiple flags)
  -v, --verbose           Be more Verbose
  --help                  Show this message and exit.
```
