import pickle
import requests
import time
from flask import session, flash
from models import connect_db, db, User


def getToken():
    url = "https://accounts.spotify.com/api/token"

    payload = 'grant_type=client_credentials&client_id=32dcf2a655a84387beb033858c58c4fa&client_secret=8c2e1661ebbf48d4978fed7bc585ee23'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': '__Host-device_id=AQD0pt6oHOfQGGyBUbX5sfdR9EX3CCEKg9DhURAZOYdWezEn68ssw0XnELO0LI7HcGIZBOpZMhcSjnbAkUcJyLtWNpm5PJackds'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json().get("access_token")

def getSongData(songList):
    
    songNameList = []
    idList = []
    artistList = []
    albumList = []


    for song in songList:
        # nameList1.append(song["name"])
        idList.append(song["id"])
        albumList.append(song["albumIds"])

        for artist in song["artistIds"]:
            artistList.append(artist)
    return {
            'idList': idList,
            'artistList': artistList,
            'albumList': albumList
            }



def checkIfUserPlaylistIsEmpty(data):
    check = False
    if len(data) == 0:
        check = True
    return check

def getChemistryData(key):
    data = {}
    if key in session:
        data = session[key]
    else:
        data = False
    return data

def getSelectedUserPlaylistDataFromSession(key):
    data = ""
    if key in session:
        data = session[key]
    return data


def writeDataToPickle(fileName, data):
    if len(data) == 0:
        open(f'{fileName}.pickle', "w").close()
    else:
        with open(f'{fileName}.pickle', "wb") as file:
                pickle.dump(data, file)

def getDataFromPickle(fileName):
    data = []
    try:
        with (open(f'{fileName}.pickle', "rb")) as openfile:
            while True:
                try:
                    data = pickle.load(openfile)
                except EOFError:
                    break
    except FileNotFoundError:
        return []
    return data

def get1000songs(playlistId, songCount):
    authToken = getToken()
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(songCount)
    collectedSongs = []
    offsets = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900]
    offset = 0;
    start = time.time()
    print("hello")
    
    try:
      while True:
          url = f"https://api.spotify.com/v1/playlists/{playlistId}/tracks?offset={offset}&limit=100"
          headers = {
          'Authorization': f"Bearer {authToken}"
          }
          songList = requests.request("GET", url, headers=headers)
          collectedSongs.extend(songList.json()["items"])
          offset = offset + 100;
          if len(collectedSongs) >= songCount:
              break;
    except Exception as e:
      print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      print(e)
      flash("Could not retreive all songs", 'info')
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(len(collectedSongs))
    end = time.time()
    print(end - start)
    return collectedSongs


def updateColumnData(id, colName, data):
    userData = db.session.query(User).filter(User.id == id).one()
    
    if colName == "user1_playlist":
        userData.user1_playlist = data
    if colName == "user2_playlist":
        userData.user2_playlist = data
    if colName == "user1_songlist":
        userData.user1_songlist = data
    if colName == "user2_songlist":
        userData.user2_songlist = data

    if colName == "commonSongData":
        print('&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&')
        print(data)
        userData.commonSongData = data
    db.session.commit()
            

def getColumnData(id, colName):
    userData = db.session.query(User).filter(User.id == id).one()
    data = None
    if colName == "user1_playlist":
        data = userData.user1_playlist
    if colName == "user2_playlist":
        data = userData.user2_playlist
    if colName == "user1_songlist":
        data = userData.user1_songlist 
    if colName == "user2_songlist":
        data = userData.user2_songlist
    
    if colName == "commonSongData":
        data = userData.commonSongData
    
    if data == None or data == []:
        return  []
    else:
        return  data
    