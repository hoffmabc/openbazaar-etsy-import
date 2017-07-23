#!/usr/bin/env python

import base64
import csv
import requests

import click


__session = None
verbose = False
api_url = 'http://{server}:{port}/api/v1'

countries = [
    'NA', 'ALL', 'NORTH_AMERICA', 'SOUTH_AMERICA', 'EUROPE', 'AFRICA', 'ASIA', 'ALBANIA', 'ALGERIA',
    'AMERICAN_SAMOA', 'ANDORRA', 'ANGOLA', 'ANGUILLA', 'ANTIGUA', 'ARGENTINA', 'ARMENIA', 'ARUBA', 'AUSTRALIA',
    'AUSTRIA', 'AZERBAIJAN', 'BAHAMAS', 'BAHRAIN', 'BANGLADESH', 'BARBADOS', 'BELARUS', 'BELGIUM', 'BELIZE',
    'BENIN', 'BERMUDA', 'BHUTAN', 'BOLIVIA', 'BONAIRE_SINT_EUSTATIUS_SABA', 'BOSNIA', 'BOTSWANA', 'BOUVET_ISLAND',
    'BRAZIL', 'BRITISH_INDIAN_OCEAN_TERRITORY', 'BRUNEI_DARUSSALAM', 'BULGARIA', 'BURKINA_FASO', 'BURUNDI',
    'CABO_VERDE', 'CAMBODIA', 'CAMEROON', 'CANADA', 'CAYMAN_ISLANDS', 'CENTRAL_AFRICAN_REPUBLIC', 'CHAD', 'CHILE',
    'CHINA', 'CHRISTMAS_ISLAND', 'COCOS_ISLANDS', 'COLOMBIA', 'COMOROS', 'CONGO_REPUBLIC', 'CONGO',
    'COOK_ISLANDS', 'COSTA_RICA', 'COTE_DIVOIRE', 'CROATIA', 'CUBA', 'CURACAO', 'CYPRUS', 'CZECH_REPUBLIC',
    'DENMARK', 'DJIBOUTI', 'DOMINICA', 'DOMINICAN_REPUBLIC', 'ECUADOR', 'EGYPT', 'EL_SALVADOR',
    'EQUATORIAL_GUINEA', 'ERITREA', 'ESTONIA', 'ETHIOPIA', 'FALKLAND_ISLANDS', 'FAROE_ISLANDS', 'FIJI', 'FINLAND',
    'FRANCE', 'FRENCH_GUIANA', 'FRENCH_POLYNESIA', 'FRENCH_SOUTHERN_TERRITORIES', 'GABON', 'GAMBIA', 'GEORGIA',
    'GERMANY', 'GHANA', 'GIBRALTAR', 'GREECE', 'GREENLAND', 'GRENADA', 'GUADELOUPE', 'GUAM', 'GUATEMALA', 'GUERNSEY',
    'GUINEA', 'GUINEA_BISSAU', 'GUYANA', 'HAITI', 'HEARD_ISLAND', 'HOLY_SEE', 'HONDURAS', 'HONG_KONG', 'HUNGARY',
    'ICELAND', 'INDIA', 'INDONESIA', 'IRAN', 'IRAQ', 'IRELAND', 'ISLE_OF_MAN', 'ISRAEL', 'ITALY', 'JAMAICA',
    'JAPAN', 'JERSEY', 'JORDAN', 'KAZAKHSTAN', 'KENYA', 'KIRIBATI', 'NORTH_KOREA', 'SOUTH_KOREA', 'KUWAIT',
    'KYRGYZSTAN', 'LAO', 'LATVIA', 'LEBANON', 'LESOTHO',
    'LIBERIA', 'LIBYA', 'LIECHTENSTEIN', 'LITHUANIA', 'LUXEMBOURG', 'MACAO', 'MACEDONIA', 'MADAGASCAR', 'MALAWI',
    'MALAYSIA', 'MALDIVES', 'MALI', 'MALTA', 'MARSHALL_ISLANDS', 'MARTINIQUE', 'MAURITANIA', 'MAURITIUS', 'MAYOTTE',
    'MEXICO', 'MICRONESIA', 'MOLDOVA', 'MONACO', 'MONGOLIA', 'MONTENEGRO', 'MONTSERRAT', 'MOROCCO', 'MOZAMBIQUE',
    'MYANMAR', 'NAMIBIA', 'NAURU', 'NEPAL', 'NETHERLANDS', 'NEW_CALEDONIA', 'NEW_ZEALAND', 'NICARAGUA', 'NIGER',
    'NIGERIA', 'NIUE', 'NORFOLK_ISLAND', 'NORTHERN_MARIANA_ISLANDS', 'NORWAY', 'OMAN', 'PAKISTAN', 'PALAU', 'PANAMA',
    'PAPUA_NEW_GUINEA', 'PARAGUAY', 'PERU', 'PHILIPPINES', 'PITCAIRN', 'POLAND', 'PORTUGAL', 'PUERTO_RICO', 'QATAR',
    'REUNION', 'ROMANIA', 'RUSSIA', 'RWANDA', 'SAINT_BARTHELEMY', 'SAINT_HELENA', 'SAINT_KITTS', 'SAINT_LUCIA',
    'SAINT_MARTIN', 'SAINT_PIERRE', 'SAINT_VINCENT', 'SAMOA', 'SAN_MARINO', 'SAO_TOME', 'SAUDI_ARABIA', 'SENEGAL',
    'SERBIA', 'SEYCHELLES', 'SIERRA_LEONE', 'SINGAPORE', 'SINT_MAARTEN', 'SUCRE', 'SLOVAKIA', 'SLOVENIA',
    'SOLOMON_ISLANDS', 'SOMALIA', 'SOUTH_AFRICA', 'SOUTH_SUDAN', 'SPAIN', 'SRI_LANKA', 'SUDAN', 'SURINAME',
    'SVALBARD', 'SWAZILAND', 'SWEDEN', 'SWITZERLAND', 'SYRIAN_ARAB_REPUBLIC', 'TAIWAN', 'TAJIKISTAN', 'TANZANIA',
    'THAILAND', 'TIMOR_LESTE', 'TOGO', 'TOKELAU', 'TONGA', 'TRINIDAD', 'TUNISIA', 'TURKEY', 'TURKMENISTAN',
    'TURKS_AND_CAICOS_ISLANDS', 'TUVALU', 'UGANDA', 'UKRAINE', 'UNITED_ARAB_EMIRATES', 'UNITED_KINGDOM',
    'UNITED_STATES', 'URUGUAY', 'UZBEKISTAN', 'VANUATU', 'VENEZUELA', 'VIETNAM', 'VIRGIN_ISLANDS_BRITISH',
    'VIRGIN_ISLANDS_US', 'WALLIS_AND_FUTUNA', 'WESTERN_SAHARA', 'YEMEN', 'ZAMBIA', 'ZIMBABWE', 'AFGHANISTAN',
    'ALAND_ISLANDS']


def login(user, password):
    global __session
    __session = requests.Session() if __session is None else __session
    payload = {'username': user, 'password': password}
    login = __session.post('{0}/login'.format(api_url), data=payload)
    if verbose:
        print("login: {0}".format(login.json().get('success')))
    if login.status_code == requests.codes.ok:
        return True
    else:
        print("Error logging in!")
        return False


def etl_listings(filename, origin, destination):
    """Format CSV listings into dictionary for uploading to OpenBazaar.

    :param filename: Filename for Etsy listings csv
    :type filename: string
    :param origin: Shipping Origin Country to use
    :type origin: string
    :param destination: Shipping Countries to use
    :type destination: list
    :returns: success
    :rtype: boolean
    """
    success = True

    with open(filename, 'rU') as f:
        reader = csv.DictReader(f, delimiter=',')

        for listing in reader:
            # Download images from listing
            image_hashes = {}
            image = requests.get(listing.get('IMAGE1'), stream=True)
            if image.status_code == 200:
                image.raw.decode_content = True
                image_64 = base64.encodestring(image.raw.read())

                # Upload to server and get hash
                payload = {
                    'image': image_64
                }
                image_hashes = __session.post('{0}/upload_image'.format(api_url), data=payload)
                image_hashes = image_hashes.json()

            # Separate comma-separated tags
            tags = [x.strip() for x in listing.get('TAGS').split(',')]

            # Insert listing into OB
            listing = {
                'keywords': tags,
                'title': listing.get('TITLE'),
                'description': listing.get('DESCRIPTION'),
                'currency_code': listing.get('CURRENCY_CODE'),
                'price': listing.get('PRICE'),
                'process_time': 'TBD',
                'images': image_hashes.get('image_hashes'),
                'expiration_date': '',
                'metadata_category': 'physical good',
                'nsfw': 'false',
                'terms_conditions': '',
                'returns': '',
                'shipping_currency_code': listing.get('CURRENCY_CODE'),
                'shipping_domestic': '',
                'shipping_international': '',
                'category': '',
                'condition': '',
                'sku': '',
                'free_shipping': 'false',
                'ships_to': destination,
                'shipping_origin': origin
            }
            if verbose:
                print(listing)
            success = upload(listing)
        return success


def upload(listing):
    posted = __session.post('{0}/contracts'.format(api_url), data=listing)
    if posted.status_code != requests.codes.ok:
        print("Error uploading listing {0}".format(listing.get('title')))
        return False
    if verbose:
        print("Uploaded listing {0}".format(listing.get('title')))
    return True


@click.command()
@click.option('--file', '-f', 'filename', default='listings.csv', help='Filename to import')
@click.option('--server', '-s', default='localhost', help='OpenBazaar server')
@click.option('--port', '-P', default='18469', help='Port for OpenBazaar server')
@click.option('--user', '-u', default='user', help='Username for OpenBazaar server')
@click.option('--pass', '-p', 'password', default='hunter2', help='Password for OpenBazaar server')
@click.option('--origin', '-o', default='ALL', help='Shipping Origin Country to use')
@click.option('--destination', '-d', default=['ALL'], help='Shipping Countries to use (use multiple flags)',
              multiple=True)
@click.option('--verbose', '-v', 'verbosity', is_flag=True, help='Be more Verbose')
def entry(filename, server, port, user, password, origin, destination, verbosity):
    """Python application to import Etsy CSV Listings to OpenBazaar

    Example: import_listings.py -o UNITED_STATES -d UNITED_STATES -d CANADA

    """
    global verbose, api_url

    verbose = verbosity
    api_url = api_url.format(server=server, port=port)

    # manually verify origin & destination because type.click.Choice() is too verbose in --help
    bad_countries = []
    destinations = list(destination)
    for dest in destinations:
        if dest not in countries:
            bad_countries.append(dest)
    if origin not in countries:
        bad_countries.append(origin)
    if bad_countries:
        print("Invalid countries: {0}".format(','.join(bad_countries)))
        print("Please use one of the following: {0}".format(' , '.join(countries)))
        exit()

    if login(user, password):
        status = etl_listings(filename, origin, destination)
        if not status:
            # Specific errors should be printed from respective functions
            print("Errors occured uploading. Please try again")


if __name__ == '__main__':
    entry()
