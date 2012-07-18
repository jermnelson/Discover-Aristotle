"""
 :mod:`help_loader` Loads help rst files for use in the discovery layer
"""
__author__ = "Gautam Webb"

from docutils.core import publish_string
from BeautifulSoup import BeautifulSoup
import os,sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
help_loader = dict()

fixures_walker = os.walk(CURRENT_DIR)
fixures_listing = next(fixures_walker)[2]

def get_file(filename,fixures_dir=CURRENT_DIR):
    """
    Helper function opens and returns the file contents of filename

    :param filename: Filename
    """
    file_obj = open(os.path.join(fixures_dir,filename),'rb')
    file_contents = file_obj.read()
    file_obj.close()
    return file_contents

for filename in fixures_listing:
    root,extension = os.path.splitext(filename)
    if extension == '.rst':
        raw_contents = get_file(filename,CURRENT_DIR)
        rst_contents = publish_string(raw_contents,
                                      writer_name="html")
        rst_soup = BeautifulSoup(rst_contents)
        main_contents = rst_soup.find("div",attrs={"class":"document"})
        help_loader[root] = main_contents.prettify()
