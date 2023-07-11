from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import simplejson


def init():
    """ Funtion used to get env variables
    """
    load_dotenv()

def pageClawler():
    """ Function responsible for iterating over each page and stoping on last
    """
    url = os.environ['INPUT_URL']
    s = requests.Session()
    #s.proxies = setProxy() #Currently dose not work
    
    finalJson = json.loads("[]")
    
    while url:
        page = s.get(url)
        
        data = parseData(page.content)
        finalJson.extend(data)
        
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find_all('a')
        for element in results:
            url = None
            if element.get_text() == "Next →":
                url = os.environ['INPUT_URL'] + element['href'][12:]
                break
    
    saveData(finalJson)

def parseData(content):
    """Funtion used to proces data 
    """
    regex_pattern = "(?=var data =).+(?=for \(var i in data\))" 
    data = re.findall(regex_pattern, str(content)).pop() #Find data in page content
    data = re.sub(r"\\n\s{0,}"," ",data).replace("\\'","'").replace("\\u201c","").replace("\\u201d","")[11:-2]
    data = re.sub(r"\"\\","\"",data)
    data = re.sub(r"\"\s[}]","\" }",data).replace("\\\"","\"")
    
    data = json.loads(data)
    
    #Delete unused data and create "by" key with data
    for element in data:
        element['by'] = element['author']['name']
        del element['author']
        
    return data

def saveData(finalJson):
    """Used to save data into jsonl file format
    """
    outputFile = open(os.environ['OUTPUT_FILE'], "w")
    outputFile.write(simplejson.dumps(finalJson, indent=4, sort_keys=True))
    outputFile.close()
    
def setProxy():
    proxyServers = {
        'http': os.environ['PROXY'],
        'https': os.environ['PROXY'],
    }
    return proxyServers    
    
    
def main():
    init()
    
    pageClawler()
    

main()