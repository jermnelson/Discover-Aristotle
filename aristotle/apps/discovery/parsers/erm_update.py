"""
 mod:`erm_update`: Update Electronic Stub Records from a CSV file
                   with URL, ISBN, and other fields extracted from an ILS
                   ERM and checkin records.
"""
__author__ = "Jeremy Nelson"
import csv,urllib,httplib2
import xml.etree.ElementTree as ElementTree
from settings import CSV_FILE,SOLR_UPDATE_URL

ELECTRONIC_JRNLS = {}
    
def load_csv(csv_file=CSV_FILE):
    """
    Method parses through CSV file and updates electronic journals dict with
    the bib number as the key and the urls, holdings, and issn (if present) for
    look-up by the MARC parser.

    :param csv_file: Common separated file, defaults to settings values
    """
    csv_reader = csv.reader(open(csv_file,'rb'))
    for row in csv_reader:
        row_dict = {}
        urls,paired_holdings,counter = [],[],0
        bib_id = row[0][0:-1] # Removes last digit as per ILS convention
        if len(row[2]) > 1:
            row_dict['issn'] = row[2]
        reversed_fields = row[3:]
        reversed_fields.reverse()
        for value in reversed_fields:
            holdings = []
            if value.lower().startswith('http'):
                raw_url = value.split(' ') # Attempts to split out text from url
                
                urls.append(raw_url[0])
                paired_holdings.append("{0} ".format(' '.join(raw_url[1:])))
            else:
                try:
                    int(value[0]) # Assumes holdings starts with an int
                    paired_holdings[counter] = "{0} {1}".format(paired_holdings[counter],
                                                                value)
                    counter += 1
                except:
                    pass
        row_dict['urls'] = '|'.join(urls)
        row_dict['holdings'] = '|'.join(paired_holdings)
        ELECTRONIC_JRNLS[bib_id] = row_dict
                
                
        
