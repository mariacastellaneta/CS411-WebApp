import requests
import json
import pprint
import pandas as pd
import random
# from .models import Show
import spotipy
from spotipy import oauth2


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


def getTicketMaster(artist,location):
    endpoint = "https://app.ticketmaster.com/discovery/v2/events.json?keyword="+artist+"&city="+location+"&apikey=O5RiEgAQZrTztqWOwSDjfvCB1jqwm1zj"
    response = requests.get(endpoint).json()

    if response['page']['totalElements']==0:
        return []
    results = {}
    results['name']=response['_embedded']['events'][0]['name']
    results['url']=response['_embedded']['events'][0]['url']
    results['date']=response['_embedded']['events'][0]['dates']['start']['localDate']
    results['start']=response['_embedded']['events'][0]['dates']['start']['localTime']
    results['info']=response['_embedded']['events'][0]['info']

    

def getArtists(bearer):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {'content-type': 'application/json', 'Accept': 'application/json',"Authorization":"Authorization: Bearer "+bearer}
    r = requests.get(url, headers=headers,params={'limit':50})
    jsonn=r.json()
    artists=jsonn['items']

    artistNames = [a['name'] for a in artists]
    artistImages= []
    for a in artists:
        try:
            img = a['images'][0]['url']
        except:
            img = ''
        artistImages.append(img)
    artistIds = [a['id'] for a in artists]

    
    return artistNames[0:8],artistImages[0:8],artistIds

def similarArtists(artistIds,bearer):

    similarArtists = []
    similarArtistImg = []
    for idd in artistIds:
        url="https://api.spotify.com/v1/artists/"+str(idd)+"/related-artists"
        headers={"Accept": "application/json", "Content-Type": "application/json", "Authorization": "Authorization: Bearer "+bearer}

        r2 = requests.get(url,headers=headers,params={'limit':1})
        
        simArtists = r2.json()['artists']
        names = [a['external_urls']['spotify'] for a in simArtists]
        for i in range(3):
            try:
                img = simArtists[i]['images'][0]['url']
            except:
                img = ''
            similarArtistImg.append(img)
        try:
            names = names[0:3]
            # similarArtists+= ['+'.join(a.split(' ')) for a in names]
            similarArtists+=names
        except:
            continue
        

    # random.shuffle(similarArtistImg)
    
    return similarArtistImg[0:12], similarArtists[0:12]

def renderRecs(recArtistsImg,recArtistsLink):
    # recArtistsImg,recArtistsLink = similarArtists()
    allDiv = ""
    for i in range(len(recArtistsImg)):
        
        allDiv += """
        <div class="col-lg-3 col-md-4 col-xs-6">
            <a href="%s" class="d-block mb-4 h-100">
                <img class="img-fluid img-thumbnail" src="%s" alt="">
            </a>
        </div>
        """%(recArtistsLink[i],recArtistsImg[i])

    return allDiv


    