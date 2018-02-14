# IDPoorDataDownloader
--------------------------------------------------------------------------------------------

This is a standalone python script for downloading JSON data from a web api, matching records within an ESRI shapefile, calculating some statistics, and generating a new ESRI shapefile with these statistics appended. 

This does not require an ESRI installation or the ArcPy module. PyShp is implemented instead to allow for use in non ESRI-stack envrionments.

[Click to see script diagram](/Home.asciidoc)

--------------------------------------------------------------------------------------------
 
 - download_idpoor.py
 - VERSION: 1.0.0 - January 5, 2018
 - AUTHOR: Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz

# Parameters 
             - Search code for "User Parameters" for areas
               where input parameters can be configured.
             - For this public repository, all passwords, usernames and URLs have been removed.
# Dependencies
            - Python 3.7 - recommend to also install 'pip package installer'
                           see https://pip.pypa.io/en/stable/installing/
            - 'Requests' for Python - see http://docs.python-requests.org/en/master/ 
                     "pip install requests"
            - 'pyShp' - see https://pypi.python.org/pypi/pyshp 
                     "pip install pyshp"

# Limitations
    - At this point, the script only works for IDPOOR13 report. Other reports will 
    fail.
--------------------------------------------------------------------------------------------
# Known Issues
  - Some issue with the shapefile dataset when Khmer text is in the commune name or other
     fields, causes issues with the output dataset, stripping ID's and editing the wrong fields.
     To fix, remove all Khmer text (some may still look like English script, but deleting and
     re-writing it appears to work. There were two instances in the khm_admbnda_adm3_gov.shp 
     dataset that caused this. (Object ID 569 and 1378).

  -  The timeout period for authentication appears to be 30 minutes.
     To circumvent this, the script re-authenticates every 300 requests. 
--------------------------------------------------------------------------------------------
