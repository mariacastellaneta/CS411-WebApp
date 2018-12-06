import requests
import json
import pprint
import pandas as pd
import random
# from .models import Show
import spotipy
from spotipy import oauth2
from constants import *
import datetime 
import time
def getEventBrite(artist,location):
    
    show = Show.objects.filter(artist__contains=artist.lower(), city__contains=location.lower()).first() 
    if show is not None:
        results = {}
        results['name'] = show.display_artist
        results['address'] = show.location
        results['city'] = show.display_city
        results['zipcode']= show.zipcode
        results['start'] = show.start_time
        results['descript'] = show.description
    else:
        input_city = str(location)
        key = 'ZN6GPC6WGYLKI7IAZSUW' # Brooke's authentication key
        categories = 'music' 
        keywords = str(artist)

        results = {}
        response = requests.get("https://www.eventbriteapi.com/v3/events/search/?location.address="+ input_city +"&expand=organizer,venue,category&q="+keywords+"&categories=103&token=" + key)
        if (response.json()['events']==[]):
            return []
            
        results['name'] = response.json()['events'][0]['name']['text']
        results['address'] = response.json()['events'][0]['venue']['address']['address_1']
        results['city'] = response.json()['events'][0]['venue']['address']['city']
        results['zipcode'] = response.json()['events'][0]['venue']['address']['postal_code']
        results['start'] = response.json()['events'][0]['start']['local']
        results['descript'] = response.json()['events'][0]['description']['text']

        # this is how you create a new entrey in the "SHOW" database
        newShow = Show(artist = results['name'].lower(),city = results['city'].lower(),display_artist=results['name'],display_city=results['city'],start_time = results['start'],description=results['descript'],zipcode = results['zipcode'])
        newShow.save()
        
    return results


# def getTicketMaster(artist,location):
#     endpoint = "https://app.ticketmaster.com/discovery/v2/events.json?keyword="+artist+"&city="+location+"&apikey=O5RiEgAQZrTztqWOwSDjfvCB1jqwm1zj"
#     response = requests.get(endpoint).json()

#     if response['page']['totalElements']==0:
#         return []
#     results = {}
#     results['name']=response['_embedded']['events'][0]['name']
#     results['url']=response['_embedded']['events'][0]['url']
#     results['date']=response['_embedded']['events'][0]['dates']['start']['localDate']
#     results['start']=response['_embedded']['events'][0]['dates']['start']['localTime']
#     results['info']=response['_embedded']['events'][0]['info']

    

def getArtists(bearer):
    #gets users top 8 artists from spotify api, bearer represents access_token from oauth, and returns their image urls.
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {'content-type': 'application/json', 'Accept': 'application/json',"Authorization":"Authorization: Bearer "+bearer}
    r = requests.get(url, headers=headers,params={'limit':50})
    jsonn=r.json()
    artists=jsonn['items']

    # artistNames = [a['name'] for a in artists]
    artistNames = ['+'.join(a['name'].split()) for a in artists]
    artistImages= []
    for a in artists:
        try:
            img = a['images'][0]['url']
        except:
            img = ''
        artistImages.append(img)
    artistIds = [a['id'] for a in artists]

    
    return artistNames[0:8],artistImages[0:8],artistIds
    # return artistNames,artistIds

def similarArtists(artistIds,bearer):
    #not used now
    similarArtists = []
    similarArtistImg = []
    for idd in artistIds:
        url="https://api.spotify.com/v1/artists/"+str(idd)+"/related-artists"
        headers={"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Authorization: Bearer "+bearer}

        r2 = requests.get(url,headers=headers,params={'limit':1})
        
        simArtists = r2.json()['artists']
        names = ['+'.join(a['name'].split()) for a in simArtists]
        # for i in range(3):
        #     try:
        #         img = simArtists[i]['images'][0]['url']
        #     except:
        #         img = ''
        #     similarArtistImg.append(img)
        # try:
            # names = names[0:3]

        similarArtists+=names
        # except:
        #     continue
        

    # random.shuffle(similarArtistImg)
    
    # return similarArtistImg[0:12], similarArtists[0:12]
    return similarArtists[0:50]


def renderRecs(recArtistsImg,recArtistsNames): 
    #recArtistsImg is the link to the image source, recArtistsNames allows for the routing to the correct url
    allDiv = ""
    for i in range(len(recArtistsImg)):
        
        allDiv += """
        <div class="col-lg-3 col-md-4 col-xs-6">
            <a href="/showinfo/%s/" class="d-block mb-4 h-100">
                <img class="img-fluid img-thumbnail" src="%s" alt="">
            </a>
        </div>
        """%(recArtistsNames[i],recArtistsImg[i])

    return allDiv #formats the HTML to fit into the template



def getTicketMaster():
    #hard coded for now
    results = {}
    urls = []
    foundArtists=[]

    #ticketmaster endpoint to find 25 shows in area (hard coded for boston right now) based on genreID (hard coded for dance/electronic right now)
    url = 'https://app.ticketmaster.com/discovery/v2/events.json?size=21&genreId=KnvZfZ7vAvF&segmentId=KZFzniwnSyZfZ7v7nJ&city=boston&apikey=O5RiEgAQZrTztqWOwSDjfvCB1jqwm1zj'
    r = requests.get(url).json()
    for i in range(len(r['_embedded']['events'])): #iterate over all the 25 returned shows and parse thru the json accordingly. 
        payload = {}

        payload['eventname'] = r['_embedded']['events'][i]['name']#r['_embedded']['events'][0]['name']
        curArtist = '+'.join(payload['eventname'].split(' '))

        if curArtist in results:
            continue

        foundArtists.append('+'.join(payload['eventname'].split(' ')))

        
        payload['url'] =r['_embedded']['events'][i]['url']#r['_embedded']['events'][0]['url']
        
        payload['venueAddr'] = r['_embedded']['events'][i]['_embedded']['venues'][0]['address']['line1']
        
        payload['venueName'] =  r['_embedded']['events'][i]['_embedded']['venues'][0]['name']
        
        payload['venueLat'] = r['_embedded']['events'][i]['_embedded']['venues'][0]['location']['latitude']
        
        payload['venueLng'] = r['_embedded']['events'][i]['_embedded']['venues'][0]['location']['longitude']
        
        iMax = 0 
        finalI = -1
        for j in range(len(r['_embedded']['events'][i]['images'])):
            nMax = r['_embedded']['events'][i]['images'][j]['height']*r['_embedded']['events'][i]['images'][j]['width']
            if nMax > iMax:
                iMax = nMax
                finalI = j
        payload['imgUrl'] = r['_embedded']['events'][i]['images'][finalI]['url']
        
        urls.append(payload['imgUrl'])
        
        date=datetime.datetime.strptime(r['_embedded']['events'][i]['dates']['start']['localDate']+'T'+r['_embedded']['events'][0]['dates']['start']['localTime'], '%Y-%m-%dT%H:%M:%S')
        payload['datetime'] =datetime.datetime.strftime(date, '%m/%d/%Y at %H:%M')

        
        try:
            payload['info']=r['_embedded']['events'][i]['info']
        except:
            pass

        #this is hard to visualize - the results dictionary is a dictionary of dictionaries (yikes), but allows data to be upfront
        #loaded rather than having to call the api again once we click a page. so for example if a kanye show is found then
        # results['Kanye'] holds a dictionary of all the information defined above.
        results[curArtist] = payload

    return results,urls,foundArtists #urls and found artists are arrays holding links and names, which allows for html rendering and URL routing
