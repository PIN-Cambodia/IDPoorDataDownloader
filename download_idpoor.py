#--------------------------------------------------------------------------------------------
# download_idpoor.py
# VERSION: 1.0.0 - January 5, 2018
# AUTHOR: Blake Gardiner for People in Need  - blake.gardiner@peopleinneed.cz
#
# PARAMETERS: Search code for "User Parameters" for areas
#                where input parameters can be configured.
# DEPENDENCIES:
#            - Python 3.7 - recommend to also install 'pip package installer'
#                           see https://pip.pypa.io/en/stable/installing/
#            - 'Requests' for Python - see http://docs.python-requests.org/en/master/ 
#                     "pip install requests"
#            - 'pyShp' - see https://pypi.python.org/pypi/pyshp 
#                     "pip install pyshp"
# ABOUT:
#
#
# LIMITATIONS
#    At this point, the script only works for IDPOOR13 report. Other reports will 
#    fail.
#--------------------------------------------------------------------------------------------
# KNOWN ISSUES
#  *  Some issue with the shapefile dataset when Khmer text is in the commune name or other
#     fields, causes issues with the output dataset, stripping ID's and editing the wrong fields.
#     To fix, remove all Khmer text (some may still look like English script, but deleting and
#     re-writing it appears to work. There were two instances in the khm_admbnda_adm3_gov.shp 
#     dataset that caused this. (Object ID 569 and 1378).
#
#  *  The timeout period for authentication appears to be 30 minutes.
#     to circumvent this, the script re-authenticates every 300 requests. 
#--------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------
# create loggers for console and to file.
import logging
logger = logging.getLogger('download_idpoor_log')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('download_idpoor_log.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
#--------------------------------------------------------------------------------------------

try:
    import datetime
    import json
    import os
    import shutil
    import sys
    import shapefile
    import requests
    logger.info("[Module import successful.]")
except ImportError as exc:
    logger.critical("[Aborting: There was an error importing modules. Check Requests and PyShp are valid in the sys path.]")
    sys.exit()
        
def main():
    global archiveDirectory
    global sourceDirectory
    global shapeFileData 
    global outputSHP
    global idpoorfilename #filename for JSON output file.
    global headers 
    global payload
    global myIdx 
    myIdx = 1
   
    # *************************************************************************
    # User Parameters (1 of 2)**************************************************
    archiveDirectory = 'output_data/'
    sourceDirectory = 'source_data/'
    shapeFileData = "khm_admbnda_adm3_gov.shp"
    outputSHP =  str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + "_" + shapeFileData
    outputSHP = archiveDirectory + outputSHP
    # Authenticate Parameters ******************************************
    authenticateURL = 'AUTHENTICATE_URL'
    username = 'USERNAME'
    password = 'PASSWORD'
    headers = {'content-type': 'application/json', 'authorization': 'Basic d2ZwOndmcCMxMjM0NQ=='}
    payload = {"user":{"email":username,"password":password}}
    idpoorfilename = 'default'
    # Report Parameters ************************************************
    #arrReportName  - list of report names to cycle through
    arrReportName = ['idpoor13']
    #arrCommuneID - array of commune id's to cycle through
    #arrCommuneID = ['160801','160802','160901','160903','160904','160905','160906','160907','160908','160909','160910']
    arrCommuneID = [10201,10202,10203,10204,10205,10206,10207,10208,10209,10210,10211,10212,10213,10301,10302,10303,10304,10305,10306,10401,10402,10403,10404,10405,10406,10407,10408,10409,10501,10502,10503,10505,10506,10507,10509,10602,10603,10604,10605,10606,10607,10608,10701,10702,10703,10704,10705,10706,10801,10802,10803,10804,10805,10806,10807,10808,10901,10902,10903,10904,10905,10906,11001,11002,11003,20101,20102,20103,20104,20105,20106,20107,20108,20201,20202,20203,20204,20205,20206,20207,20208,20209,20210,20301,20302,20303,20304,20305,20306,20307,20308,20309,20310,20401,20402,20403,20404,20405,20406,20407,20408,20501,20502,20503,20504,20505,20506,20507,20601,20602,20603,20604,20605,20606,20607,20608,20609,20701,20702,20703,20704,20705,20801,20802,20803,20804,20805,20806,20807,20808,20809,20810,20901,20902,20903,20904,20905,20906,20907,21001,21002,21003,21004,21005,21006,21101,21102,21103,21104,21105,21201,21202,21203,21204,21205,21206,21301,21302,21303,21304,21305,21306,21401,21402,21403,21404,21405,30101,30102,30103,30104,30105,30106,30107,30108,30109,30110,30111,30112,30201,30202,30203,30204,30205,30206,30207,30208,30301,30302,30303,30304,30305,30306,30307,30308,30309,30310,30501,30502,30503,30504,30601,30602,30603,30604,30605,30606,30607,30608,30609,30610,30611,30612,30613,30614,30615,30701,30702,30703,30704,30705,30706,30707,30708,30709,30710,30711,30801,30802,30803,30804,30805,30806,30807,30808,31301,31302,31303,31304,31305,31306,31307,31308,31309,31310,31311,31312,31313,31314,31315,31401,31402,31403,31404,31405,31406,31407,31408,31409,31410,31411,31412,31413,31414,31501,31503,31504,31505,31506,31507,31508,31509,31510,31512,31513,31514,40101,40102,40103,40104,40105,40106,40107,40108,40109,40110,40111,40201,40202,40203,40204,40205,40301,40302,40303,40304,40401,40402,40403,40404,40405,40406,40407,40408,40409,40501,40502,40503,40504,40505,40506,40507,40508,40509,40510,40601,40602,40603,40604,40605,40606,40607,40608,40609,40610,40611,40612,40613,40701,40702,40703,40704,40705,40706,40707,40708,40709,40801,40802,40803,40804,40805,40806,40807,40808,50101,50102,50103,50104,50105,50106,50107,50108,50109,50110,50111,50112,50113,50114,50115,50201,50202,50203,50204,50205,50301,50302,50303,50304,50305,50306,50307,50308,50309,50310,50311,50312,50313,50401,50402,50403,50404,50405,50501,50502,50503,50504,50505,50506,50507,50508,50509,50510,50511,50512,50513,50514,50515,50601,50602,50603,50604,50605,50606,50607,50608,50609,50610,50611,50613,50701,50702,50703,50704,50705,50706,50707,50708,50709,50710,50711,50712,50713,50714,50715,50801,50802,50804,50805,50806,50807,50808,60101,60102,60103,60104,60105,60106,60107,60108,60109,60110,60111,60112,60113,60114,60115,60116,60117,60118,60201,60202,60203,60204,60205,60206,60207,60208,60209,60210,60211,60301,60302,60303,60304,60306,60308,60309,60310,60401,60402,60403,60404,60405,60406,60407,60501,60502,60503,60504,60505,60601,60602,60603,60604,60605,60606,60607,60608,60609,60701,60702,60703,60704,60705,60706,60707,60708,60709,60710,60801,60802,60803,60804,60805,60806,60807,60808,60809,60810,60811,60812,60813,70101,70102,70103,70104,70105,70106,70107,70108,70109,70110,70111,70201,70202,70203,70204,70205,70206,70207,70208,70209,70210,70211,70212,70213,70214,70215,70301,70302,70303,70304,70305,70306,70307,70308,70309,70310,70311,70312,70313,70314,70315,70401,70402,70403,70404,70405,70406,70407,70501,70502,70503,70504,70505,70506,70507,70508,70509,70510,70601,70602,70603,70604,70605,70606,70607,70608,70609,70612,70613,70614,70615,70616,70701,70702,70703,70704,70705,70707,70708,70709,70711,70712,70713,70715,70716,70717,70718,70719,70801,70802,70803,70804,70805,80101,80102,80103,80104,80105,80106,80107,80108,80109,80113,80115,80116,80117,80118,80122,80125,80127,80128,80201,80202,80203,80204,80206,80207,80208,80211,80301,80302,80303,80304,80305,80306,80307,80308,80309,80310,80311,80312,80313,80314,80315,80316,80317,80318,80401,80402,80403,80404,80405,80407,80408,80409,80410,80411,80412,80501,80502,80503,80504,80505,80506,80507,80601,80602,80603,80604,80605,80606,80607,80608,80609,80610,80611,80612,80613,80614,80615,80703,80704,80707,80708,80709,80710,80711,80801,80803,80804,80807,80808,80809,80811,80813,80814,80816,80901,80902,80903,80904,80905,80906,80907,80910,80911,80913,80914,81001,81002,81003,81004,81005,81006,81007,81008,81009,81010,81011,81012,81013,81014,81015,81016,81101,81102,81103,81104,81105,81106,90101,90102,90103,90104,90201,90202,90203,90301,90302,90303,90304,90401,90402,90403,90501,90502,90503,90601,90602,90603,90604,90605,90606,90701,90702,90703,90704,90705,90706,100101,100102,100103,100104,100105,100106,100107,100108,100207,100208,100209,100210,100211,100301,100302,100303,100304,100305,100306,100307,100308,100401,100402,100403,100404,100405,100406,100407,100408,100409,100410,100501,100502,100503,100504,100505,100601,100602,100603,100604,100605,100606,100607,100608,100609,100610,110101,110102,110103,110104,110105,110201,110202,110203,110204,110205,110206,110301,110302,110401,110402,110403,110404,110501,110502,110503,110504,120101,120102,120103,120104,120105,120106,120107,120108,120109,120110,120111,120112,120201,120202,120203,120204,120205,120206,120207,120208,120209,120210,120211,120301,120302,120303,120304,120305,120306,120307,120308,120401,120402,120403,120404,120405,120406,120407,120408,120409,120410,120501,120507,120508,120510,120512,120513,120514,120515,120516,120517,120518,120519,120520,120601,120602,120606,120607,120702,120703,120704,120706,120711,120712,120801,120802,120803,120807,120901,120903,120904,120905,120906,120908,120909,120910,120911,120913,121001,121002,121003,121004,121005,121101,121102,121103,121104,121105,121201,121202,121203,121204,121205,121206,121207,121208,130101,130102,130103,130104,130105,130106,130201,130202,130203,130204,130205,130206,130207,130208,130301,130302,130303,130304,130305,130306,130307,130308,130401,130402,130403,130404,130405,130406,130501,130502,130503,130504,130505,130506,130507,130508,130509,130510,130511,130512,130601,130602,130603,130604,130605,130703,130704,130705,130706,130801,130802,140101,140102,140103,140104,140105,140106,140107,140108,140109,140201,140202,140203,140204,140205,140206,140207,140208,140301,140302,140303,140304,140305,140306,140307,140308,140309,140310,140311,140312,140313,140401,140402,140403,140404,140405,140406,140407,140408,140501,140502,140503,140504,140505,140506,140507,140508,140601,140602,140603,140604,140605,140606,140607,140608,140609,140610,140701,140702,140703,140704,140705,140706,140707,140708,140801,140802,140803,140805,140807,140808,140809,140810,140811,140901,140902,140903,140904,140905,140906,140907,140908,140909,140910,140911,141001,141002,141003,141101,141102,141103,141104,141105,141106,141107,141201,141202,141203,141204,141205,141206,141207,141208,141209,141210,141211,141301,141302,141303,141304,141305,141306,141307,141308,141309,141310,141311,150101,150102,150103,150104,150105,150106,150107,150108,150109,150110,150201,150203,150204,150205,150206,150207,150208,150209,150210,150301,150302,150303,150304,150305,150306,150307,150308,150309,150310,150311,150401,150402,150403,150404,150405,150406,150407,150501,150503,150504,150505,150506,150507,150508,150601,150602,150603,150604,150605,160101,160103,160104,160201,160202,160203,160204,160301,160302,160303,160304,160305,160306,160401,160402,160403,160404,160405,160406,160501,160502,160503,160504,160505,160506,160601,160602,160603,160604,160605,160606,160607,160701,160702,160703,160704,160705,160706,160707,160801,160802,160901,160903,160904,160905,160906,160907,160908,160909,160910,170101,170102,170103,170104,170105,170106,170107,170201,170202,170203,170204,170301,170302,170303,170304,170305,170306,170401,170402,170403,170404,170405,170406,170407,170408,170409,170410,170411,170412,170601,170602,170603,170604,170605,170606,170607,170608,170609,170610,170701,170702,170703,170704,170705,170707,170708,170709,170710,170711,170712,170713,170715,170716,170902,170903,170904,170905,170906,170907,170908,170909,171001,171002,171003,171004,171005,171006,171007,171008,171009,171010,171011,171012,171013,171101,171102,171103,171104,171105,171106,171107,171108,171109,171110,171201,171202,171203,171204,171205,171206,171301,171302,171303,171304,171305,171401,171402,171403,171404,171405,180101,180102,180103,180104,180105,180201,180202,180203,180204,180205,180206,180207,180208,180209,180210,180211,180212,180213,180214,180301,180302,180303,180304,180401,180402,180403,180404,190101,190102,190103,190104,190105,190106,190107,190201,190202,190203,190204,190205,190206,190207,190301,190302,190303,190304,190305,190401,190402,190403,190404,190501,190502,190503,190504,190505,190506,190507,190508,190509,190510,190511,200103,200104,200105,200108,200109,200110,200201,200202,200203,200204,200205,200206,200207,200208,200209,200211,200212,200301,200302,200303,200304,200305,200306,200307,200308,200309,200310,200401,200402,200403,200404,200405,200406,200407,200408,200409,200410,200411,200412,200413,200414,200415,200416,200501,200502,200503,200504,200505,200507,200508,200509,200510,200511,200512,200513,200514,200515,200516,200517,200601,200602,200603,200604,200605,200606,200607,200702,200703,200704,200705,200706,200707,200708,200709,200711,200801,200802,200803,200804,200805,210101,210102,210103,210104,210105,210106,210201,210202,210203,210204,210205,210206,210207,210208,210209,210210,210211,210212,210213,210214,210215,210301,210302,210303,210304,210305,210401,210402,210403,210404,210405,210406,210407,210408,210409,210410,210411,210412,210501,210502,210503,210504,210505,210506,210601,210602,210603,210604,210605,210606,210607,210608,210609,210610,210611,210612,210613,210701,210702,210703,210704,210705,210706,210707,210708,210709,210710,210711,210801,210802,210803,210901,210902,210903,210904,210905,210906,210907,210908,210909,210910,210911,210912,210913,210914,210915,211001,211002,211003,211004,211005,211006,211007,211008,211009,211010,211011,211012,211013,211014,220101,220103,220104,220105,220106,220201,220202,220203,220204,220301,220302,220303,220304,220401,220402,220403,220404,220405,220501,220502,220503,220504,220505,220506,230101,230103,230201,230202,230203,240101,240102,240103,240104,240201,240202,240203,240204,250101,250102,250103,250104,250105,250106,250107,250201,250202,250203,250204,250205,250206,250207,250208,250209,250210,250211,250212,250301,250302,250303,250304,250305,250306,250307,250308,250309,250310,250311,250312,250313,250314,250401,250402,250403,250404,250405,250406,250407,250501,250502,250503,250504,250505,250506,250507,250508,250601,250602,250701,250702,250703,250704,250705,250706,250707,250708,250709,250710,250711,250712,250713,250714
]
    # URL Format
    # 
    getReportURL= 'REPORT_HUB_URL'
    # New Field Parameters for shapefile *******************************
    # New set for each new field.
    # Code in summarizeJSON will need to be edited in add new fields + index
    # This set is used for two purposes:
    #    -creating new field in shape file
    #    -populating the field with the correct data.
    #newFieldX = ['FieldName', 'FieldType','FieldSize','DefaultValue']
    newFieldA = ['CntHH', 'N','10','0']   #newFieldA = ['CntHH', 'N', '20','0']
    newFieldB = ['CntVillage', 'N','10','0']
    newFieldC = ['P1HH', 'N','10','0']
    newFieldD = ['P1P2HH', 'N','10','0']
    newFieldE = ['P2HH', 'N','10','0']
    
    #add all sets above to a list.
    allNewFields = [newFieldA,newFieldB,newFieldC,newFieldD,newFieldE]
    # End User Parameters (1 of 2) *************************************************
    # *************************************************************************
    
    # PRESTART 
    # Perform checks to ensure parameters are valid before proceeding.
    cleanupWorkArea() #Run a cleanup before beginning.
    Ready2Go = True 
    if not os.path.isfile(sourceDirectory + shapeFileData):
        Ready2Go = False
        logger.error("[Aborting: The source shapefile does not exist.]")
    if not len(arrReportName) > 0:
        Ready2Go = False
        logger.error("[Aborting: No report has been specified for download. (Parameter arrReportName)]")
    if not len(arrCommuneID) > 0:
        Ready2Go = False
        logger.error("[Aborting: No commune ID's have been specified for download. (Parameter arrCommuneID)]")
    #Check the 'new fields' field names are >= 10 characters long (ESRI limitation).
    if len(allNewFields) > 0:
        for entry in allNewFields:
            if not (len(entry[0]) <= 10 and len(entry[0]) > 0):
                Ready2Go = False
                logger.error("[Aborting: New fields must have length between 1 and 10 chars.]")
    else:
        Ready2Go = False
        logger.error("[Aborting: No new fields specified.]")   
    # END PRESTART
    
    
    if Ready2Go:
        #Build the URL from the data provided.
        #Run each report once for each commune.
        loopCounter = 0
        if authenticateMe(authenticateURL):
            for report in arrReportName:        
                for commune in arrCommuneID:           
                    #Only allow 300 loops before re-authenticating - as session may expire.
                    if loopCounter > 300:
                        logger.info("[Re-authenticating to preserve session...]")
                        authenticateMe(authenticateURL)
                        loopCounter = 0
                    logger.info("[Requesting Report: " + str(report) + " Commune: " + str(commune) + "]")
                    idpoorfilename = str(report) + "_" + str(commune) + "_" + str(datetime.datetime.now().strftime("%Y%m%d%H%M")) + ".json"
                    if retrieveJSON(getReportURL + str(report) + "/" + str(commune) + ".json?"):
                        #Index value - the first new field entry will have a different
                        # input shapefile to the rest.  Following calls should use the
                        # output shapfile of the first call.
                        for entry in allNewFields:
                            if myIdx == 1:
                                addFields2ShapeFile(sourceDirectory + shapeFileData,entry[0],entry[1],entry[2],entry[3], outputSHP)
                                myIdx += 1
                            else:
                                addFields2ShapeFile(outputSHP,entry[0],entry[1],entry[2],entry[3], outputSHP)
                                myIdx += 1
                    
                        summarizeJSON(str(commune), idpoorfilename)
                        loopCounter += 1
                    else: 
                        logger.error("[Aborting: Could not retrieve JSON. Something went wrong]")
                        
                    logger.info("[Finished work for Report: " + str(report) + " Commune: " + str(commune) + "]")
            #Copies the spatial reference file of the source shapefile as this is not done by PyShp.   
            shutil.copy(sourceDirectory + shapeFileData.split(".",2)[0] + ".prj", outputSHP.split(".",2)[0] + ".prj")
            cleanupWorkArea()
            
        else:
            logger.critical("[Aborting: Authentication could not be completed.]")
        
       
        logger.info("[ -------------- End of script -------------- ]\n")
    else:
        logger.error("[The script failed pre-start checks. Please review input parameters. No work was done.]")
       
def authenticateMe(authUrl):
    ##-------------------------------------------------------------------
    # Authenticates the session with the hub.
    # Need to hold cookies in a session in order to authenticate GET request
    # If response is 201 (OK) then return True, otherwise return False
    ##-------------------------------------------------------------------
    logger.info("[Attempting to authenticate to hub..." + "]")
    try:
        s = requests.Session()
        AuthenticateMe = requests.Response
        AuthenticateMe = s.post(url=authUrl, headers=headers,data=json.dumps(payload))
        global sessCookies 
        sessCookies = s.cookies
        
        logger.info("[Connected with Status Code " + str(AuthenticateMe.status_code) + "]")                                                                             
        if AuthenticateMe.status_code == 201:
            return True
        else: 
            logger.error("[Could not authenticate - check username/password are correct." + "]")
            logger.error("[" + (str(AuthenticateMe.json())) + "]")
            return False
        
    except:
        logger.critical("[An error occurred whilst authenticating.]")
        return False
        
def retrieveJSON(requestURL):
    #Retrieve JSON data with web request.
    try:
        getReport = requests.get(requestURL, headers=headers,data=json.dumps(payload), cookies=sessCookies)
        logger.info("[Response Status Code was " + str(getReport.status_code) + "]")
        if not getReport.status_code == 400:
            #print ("RESPONSE [JSON " + str(getReport.json()) + "]")
            if dumpJSON(getReport.json()):
                return True
            else:
                logger.critical("[An error occurred whilst dumping the JSON to file.]")
                return False
        else:
            logger.error("[Bad response from server. Commune ID may be invalid.]")
            return False
    except:
        logger.critical("[An error occurred whilst accessing the portal." + "]")
        logger.critical("[Failed for URL [" + requestURL + "]]")
        return False

def dumpJSON(JSONObject):
    #Write the JSON data to an output file.
    try:
        with open(idpoorfilename, 'w') as outfile:
            json.dump(JSONObject, outfile)
            logger.info("[Data written to file successfully.]")
            return True
    except:
        logger.critical("[While writing to file " + idpoorfilename + " failed with: " + sys.exc_info()[0] + "]")
        return False
    
def addFields2ShapeFile(targetSHP,newFieldName,fieldType,fieldSize,defaultValue,outputSHP):
    # Add a new fields to the target shapefile
    # Call repeatedly to add multiple fields.
    # Function creates a new file and copies existing fields/data.
    # e.g. addFields2ShapeFile(shapeFileData,"NewField2","C","50","2","Edit_" + shapeFileData)
    # INPUTS: Target Shapefile, new field name, data type, size,default value, output name.
    try:
        r = shapefile.Reader(targetSHP) # Create a new shapefile in memory
        w = shapefile.Writer() # Copy over the existing fields
        w.fields = list(r.fields)
        exitFlag = True # First, flag if the field already exists.
        for i in w.fields:
            if i[0] == newFieldName:
                exitFlag = False
                
        if exitFlag: # Only add new field if it doesn't already exist.
            # Add our new field using pyShp
            logger.info("[Adding new field '" + newFieldName + "' to the shape file]")
            w.field(newFieldName,fieldType, fieldSize)
            for rec in r.records():
                rec.append(defaultValue)
                w.records.append(rec)
            
            w._shapes.extend(r.shapes())
            w.save(outputSHP)
            
    except:
        logger.critical("[While adding field to shape file.]"  + sys.exc_info()[0])
        
def summarizeJSON(communeID, sourceJSONFile):
    #This function analyses the JSON file
    #changes to the JSON or output requirements will require edits to this function.
    try:
        logger.info("[Beginning analysis of JSON file.]")
        communeData = json.load(open(sourceJSONFile))
        
        villageCounter = 0
        totalHouseholdsInVillage = 0
        totalPoor1Households = 0
        totalPoor1Poor2Households = 0
        totalPoor2Households = 0 
        for village in communeData:   
            villageCounter += 1
            totalHouseholdsInVillage = (totalHouseholdsInVillage + int(village["HouseholdsInVillage"]))
            totalPoor1Households = (totalPoor1Households + int(village["Poor1Households"]))
            totalPoor1Poor2Households = (totalPoor1Poor2Households + int(village["Poor1Poor2Households"]))
            totalPoor2Households = (totalPoor2Households + int(village["Poor2Households"]))
        
        logger.info("[IDPOOR Commune Stats - [Commune File: " + sourceJSONFile + "], [Villages: " + str(villageCounter) + "], [Total Households: " + str(totalHouseholdsInVillage) + "], [Poor1 Households: " + str(totalPoor1Households) + "], [Poor1Poor2 Households: " + str(totalPoor1Poor2Households) + "], [Poor2 Households: " + str(totalPoor2Households) + "]].")
        
        #***********************************************************************************
        # User Parameters (2 of 2)********************************************************
        # The third function parameter (an integer) reflects the index position of the field
        # as it should appear in the shapefile. This is the target field location
        # for summarized data.
        populateFieldShapeFile(communeID,outputSHP,9,totalHouseholdsInVillage)
        populateFieldShapeFile(communeID,outputSHP,10,villageCounter)
        populateFieldShapeFile(communeID,outputSHP,11,totalPoor1Households)
        populateFieldShapeFile(communeID,outputSHP,12,totalPoor1Poor2Households)
        populateFieldShapeFile(communeID,outputSHP,13,totalPoor2Households)
        # End User Parameters (2 of 2)***************************************************
        #**********************************************************************************
    except:
        logger.critical("[Error during summarizeJSON call.] " + sys.exc_info()[0])
        
def populateFieldShapeFile(communeID,targetShapeFile,targetFieldIndex,value):
    #This function modifies the spatial .shp file.
    #Adds JSON response info to attributes.
    #Matches with commune ID at index 6
    #INPUTS: Commune ID, Value to Update with.
    try:
        logger.info("[Populating shape file with Commune Statistics.]")
        e = shapefile.Editor(targetShapeFile)
        for i in range(len(e.records)):
            if(str(e.records[i][6])==str(communeID)):
                e.records[i][targetFieldIndex]=value
                logger.info("[Edited Commune [" + str(communeID) + "] with value [" + str(value) + "]]")
        e.save(targetShapeFile)
       
    except:
        logger.critical("[Error while populating data to shapefile.] " + sys.exc_info()[0])

def cleanupWorkArea():
    #Perform a cleanup of the working directory
    #archive used json files.
    logger.info("[Cleaning up working directory.]")
    try:
        if not os.path.exists(archiveDirectory + "/"):
            os.makedirs("." + archiveDirectory + "/")
        if not os.path.exists(sourceDirectory + "/"):
            os.makedirs("." + sourceDirectory + "/")
    except:
        logger.critical("[Error while creating archive or source directory.]")
    
    try:
        arr_txt = [x for x in os.listdir() if x.endswith(".json")]
        for fileitems in arr_txt:
            shutil.move(fileitems, archiveDirectory + "/" + fileitems)
    except:
        logger.critical("[Error while archiving file.]")
        
    logger.info("[Cleanup complete.]")
        

if __name__ == "__main__":
    main()


   
