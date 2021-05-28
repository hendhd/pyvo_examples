#! /usr/bin/ python
# -*- coding=utf-8 -*- 

# A demo program to show how datalink and SODA in PyVO work.

import pyvo
import warnings
import sys

# Keep the output of this example "sane".
if not sys.warnoptions:
  warnings.simplefilter("ignore")


def main():
  # Fetch a datalink table via TAP (see below)
  table=get_datalink_table()

  # Iterate over the datalink objects constructed by the datalink block
  # in the VO-table and the pub_did of each table row.
  for dl in table.iter_datalinks():

    # Get the preview object from the datalink
    datalink_preview = next(dl.bysemantics('#preview'))

    #print the access_url from the preview object
    print ("Access URL: ", datalink_preview['access_url'])



def get_datalink_table():
  """We need this function to obtain a table with datalinks contained.
  So this is *not* about the datalink bit"""

  # Make the TAP service object
  service = pyvo.dal.TAPService ("http://dc.zah.uni-heidelberg.de/tap")

  # Query the TAP service with a simple ADQL query.
  result = service.search ("SELECT TOP 3 * FROM lsw.plates")

  return result



if __name__=="__main__":
  main()



