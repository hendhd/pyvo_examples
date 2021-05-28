#! /usr/bin/ python
# -*- coding=utf-8 -*- 

# A demo program for PyVO
# 1. Query SIMBAD to get galaxies of the fornax cluster
# 2. Get a datalink from the fornax images at the GAVO dc
# 3. Use the datalink and SODA to make a cutout on this image around the
# galaxies we are interested in. 
#
# Markus Demleitner and Hendrik Heinl
# heinl@g-vo.org
#

from astropy import units as u
import pyvo

import tempfile
import contextlib
import os
import warnings
import sys

# Keep the output of this example "sane".
if not sys.warnoptions:
  warnings.simplefilter("ignore")




def get_galaxies():
  """Get information of galaxies in the fornax cluster from SIMBAD"""

  # Make the TAP service object
  service = pyvo.dal.TAPService ("http://simbad.u-strasbg.fr:80/simbad/sim-tap")

  # Query the TAP service with a simple ADQL query.
  result = service.search ("""
  SELECT TOP 15
  oid,ra,dec,galdim_majaxis
  FROM basic
  WHERE 1=CONTAINS(
  POINT('',ra, dec),
  CIRCLE('',54.81426, -35.4652, 0.6))
  AND galdim_majaxis>0.4 """)

  return result

# PyVO won't let us send FITS image via samp, so here is the workaround
# to make it do so!
@contextlib.contextmanager
def accessible_binary(bytes, suffix=".fits"):
    """
    a context manager making some bytes (typically: an image)
    available with a URL for local SAMP clients.
    """
    handle, f_name = tempfile.mkstemp(suffix=suffix)
    with open(handle, "wb") as f:
        f.write(bytes)
    try:
        yield "file://" + f_name
    finally:
        os.unlink(f_name)



def main():
  # get galaxies from SIMBAD
  galaxies=get_galaxies()

  # Sent the table to Aladin
  galaxies.broadcast_samp('Aladin')

  # make the service object of the GAVO TAP service
  svc = pyvo.dal.TAPService("http://dc.g-vo.org/tap")
	# get the "large" version of a fornax cluster mosaic
  result = svc.run_sync("SELECT did FROM fornax.data WHERE pixelSize[1]>10000")

  # We only have one result; get the datalink object for it.
  dl = next(result.iter_datalinks())
  
  # And now get "the" processing service in there (there could be
  # more, but there aren't here)
  soda_svc = dl.get_first_proc()

  # and now do the cutouts:
  for (oid, ra, dec, galmajax) in galaxies.to_table():
    a=soda_svc.process(circle=[ra*u.deg, dec*u.deg, galmajax/60*u.deg]).read()
    
    with accessible_binary(a) as img_url:
      with pyvo.samp.connection() as conn:

        pyvo.samp.send_image_to(conn=conn,
        url=img_url, client_name="Aladin")


if __name__=="__main__":
  main()

