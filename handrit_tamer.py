# -*- coding: utf-8 -*-
"""handrit-tamer.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FJ3NnnLSjl68YzTQhFWD6sz_WQZ7zTNv
"""

#import libraries
import requests
import lxml
from bs4 import BeautifulSoup
import urllib
import pandas as pd
import time
import statistics
import crawler
from metadata import get_all_data as maddyData

"""# Result URL to list of shelfmarks


"""

def efnisordResult(inURL):
  resultPage = requests.get(inURL).content
  pho = BeautifulSoup(resultPage, 'lxml')
  theGoods = pho.find('tbody')
  identifierSoup = theGoods.find_all(class_='id')
  identifierList = []
  for indi in identifierSoup:
    identifier = indi.get_text()
    identifierList.append(identifier)
  return identifierList

def leitaResult(inURL):
  # -> unused
  resultPage0 = requests.get(inURL).content
  resultPagesList = []
  resultPagesList = resultPagesList.append(inURL)
  soup = BeautifulSoup(resultPage0, 'lxml')
  pagesSoup = soup.find(class_="t-data-grid-pager")
  print(pagesSoup)
  linksToPages = pagesSoup.find_all('a')
  for link in linksToPages:
    pageURL = link.get('href')
    print(pageURL)
    resultPagesList = resultPagesList.append(pageURL)
  return resultPagesList

# startURL = input("Feed me!")

# listOfIdentifiers = leitaResult(startURL)
# print(listOfIdentifiers)

"""## Parse search results

get a list of shelfmarks from a search result url
"""

from bs4 import BeautifulSoup
import requests
import lxml

def get_shelfmarks(url):
    """Get Shelfmarks from an URL

    This function returns a list of strings containing shelfmarks from a page on handrit.is.

    Args:
        url (str): a URL to a search result page on handrit.is

    Returns:
        List[str]: A list of Shelfmarks
    """
    htm = requests.get(url).text
    soup = BeautifulSoup(htm, 'lxml')
    subsoups = soup.select("td.shelfmark")
    print(subsoups)
    shelfmarks = [ss.get_text() for ss in subsoups]
    shelfmarks = [sm.strip() for sm in shelfmarks]
    print(f"At 'get_shelfmarks', I still have {len(shelfmarks)}, and these are:")
    print(shelfmarks)
    return shelfmarks
  

def get_search_result_pages(url):
    """Get multiple result pages from search with 26+ hits.

    This function returns a list of all result pages from one search result,
    if the search got too many hits to display on one page.

    Args:
        url (str): URL to a multi page search result

    Returns:
        List[str]: a list with URLs for all pages of the search result
    """
    res = [url]
    htm = requests.get(url).text
    soup = BeautifulSoup(htm, 'lxml')
    links = soup.select("div.t-data-grid-pager > a")
    urls = [l['href'] for l in links]
    for u in urls:
      if u not in res:
        res.append(u)
    return res


def get_shelfmarks_from_urls(urls): # -> somethings fucky
  results = []
  if len(urls) == 1:
    url = urls[0]
    results += get_shelfmarks(url)
    return list(set(results))
  for url in urls:
    results += get_shelfmarks(url)
    time.sleep(0.5)
  return list(set(results))

"""#Shelfmarks to URLs

##Shelfmark to ID
"""

def splitshelfmark(shelfmark):
  #splits shelfmark into collection and rest
  varcollection, rest = shelfmark.split(" ", 1)
  #replaces Í with I in the collection if there are any
  try:
    varcollection = varcollection.replace("Í", "I")
  except Exception:
    pass
  #splits the rest of the shelfmark into middlebit (letter and Number) and format
  try:
    middlebit, varformat = rest.rsplit(" ", 1)
  except:
    print(rest)
    middlebit = rest
    varformat = ""
  #tries to split the middlebit into letter and number (only possible if there's a letter)
  try:
    varnumber, varletter = middlebit.split(" ", 1)
    varletter = varletter.replace(" ", "-")
    varnumber2 = varnumber.zfill(3)
    varnumber = varnumber.zfill(4)
    return varcollection, varnumber, varformat, varletter, varnumber2
  except Exception:
    pass
  #reassign variables if it's a fragment
  if middlebit == "Fragm":
      varnumber = middlebit
      varnumber2 = varformat.zfill(3)
      varnumber = varformat.zfill(4)
      del varformat
      varformat = "fragm"
  else:
      varnumber2 = middlebit.zfill(3)
      varnumber = middlebit.zfill(4)
  return varcollection, varnumber, varformat, "", varnumber2

#turns format into the number used in the url
def formattonumber(varformat):
  if varformat == "fol.":
    formatnumber = "02"
    return formatnumber
  if varformat == "4to":
    formatnumber = "04"
    return formatnumber
  if varformat == "8vo":
    formatnumber = "08"
    return formatnumber
  if varformat == "12mo":
    formatnumber = "12"
    return formatnumber
  if varformat == "fragm":
    formatnumber = "Fragm"
    return formatnumber

#creates two possible ids, with and without letter
def createid(formatnumber, varcollection, varletter, varnumber, varnumber2):
  if varcollection is None \
      or formatnumber is None \
      or varnumber is None \
      or varnumber2 is None:
    return "", "", "", ""
  try:
    id1 = varcollection+formatnumber+"-"+varnumber+varletter
    id2 = varcollection+formatnumber+"-"+varnumber+"-"+varletter
    id3 = varcollection+formatnumber+"-"+varnumber2+varletter
    id4 = varcollection+formatnumber+"-"+varnumber2+"-"+varletter
  except Exception:
    id1 = varcollection+formatnumber+"-"+varnumber
    id2 = varcollection+formatnumber+"-"+varnumber
    id3 = varcollection+formatnumber+"-"+varnumber2
    id4 = varcollection+formatnumber+"-"+varnumber2
  return id1, id2, id3, id4

"""##Creating and checking URL possibilities"""

#Creating list of possible URLs
def createurl(id1, id2, id3, id4):
  baseurl = "https://handrit.is/is/manuscript/xml/"
  urllist = [
             baseurl+id1+"-is.xml",
             baseurl+id2+"-is.xml",
             baseurl+id3+"-is.xml",
             baseurl+id4+"-is.xml",
             baseurl+id1+"-en.xml",
             baseurl+id2+"-en.xml",
             baseurl+id3+"-en.xml",
             baseurl+id4+"-en.xml",
             baseurl+id1+"-da.xml",
             baseurl+id2+"-da.xml",
             baseurl+id3+"-da.xml",
             baseurl+id4+"-da.xml"
  ]
  return urllist

#Checking whether URLs work, saving all working ones into urllist2
def checkurl(urllist):
  for i in urllist:
    resp = requests.get(i)
    if resp.ok:
      return i
    time.sleep(0.2)

#Choosing the first URL from urllist2 in case there are multiple
# -> not used anymore
def chooseurl(urllist2):
  url = urllist2[0]
  return url

#combines all the functions from splitshelfmark to one working url
def shelfmarktourl(shelfmark):
  varcollection, varnumber, varformat, varletter, varnumber2 = splitshelfmark(shelfmark)
  formatnumber = formattonumber(varformat)
  id1, id2, id3, id4 = createid(formatnumber, varcollection, varletter, varnumber, varnumber2)
  urllist = createurl(id1, id2, id3, id4)
  url = checkurl(urllist)
  if url:
    return url
  else:
    print(f"        Warning: couldn't find {shelfmark}")

#iterates it for every shelfmark in a list (from Sven), returns one working url for each in list urls
def shelfmarkstourls(shelfmarks):
  urls = []
  for i in shelfmarks:
    url = shelfmarktourl(i)
    if url and url not in urls:
      urls.append(url)
      print(f'   {i} \t-> \t{url}')
    time.sleep(0.5)
  return urls

#test
# print(shelfmarkstourls(["AM 666 b 4to", "JS Fragm 12", "ÍB 62 fol."]))

"""#IDs to URLs"""

#Creating list of possible URLs
def id_createurl(id):
  baseurl = "https://handrit.is/is/manuscript/xml/"
  url1 = baseurl+id+"-is.xml"
  url2 = baseurl+id+"-en.xml"
  urllist = [url1, url2]
  return urllist

#Checking whether URLs work, saving all working ones into urllist2
# -> unused
def id_checkurl(urllist):
  urllist2 = []
  for i in urllist:
    resp = requests.get(i)
    if resp.ok:
      urllist2.append(i)
  return urllist2

#Choosing the first URL from urllist2 in case there are multiple
# -> unused
def id_chooseurl(urllist2):
  url = urllist2[0]
  return url

#combines all the functions from creating url to one working url
def idtourl(id):
  urllist = id_createurl(id)
  url = checkurl(urllist)
  if url:
    return url
  else:
    print(f"        Warning: couldn't find {id}")
  # urllist2 = id_checkurl(urllist)
  # url = id_chooseurl(urllist2)
  # return url

#iterates it for every id in a list (from Sven), returns one working url for each in list urls
def idstourls(ids):
  urls = []
  for i in ids:
    url = idtourl(i)
    if url not in urls:
      urls.append(url)
      print(f'   {i} \t-> \t{url}')
    time.sleep(0.5)
  return urls

#test
# print(idstourls(["AM04-0007", "AM04-0970-VII", "IB04-0324"]))

"""# Section: XML Parser

Maddy: URL-Liste => Dataframe mit Textinfo
"""

def get_xml(urls):
  res = []
  for i in range(len(urls)):
    myURL = urls[i]
    if not myURL:
      continue
    sauce = urllib.request.urlopen(myURL).read()
    soup = BeautifulSoup(sauce, "xml")
    res.append(soup)
    time.sleep(0.5)
    perc = (i + 1) / len(urls) * 100
    print(f'    Parsed XML {i + 1} of {len(urls)} ({perc}%)')
  return res
 

def get_mstexts(soups):
  handritID = []
  handritList = []
  textmatrix = []
   
  # Finds handritID for all manuscripts and the titles of texts they contain
  for soup in soups:
    # Finds handritID for labelling the column
    tag = soup.msDesc
    try:
      handritID = str(tag['xml:id'])
      handritID = handritID[0:-3]
    except:
      handritID = 'N/A'
    handritList.append(handritID)
  
      

    titlelist = []
    title = []
    alltitles = []
    danishtitles = []

    # Removes "summary" and "head" because they also contain "titles" ('sögubók' for example)
    for summary in soup("summary"):
        summary.decompose()
    
    for head in soup("head"):
        head.decompose()

    for titleStmt in soup("titleStmt"):
        titleStmt.decompose()

    # There, we noticed that sometimes the tag title is used even though it shoudn't
    for surrogates in soup("surrogates"):
        surrogates.decompose()

    # Cuts additional info, sometimes there are titles mentioned too that are not part of the ms ANYMORE (but maybe were)
    for accMat in soup("accMat"):
        accMat.decompose()



    # Finds all text titles (type:uniform - if list empty type:supplied)

    alltitles = soup.find_all("title", {"type":"uniform"})
    if len(alltitles)==0:
      alltitles = soup.find_all("title", {"type":"supplied"})
      if len(alltitles)==0:
        alltitles = soup.find_all("title")
    

    # Gets rid of dublettes (only if title type=uniform, not if type=supplied ?!)
    else:
      # Are there Danish titles? (xml:lang:da)
      danishtitles = soup.find_all("title", {"type":"uniform", "xml:lang":"da"})

      # Yes: Lets get rid of them! (Assuming that the remaining texts are xml:lang:non)
      if len(danishtitles)> 0:
        alltitles = soup.find_all("title", {"type":"uniform", "xml:lang":"non"})

    # Puts text titles into a list
    for title in alltitles:

      # element.tag => string
      title = title.get_text()

      # string => list
      titlelist.insert(len(title), title)

    # Adds text lists into a list (=matrix)
    textmatrix.append(titlelist)
    
   
  # Creates DataFrame (inserts 'list of lists of texts' [textmatrix] into DataFrame and adds column labels)
  data = []
  data = pd.DataFrame (textmatrix).transpose()
  data.columns = [handritList]

  #print(data)
  return data

# Obs! You cannot open this file directly in Excel but import it there (encoding utf-8)    
def CSVExport(FileName, DataFrame):
    DataFrame.to_csv(FileName+".csv", encoding='utf-8')
    print("File exported")
    return


# Hier müsse noch die Funktion von Eline kommen, wie aus ner Signatur eine URL (myURL) werden kann
myURLList = ["https://handrit.is/is/manuscript/xml/AM04-0576a-is.xml",
"https://handrit.is/is/manuscript/xml/IB04-0076-is.xml",
"https://handrit.is/is/manuscript/xml/AM02-0123-is.xml",
"https://handrit.is/is/manuscript/xml/IB04-0076-is.xml",
"https://handrit.is/is/manuscript/xml/AM02-0130-is.xml",
"https://handrit.is/is/manuscript/xml/AM02-0162E-is.xml",
"https://handrit.is/is/manuscript/xml/AM04-0446-is.xml",
"https://handrit.is/is/manuscript/xml/Lbs08-0520-is.xml"]

# resultingDataframe = get_mstexts(myURLList)
# print(resultingDataframe)
# CSVExport("Test", resultingDataframe)

"""Maddy: URL-Liste => Dataframe zu Manuskriptinfo"""

def get_msinfo(soups):

  handritID = []
  signature = []
  country = []
  settlement = []
  repository = []
  date = []
  noteBefore = []
  notAfter = []
  when = []
  meandate = []
  yearrange = []

  data = []
  data = pd.DataFrame(columns=['Handrit ID', 'Signature', 'Country',
                               'Settlement', 'Repository', 'Original Date', "Mean Date", "Range"])

  for soup in soups: 

    #handrit-ID finder
    tag = soup.msDesc
    try:
      handritID = str(tag['xml:id'])
      handritID = handritID[0:-3]
    except:
      handritID = 'N/A'
    
    #msIdentifier finder
    try:
      msID = soup.find("msIdentifier")
    except:
      msID = 'N/A'

    #msDetails finder
    if msID == 'N/A':
      country = 'N/A'
      settlement = 'N/A'
      repository = 'N/A'
      signature = 'N/A'
    try:
      country = msID.find("country")
      settlement = msID.find("settlement")
      repository = msID.find("repository")
      signature = msID.find("idno")
      country = country.get_text()
      settlement = settlement.get_text()
      repository = repository.get_text()
      signature = signature.get_text()
    except:
      msID == 'N/A'
      country = 'N/A'
      settlement = 'N/A'
      repository = 'N/A'
      signature = 'N/A'  


    
    #Original date: information rather in tag classes than as texts in tags!
    #Sometimes not before/not after, sometimes when
    tag = soup.origDate
    date = "" 
    ta = 0
    tp = 0
    meandate = 0
    yearrange = 0
    if tag:
      if tag.get('notBefore') and tag.get('notAfter'):
        notBefore = str(tag['notBefore'])
        notAfter = str(tag['notAfter'])

        # Snibbel Snibbel
        if len(notBefore) >= 5 :
          notBefore = notBefore[0:4]

        if len(notAfter) >= 5 :
          notAfter = notAfter[0:4]
        # Snibbel Snibbel Ende

        date = str(notBefore + "-" + notAfter)
        tp = int(notBefore)
        ta = int(notAfter)
        meandate = int(statistics.mean([int(tp), int(ta)]))
        yearrange = int(ta)-int(tp)
        
      elif tag.get('when'):
        date = str(tag['when'])
        tp = int(date)
        ta = int(date)
        meandate = int(statistics.mean([int(tp), int(ta)]))
        yearrange = int(ta)-int(tp)

      elif tag.get('from') and tag.get('to'):
        fr = str(tag['from'])
        to = str(tag['to'])
        date = str(fr + "-" + to)
        tp = int(fr)
        ta = int(to)
        meandate = int(statistics.mean([int(tp), int(ta)]))
        yearrange = int(ta)-int(tp)


    #make plain text
    

    data = data.append({'Handrit ID': handritID, 'Signature' : signature,
                        'Country' : country,
                        'Settlement' : settlement,
                        'Repository' : repository,
                        'Original Date' : date,
                        'Terminus Postquem' : tp,
                        'Terminus Antequem' : ta,
                        'Mean Date' : meandate,
                        'Range' : yearrange}, 
                       ignore_index=True)
 

  return data

def get_id_from_shelfmark_local(shelfmarks: list) -> list:
  _shelfmark_path = 'data/ms_shelfmarks.csv'
  shelfIDPD = pd.read_csv(_shelfmark_path)
  shelfIDPD = shelfIDPD[shelfIDPD['shelfmark'].isin(shelfmarks)]
  idList = shelfIDPD['id'].tolist()
  return idList


# Hier müsse noch die Funktion von Eline kommen, wie aus ner Signatur eine URL (myURL) werden kann
# myURLList = ["https://handrit.is/is/manuscript/xml/JS08-0407-is.xml", "https://handrit.is/is/manuscript/xml/AM04-0666-a-en.xml",  "https://handrit.is/is/manuscript/xml/IB04-0070-is.xml", "https://handrit.is/is/manuscript/xml/AM04-0666-b-da.xml"]

# resultingDataframe = get_msinfo(myURLList)

"""Combine it all"""

def get_data_from_browse_url(url: str, DataType: str):
  '''Get the desired data from a handrit browse URL.
    The data frame to be returned depends on the DataType variable (cf. below).
    If DataType = Contents:
        Data frame columns will be the shelfmarks/IDs of the MSs, each column containing the text
        witnesses listed in the MS description/XML.

    If DataType = Metadata:
        Data frame contains the following columns:
        ['Handrit ID', 'Signature', 'Country',
                                'Settlement', 'Repository', 'Original Date', 'Mean Date', 'Range']
    
  Args:
      inURL(str, required): A URL pointing to a handrit browse result page.
      DataType(str, required): Whether you want to extract the contents of MSs from the XMLs or metadata
      such as datings and repository etc. (cf. above). Can be 'Contents' or 'Metadata'

  Returns:
      pd.DataFrame: DataFrame containing MS contents or meta data.
  '''
  ids = efnisordResult(url)
  print(f'Got {len(ids)} IDs.')
  if DataType == "Maditadata":
    data = maddyData(inData=ids, DataType='ids')
    return data
  xmls = []
  for i in ids:
    xml = crawler.load_xmls_by_id(i)
    xmlList = list(xml.values())
    for x in xmlList:
      xmls.append(x)
  if DataType == "Contents":
    data = get_mstexts(xmls)
  if DataType == "Metadata":
    data = get_msinfo(xmls)
  return data

def get_data_from_search_url(url: str, DataType: str):
  '''This will get the requested data from the corresponding XML files and return it as a data frame.
  
  The data frame to be returned depends on the DataType variable (cf. below).
    If DataType = Contents:
        Data frame columns will be the shelfmarks/IDs of the MSs, each column containing the text
        witnesses listed in the MS description/XML.

    If DataType = Metadata:
        Data frame contains the following columns:
        ['Handrit ID', 'Signature', 'Country',
                               'Settlement', 'Repository', 'Original Date', 'Mean Date', 'Range']
    
  Args:
      inURL(str, required): A URL pointing to a handrit search result page.
      DataType(str, required): Whether you want to extract the contents of MSs from the XMLs or metadata
      such as datings and repository etc. (cf. above). Can be 'Contents' or 'Metadata'

  Returns:
      pd.DataFrame: DataFrame containing MS contents or meta data.
  '''
  pages = get_search_result_pages(url)
  print(f'Got {len(pages)} pages.')
  shelfmarks = get_shelfmarks_from_urls(pages)
  print(f'Got {len(shelfmarks)} shelfmarks.')
  print(shelfmarks)
  ids = get_id_from_shelfmark_local(shelfmarks)
  if DataType == "Maditadata":
    data = maddyData(inData=ids, DataType='ids')
    return data
  xmls = []
  for i in ids:
    xml = crawler.load_xmls_by_id(i)
    xmlList = list(xml.values())
    for x in xmlList:
      xmls.append(x)
  print(f'Got {len(xmls)} XML files')
  if DataType == "Contents": 
    data = get_mstexts(xmls)
  if DataType == "Metadata":
    data = get_msinfo(xmls)
  return data


def get_from_search_list(inURLs: list, DataType: str, joinMode: str):
  '''This will get the requested data from the corresponding XML files and return it as a data frame.
  
  The data frame to be returned depends on the DataType variable (cf. below).
    If DataType = Contents:
        Data frame columns will be the shelfmarks/IDs of the MSs, each column containing the text
        witnesses listed in the MS description/XML.

    If DataType = Metadata:
        Data frame contains the following columns:
        ['Handrit ID', 'Signature', 'Country',
                               'Settlement', 'Repository', 'Original Date', 'Mean Date', 'Range']
    
  Args:
      inURLs(list, required): A URL pointing to a handrit search result page.
      DataType(str, required): Whether you want to extract the contents of MSs from the XMLs or metadata
        such as datings and repository etc. (cf. above). Can be 'Contents' or 'Metadata'
      joinMode(str, required): Whether you want all info or only those that occur in the results of all
        search URLs passed as input. If 'shared' returns empty, it means there is no overlap.
        Set 'All' if you want to return all MSs and their data (duplicates will be removed).
        Set 'Shared' if you only want the MSs occuring in all search result URLs.

  Returns:
      pd.DataFrame: DataFrame containing MS contents or meta data.
  '''
  listList = []
  for url in inURLs:
    pages = get_search_result_pages(url)
    print(f'Got {len(pages)} pages.')
    shelfmarks = get_shelfmarks_from_urls(pages)
    listList.append(shelfmarks)
  if joinMode == 'Shared':
    finalMSs = list(set.intersection(*map(set, listList)))
  if joinMode == 'All':
    allTheStuff = [i for x in listList for i in x]
    finalMSs = list(set(allTheStuff))
  ids = get_id_from_shelfmark_local(finalMSs)
  xmls = []
  if DataType == "Maditadata":
    data = maddyData(inData=ids, DataType='ids')
    return data
  for i in ids:
    xml = crawler.load_xmls_by_id(i)
    xmlList = list(xml.values())
    for x in xmlList:
      xmls.append(x)
  print(f'Got {len(xmls)} XML files')
  if DataType == "Contents":
    data = get_mstexts(xmls)
  if DataType == "Metadata":
    data = get_msinfo(xmls)
  return data


"""Do the Magic

To be able to run the program, all code blocks before this text need to be run once to initialize everything.  
Simply click in this text and then hit "Runtime" > "Run before" in the menu on top.

The program can handle two kinds of input: 
A URL from the "browse" function on handrit.is 
or a URL from a search result.  
Note that search results will automatically get all the sub-pages, 
while in the browse url you should click "sýna allt" first.

The simplest way to use the program is to take advantage 
of the convenience functions `get_data_from_browse_url()`
and `get_data_from_search_url()` as shown below.

To do more sophisticated analyses like combining results,
or to keep things faster, you can also implement the steps of these functions manually, and work with the data inbetween, as is shown too.

In any case, you will get a `DataFrame` back, which can be exported, using `CSVExport()` (see example). After doing so, you will see the file if you click on the "Files" tab at the very left of the page (the folder symbol).  
Download this file and import it in Excel (encoding must be `utf-8`) to do further analysis with the data.

## Browse

The following code retrieves and analyzes the XMLs from one browsing category.

Explanation:
- `browse_sample = "..."` assigns a URL to a variable
- `data = get_data_from_browse_url(browse_sample)` gets the data fom said URL and stores it in a variable called `data`
- `print(data)` displays the data
- `CSVExport("Browse_results", data)` exports the data to a file called `Browse_results.csv`
"""

# Browse

# browse_sample = "https://handrit.is/is/manuscript/list/keyword/skalds?showall.browser=1"
# browse_sample = "https://handrit.is/is/manuscript/list/keyword/bok"
# browse_sample = "https://handrit.is/is/manuscript/list/keyword/lestur"
# browse_sample = "https://handrit.is/en/manuscript/list/keyword/timat"
# browse_sample = "https://handrit.is/en/manuscript/list/keyword/lit"

# data = get_data_from_browse_url(browse_sample)

# print(data)
# CSVExport("Browse_results", data)

# """## Search

# The following code retrieves and analyzes the XMLs from one search result.  
# It works just like the browse code.
# """

# # Search

# # search_sample = "https://handrit.is/en/search/results/WWbmHV"
# # search_sample = "https://handrit.is/en/search/results/BzDSqt"
# # search_sample = "https://handrit.is/en/search/results/CR9fkh"
# # search_sample = "https://handrit.is/is/search/results/hsWTp2"
# search_sample = "https://handrit.is/en/search/results/Wwf4t3"

# data = get_data_from_search_url(search_sample, DataType="Contents")

# print(data)
# CSVExport("Search_results", data)

# """## Advanced

# The following code blocks do some manual work, which allows more refined analysis more quickly.

# In the first code block we combine the shelfmarks of Landnámabók and Íslendingabók manuscripts.
# """

# # Search results of Landnámabók and Íslendingabók
# landnama = "https://handrit.is/is/search/results/fgq5G8"
# islendinga = "https://handrit.is/is/search/results/RmNlh3"
# pages = get_search_result_pages(landnama)
# shelfmarks_lnb = get_shelfmarks_from_urls(pages)
# pages = get_search_result_pages(islendinga)
# shelfmarks_ib = get_shelfmarks_from_urls(pages)

# # combine the shelfmarks
# shelfmarks_combined = shelfmarks_lnb + shelfmarks_ib

# # ensure each shelfmark only appears once
# shelfmarks_combined = list(set(shelfmarks_combined))

# print(f'Number of shelfmarks: {len(shelfmarks_combined)}')

# """If we run the code, in the next block, `shelfmarks_combined` will still be available.

# If we were to change something in the next block, we wouldn't have to re-run the first block.


# """

# urls = shelfmarkstourls(shelfmarks_combined)
# xmls_combined = get_xml(urls)
# print(f'Number of XML files loaded: {len(xmls_combined)}')

# """Finally, we can do all sorts of things with the XML, without having to reload it each time."""

# data = get_mstexts(xmls_combined)
# print(data)
# CSVExport("lnb_ib_combined_texts", data)
# data = get_msinfo(xmls_combined)
# print(data)
# CSVExport("lnb_ib_combined_metadata", data)

# """E.g. we can get only the manuscripts that are dated"""

# dated_data = data[data['Original Date'] != '']
# print(dated_data)
# CSVExport("lnb_ib_combined_metadata_dated", dated_data)
# dates = dated_data[['Original Date', 'Terminus Antequem', 'Terminus Postquem']]
# print(dates)

# """We can even plot data"""

# dates['Terminus Antequem'].plot.hist(bins=60)

# dates['Terminus Antequem'].plot.hist(bins=60)
# dates['Terminus Postquem'].plot.hist(bins=60)

# dates[['Terminus Postquem', 'Terminus Antequem']].plot.hist(bins=60, alpha=0.5)

# Test
# ----

# inList = ['https://handrit.is/en/search/results/L0tPvR', 'https://handrit.is/en/search/results/1HdG84']
# data = get_from_search_list(inList, "Contents")
# print(data)