# pages/views.py
from django.views.generic import TemplateView
from spotipy import oauth2
from django.shortcuts import render
import spotipy
from users.models import CustomUser
from . import services
import requests
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = '78f584e7e40c41528f1601d32a27d15c'
SPOTIPY_CLIENT_SECRET = 'b284e94507c34fc6b7f17ac0f0fbaca7'
SPOTIPY_REDIRECT_URI = 'http://127.0.0.1:8000/login/'
SCOPE = 'user-top-read'
CACHE = '.spotipyoauthcache'
sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE )

client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
# class HomePageView(TemplateView):
#     template_name = 'home.html'

def login(request):
    auth_url = sp_oauth.get_authorize_url()
    payload = {'auth_url':auth_url}
    # print(auth_url)
    # return render(request, 'login.html',payload)
    access_token = ""

    # token_info = sp_oauth.get_cached_token()

    # if token_info:
    #     print("Found cached token!")
    #     access_token = token_info['access_token']
      
    code = sp_oauth.parse_response_code(request.get_full_path())
    if code:
        # print("Found Spotify auth code in Request URL! Trying to get valid access token...")
        token_info = sp_oauth.get_access_token(code)
        access_token = token_info['access_token']
        sp = spotipy.Spotify(auth=access_token,client_credentials_manager=client_credentials_manager)
        user = sp.current_user()
        dbUser =CustomUser.objects.filter( spotifyid__contains=user['id'] ).first() 

        #LOTS OF COMMENTED STUFF sorry it represents how i made a ruf attempt at searching every similar artist
        artistNames,artistUrls,artistExtLinks = services.getArtists(access_token) #gets top 8 artists in spotify

        # MyTopArtists, MyTopArtistsId = services.getArtists(access_token)
        # print(MyTopArtists)
        # print()
        # print(MyTopArtistsId)
        # MyTopArtistsEvents, TopArtistImgs, FoundTopNames = services.getTicketMaster(MyTopArtists) #returns dict of dicts -> each key is an artist, each value is payload
        # print(TopArtistImgs)
        # print(MyTopArtistsEvents)
        # if requests.session['Concerts'] is None:
        #     requests.session['Concerts'] = MyTopArtistsEvents
        # else:
        # requests.session['Concerts'].update(MyTopArtistsEvents)


        # SimilarArtistNames = services.similarArtists(MyTopArtistsId,access_token)
        MySimilarArtistEvents,SimArtistsImgs,SimFoundNames = services.getTicketMaster() #gets the ticketmaster suggested artists
        #will eventualy accept the genreIDs to make dynamic.
        # requests.session['SimilarArtistConcerts']=MySimilarArtistEvents
        divs = services.renderRecs(SimArtistsImgs,SimFoundNames)
        
        # MyTopArtistsEvents.update(MySimilarArtistEvents)

        #so the request.session allows data to be accessed between views per session. I store all the events in the 'Concerts' field
        #that i made inthe session, so when i access the /showinfo/ARTIST/ url, it will go in to the request.session['Concerts'][ARTIST] to get 
        #the appropriate payload depending on the artist. saves a lot of loading time. kinda like a caching system to hold the data per session.
    
        request.session['Concerts']=MySimilarArtistEvents


        if dbUser is None:
            print("didn't find it")
            newUser = CustomUser(username = user['display_name'],location = 'Boston',spotifyid=user['id'])
            newUser.save()
            

            #RIGHT NOW HARD CODED TO ASSUME 8 TOP ARTISTS - probably need to make this more general, in the event the user doesn't
            #have 8 top artists? need to investigate what spotify api returns in that event.
            payload = {
                
                'artist1img':artistUrls[0],
                'artist2img':artistUrls[1],
                'artist3img':artistUrls[2],
                'artist4img':artistUrls[3],
                'artist5img':artistUrls[4],
                'artist6img':artistUrls[5],
                'artist7img':artistUrls[6],
                'artist8img':artistUrls[7],

                'topURL1':artistExtLinks[0],
                'topURL2':artistExtLinks[1],
                'topURL3':artistExtLinks[2],
                'topURL4':artistExtLinks[3],
                'topURL5':artistExtLinks[4],
                'topURL6':artistExtLinks[5],
                'topURL7':artistExtLinks[6],
                'topURL8':artistExtLinks[7],

                'user':newUser.username,
                'location':newUser.location,
                'divs':divs
            }
            # request.session['user']=user
            return render(request,'index.html',payload)
        else:

            payload = {
                
                'artist1img':artistUrls[0],
                'artist2img':artistUrls[1],
                'artist3img':artistUrls[2],
                'artist4img':artistUrls[3],
                'artist5img':artistUrls[4],
                'artist6img':artistUrls[5],
                'artist7img':artistUrls[6],
                'artist8img':artistUrls[7],
                'topURL1':artistExtLinks[0],
                'topURL2':artistExtLinks[1],
                'topURL3':artistExtLinks[2],
                'topURL4':artistExtLinks[3],
                'topURL5':artistExtLinks[4],
                'topURL6':artistExtLinks[5],
                'topURL7':artistExtLinks[6],
                'topURL8':artistExtLinks[7],
                'user':dbUser.username,
                'location':dbUser.location,
                'divs':divs
            }

            # print("found dbUser")
            # return render(request,'success.html',{'success':dbUser.spotifyid})
            # request.session['user']=user

            return render(request,'index.html',payload)


    if access_token:
        # print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        results = sp.current_user()
        # print(results)
        return render(request,'success.html')
    
    
    else:
        return render(request,'login.html',payload)

def success(request):
    payload = {'success':request.session['user']}
    return render(request,'success.html',payload)


def showinfo(request,artist):
    
    payload = request.session['Concerts'][artist] #so when i click the show thumbnail - it routes me to something like /showinfo/Drake/
    #then in here artist=Drake, and it will look in my session cache to find the payload for drake, and render the showinfo.html accordingly.
    return render(request,'showinfo.html',payload)