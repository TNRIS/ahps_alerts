# -*- coding: utf-8 -*-

"""AHPS Alerts"""
import json

import feedparser
import re
from bs4 import BeautifulSoup

GAUGE_PATTERN = re.compile('[A-Z]{4}\d')
DATA_ENTRY_PATTERN = re.compile('(\S+\s*)*:(\s\S*)+|(\S+\s*)*:(\s\S*)+')
DATA_ITEM_PATTERN = re.compile(re.compile('\S+\s*:\s\S+'))

REGIONS = {
    'texas': {
        'description': 'Statewide alerts',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/tx.rss'
    },
    'ama': {
        'description': 'Amarillo, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/ama.rss'
    },
    'ewx': {
        'description': 'Austin, San Antonio, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/ewx.rss'
    },
    'bro': {
        'description': 'Brownsville, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/bro.rss'
    },
    'crp': {
        'description': 'Corpus Christi, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/crp.rss'
    },
    'epz': {
        'description': 'El Paso, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/epz.rss'
    },
    'fwd': {
        'description': 'Fort Worth, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/fwd.rss'
    },
    'hgx': {
        'description': 'Houston, Galveston, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/alert/hgx.rss'
    },
    'lub': {
        'description': 'Lubbock, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/fcst/lub.rss'
    },
    'maf': {
        'description': 'Midland, Odessa, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/fcst/maf.rss'
    },
    'sjt': {
        'description': 'San Angelo, Texas',
        'feed': 'https://water.weather.gov/ahps2/rss/fcst/sjt.rss'
    }
}


def get_alerts(office):
    """
    Retrieves the National Weather Service Advanced Hydrologic Prediction Service

    Args:
        office: the region the gauge alert is in

    Returns:
        Parsed alerts in JSON format
    """
    d = feedparser.parse(REGIONS[office]['feed'])
    alerts = d['entries']
    parsed_alerts = {}
    for alert in alerts:
        alert_title = alert['title']
        parsed_alerts[parse_for_gauge(alert_title)] = parse_summary(alert_title, alert['summary'])

    return json.dumps(parsed_alerts)


def parse_for_gauge(s):
    """
    Parses a string for a valid gauge ID

    Args:
        s: The string to be parsed

    Returns:
        Returns a matching gauge ID or None if not found
    """
    g = GAUGE_PATTERN.search(s)
    if g:
        return g.group(0)
    return None


def parse_summary(title, data):
    """
    Parses the alert feed for data and returns a nested dictionary
    of alert values

    Args:
        title: the alert title
        data: the alert summary

    Returns:
        Returns a nested dictionary of parsed alert information.
    """
    soup = BeautifulSoup(data, 'html.parser')
    summary = {'title': title}

    sections = soup.find_all("h2")
    subsections = soup.find_all(["u", "i"])
    data_items = soup.find_all(text=DATA_ITEM_PATTERN)

    section = None
    subsection = None

    for element in soup.descendants:
        if element in sections:
            section = element
            summary[section.text] = {}
        elif element in subsections:
            subsection = element
            summary[section.text][subsection.text] = {}
        elif element in data_items:
            data_key, data_value = (d.strip() for d in element.split(": "))
            summary[section.text][subsection.text][data_key] = data_value

    return summary


if __name__ == '__main__':
    print(get_alerts('texas'))
