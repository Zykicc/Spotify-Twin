from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from forms import GetUser1, GetUser2
from models import connect_db, db, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from appFunctions import *
import requests
import re
import json

# keys
USER1_PLAYLIST = "user1_playlist"
USER2_PLAYLIST = "user2_playlist"

USER1_SONGLIST = "user1_songlist"
USER2_SONGLIST = "user2_songlist"

USER1_SELECTED_PLAYLIST_ID = "USER1_SELECTED_PLAYLIST_ID" 
USER2_SELECTED_PLAYLIST_ID = "USER2_SELECTED_PLAYLIST_ID"

USER1_HAS_EMPTY_PLAYLIST = "USER1_HAS_EMPTY_PLAYLIST"
USER2_HAS_EMPTY_PLAYLIST = "USER2_HAS_EMPTY_PLAYLIST"

CHEMISTRY_DATA = "CHEMISTRY_DATA"

CURR_USER_KEY = "curr_user"

# glboal vars
# CommonSongData = []

# User1PlaylistData = []
# User2PlaylistData = []

# User1SonglistData = []
# User2SonglistData = []

authToken = ""

def createApp():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///spotifytwin_db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SECRET_KEY"] = "abc123"
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

    app.app_context().push()


    toolbar = DebugToolbarExtension(app)

    return app

app = createApp()
connect_db(app)

################################################################################
@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None
        user = None
        try:
            user = User.signup()
        except IntegrityError:
            flash("Sign up error", 'danger')

        db.session.commit()
        do_login(user)

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


# @app.route('/setData', methods=["GET", "POST"])
# def setData():
#     if 'user1_playlist' in request.form:
#         global User1PlaylistData
#         User1PlaylistData = request.form['user1_playlist']
    
#     print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
    
#     return redirect('/')


@app.route('/getUserPlaylists', methods=["GET", "POST"])
def getUserPlaylists():
    """Gets all user playlists and saves data to pickle file"""
    try:

        if 'user1_id' in request.form:
            user_id = request.form['user1_id']
        else:
            user_id = request.form['user2_id']

        authToken = getToken()

        userId = re.search(r'(?<=open\.spotify\.com/user/)(.*)(?=\?si=)', user_id).group()

        url = f"https://api.spotify.com/v1/users/{userId}/playlists"
        headers = {
        'Authorization': f"Bearer {authToken}"
        }
        playlist = requests.request("GET", url, headers=headers)
        print("#################################################")

        new_playlist = []
        for item in playlist.json()["items"]:
            new_playlist.append({ 
                'name': item["name"], 
                'id': item["id"],
                'image': item["images"][0]["url"],
                'songCount': item["tracks"]["total"]
            })

        if 'user1_id' in request.form:
            # global User1PlaylistData
            # User1PlaylistData = new_playlist

            updateColumnData(g.user.id, "user1_playlist", new_playlist)

            if len(new_playlist) == 0:
                session[USER1_HAS_EMPTY_PLAYLIST] = True
            else:
                session[USER1_HAS_EMPTY_PLAYLIST] = False
        else:
            # global User2PlaylistData
            # User2PlaylistData = new_playlist
            updateColumnData(g.user.id, "user2_playlist", new_playlist)
            # writeDataToPickle(USER2_PLAYLIST, new_playlist)
            if len(new_playlist) == 0:
                session[USER2_HAS_EMPTY_PLAYLIST] = True
            else:
                session[USER2_HAS_EMPTY_PLAYLIST] = False

    except Exception as e:
        print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        print(e)
        flash("Invalid Spotify link", 'danger')
        
    
    return redirect('/')

##############################################################################

@app.route("/getPlaylistItems/<string:userId>/<string:playlistId>", methods=["GET"])
def getPlaylistItems(userId, playlistId):
    """gets all songs in the playlist, and gets the first 1000 songs in the playlist with offset function. All data is saved in pickle file"""

    prevSelectedPlaylistId = ''
    if userId == "user1":
        if USER1_SELECTED_PLAYLIST_ID in session:
            prevSelectedPlaylistId = getSelectedUserPlaylistDataFromSession(USER1_SELECTED_PLAYLIST_ID)
    else:
        if USER2_SELECTED_PLAYLIST_ID in session:
            prevSelectedPlaylistId = getSelectedUserPlaylistDataFromSession(USER2_SELECTED_PLAYLIST_ID)

    if prevSelectedPlaylistId != playlistId:
        if CHEMISTRY_DATA in session:
            del session[CHEMISTRY_DATA]

    selectedPlayList = ''
    new_songList = []
    try:
        if userId == "user1":
            # global User1PlaylistData
            # playListUser = User1PlaylistData
            playListUser = getColumnData(g.user.id, "user1_playlist")
            # playListUser = getDataFromPickle(USER1_PLAYLIST)
        else:
            # global User2PlaylistData
            # playListUser = User2PlaylistData
            playListUser = getColumnData(g.user.id, "user2_playlist")
            # playListUser = getDataFromPickle(USER2_PLAYLIST)
        selectedPlayList = [playlist for playlist in playListUser if playlist["id"] == playlistId]
        selectedPlayList = selectedPlayList[0]

        songList = get1000songs(playlistId, selectedPlayList["songCount"])

        
        for item in songList:
            if(item["track"] is not None):
                artistList = []
                artistIdList = []
                for artist in item["track"]["artists"]:
                    artistIdList.append(artist["id"])
                    artistList.append(artist["name"])
                
                songUrl = ''
                if(item["track"]["external_urls"].get('spotify') != None):
                    songUrl = item["track"]["external_urls"]["spotify"]
                
                new_songList.append({ 
                    'name': item["track"]["name"], 
                    'id': item["track"]["id"],
                    'artists': artistList,
                    'artistIds': artistIdList,
                    'album': item["track"]["album"]["name"],
                    'albumIds': item["track"]["album"]["id"],
                    'image': item["track"]["album"]["images"],
                    'songUrl': songUrl
                })
            else:
                print("**************************************************")
                print(item)

        
        
    
    except Exception as e:
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(e)
        flash("Error: Could not retreive songs", 'danger')

    if userId == "user1":
        # global User1SonglistData
        # User1SonglistData = new_songList
        updateColumnData(g.user.id, "user1_songlist", new_songList)
        # writeDataToPickle(USER1_SONGLIST, new_songList)
        session[USER1_SELECTED_PLAYLIST_ID] = playlistId
    else:
        # global User2SonglistData
        # User2SonglistData = new_songList
        updateColumnData(g.user.id, "user2_songlist", new_songList)
        # writeDataToPickle(USER2_SONGLIST, new_songList)
        session[USER2_SELECTED_PLAYLIST_ID] = playlistId

    return redirect("/")



@app.route("/compareUsersPlaylists", methods=["GET", "POST"])
def comparePlaylists():
    """Gathers users playlists data and compares them"""

    # global User1SonglistData
    # global User2SonglistData
    # songListUser1 = User1SonglistData
    # songListUser2 = User2SonglistData
    songListUser1 = getColumnData(g.user.id, "user1_songlist")
    songListUser2 = getColumnData(g.user.id, "user2_songlist")
    # songListUser1 = getDataFromPickle(USER1_SONGLIST)
    # songListUser2 = getDataFromPickle(USER2_SONGLIST)

    songListdata1 = getSongData(songListUser1)

    artistList1 = list(set(songListdata1['artistList']))  
    idList1 = list(set(songListdata1['idList']))
    albumList1 = list(set(songListdata1['albumList']))
        

    songListdata2 = getSongData(songListUser2)

    artistList2 = list(set(songListdata2['artistList']))  
    idList2 = list(set(songListdata2['idList']))
    albumList2 = list(set(songListdata2['albumList']))

    # get the dictionary values (we don't care about the keys now)
    uniqueSongDataUser1 = list({song['id']:song for song in songListUser1}.values())


    # get the dictionary values (we don't care about the keys now)
    uniqueSongDataUser2 = list({song['id']:song for song in songListUser2}.values())

    songData2Ids = {song2['id'] for song2 in uniqueSongDataUser2}

    # setting data for global var
    commonSongData = [song for song in uniqueSongDataUser1 if song['id'] in songData2Ids]

    updateColumnData(g.user.id, "commonSongData", commonSongData)

    sameSongCount = len(list(set(idList1).intersection(idList2)))
    sameArtistCount = len(list(set(artistList1).intersection(artistList2)))
    sameAlbumCount = len(list(set(albumList1).intersection(albumList2)))
    
    toalSongs = []
    toalSongs.extend(idList1)
    toalSongs.extend(idList2)
    totalSongCount = len(list(set(toalSongs)))

    toalartists = []
    toalartists.extend(artistList1)
    toalartists.extend(artistList2)
    totalArtistCount = len(list(set(toalartists)))

    toalAlbums = []
    toalAlbums.extend(albumList1)
    toalAlbums.extend(albumList2)
    totalAlbumCount = len(list(set(toalAlbums)))

    spotifyChemPerc = format((sameSongCount + sameArtistCount + sameAlbumCount) / (totalSongCount + totalArtistCount + totalAlbumCount), ".0%")
    
    chemData = {
        'sameSongCount': sameSongCount,
        'sameArtistCount': sameArtistCount,
        'sameAlbumCount': sameAlbumCount,
        'spotifyChemPerc': spotifyChemPerc
    }

    session[CHEMISTRY_DATA] = chemData

    return redirect("/")


########################################################################
@app.route('/clearData', methods=["GET"])
def clearData():
    """Handles clearing all saved data"""
    # global User1PlaylistData
    # User1PlaylistData = []

    updateColumnData(g.user.id, "user1_playlist", [])
    updateColumnData(g.user.id, "user2_playlist", [])
    updateColumnData(g.user.id, "user1_songlist", [])
    updateColumnData(g.user.id, "user2_songlist", [])

    # global User2PlaylistData
    # User2PlaylistData = []
    # writeDataToPickle(USER1_PLAYLIST, [])
    # writeDataToPickle(USER2_PLAYLIST, [])
    
    # global User1SonglistData
    # User1SonglistData = []
    # global User2SonglistData
    # User2SonglistData = []
    # writeDataToPickle(USER1_SONGLIST, [])
    # writeDataToPickle(USER2_SONGLIST, [])

    if CHEMISTRY_DATA in session:
        del session[CHEMISTRY_DATA]

    if USER1_SELECTED_PLAYLIST_ID in session:
        del session[USER1_SELECTED_PLAYLIST_ID]
    
    if USER2_SELECTED_PLAYLIST_ID in session:
        del session[USER2_SELECTED_PLAYLIST_ID]

    if USER1_HAS_EMPTY_PLAYLIST in session:
        session[USER1_HAS_EMPTY_PLAYLIST] = False    

    if USER2_HAS_EMPTY_PLAYLIST in session:
        session[USER2_HAS_EMPTY_PLAYLIST] = False

    # global CommonSongData
    updateColumnData(g.user.id, "commonSongData", [])
    # CommonSongData = []
    return redirect('/')

##################################################################
@app.route("/", methods=["GET", "POST"])
def home_page():
    """home page, also all data is sent to this route"""

   

    form1 = GetUser1()
    form2 = GetUser2()
    
    # global User1PlaylistData
    # playListUser1 = User1PlaylistData

    playListUser1 = getColumnData(g.user.id, "user1_playlist")
    playListUser2 = getColumnData(g.user.id, "user2_playlist")
    songListUser1 = getColumnData(g.user.id, "user1_songlist")
    songListUser2 = getColumnData(g.user.id, "user2_songlist")
    

    # global User2PlaylistData
    # playListUser2 = User2PlaylistData
    # playListUser1 = getDataFromPickle(USER1_PLAYLIST)
    # playListUser2 = getDataFromPickle(USER2_PLAYLIST)

    filledBothSongList = False
    # global User1SonglistData
    # songListUser1 = User1SonglistData;
    # global User2SonglistData
    # songListUser2 = User2SonglistData;
    # songListUser1 = getDataFromPickle(USER1_SONGLIST)
    # songListUser2 = getDataFromPickle(USER2_SONGLIST)


    if len(songListUser1) != 0 and len(songListUser2) != 0:
        filledBothSongList = True
    else:
        filledBothSongList = False

    selectedUser1PlaylistId = getSelectedUserPlaylistDataFromSession(USER1_SELECTED_PLAYLIST_ID)
    selectedUser2PlaylistId = getSelectedUserPlaylistDataFromSession(USER2_SELECTED_PLAYLIST_ID)

    
    chemistryData = getChemistryData(CHEMISTRY_DATA)

    user1PlaylistIsEmpty = checkIfUserPlaylistIsEmpty(USER1_HAS_EMPTY_PLAYLIST)
    user2PlaylistIsEmpty = checkIfUserPlaylistIsEmpty(USER2_HAS_EMPTY_PLAYLIST)

        
    # global CommonSongData
    commonSongdata = getColumnData(g.user.id, "commonSongData")
    
    
    return render_template('home.html', form1=form1, form2=form2, playListUser1=playListUser1, playListUser2=playListUser2, showCompareBtn=filledBothSongList, selectedUser1PlaylistId=selectedUser1PlaylistId, selectedUser2PlaylistId=selectedUser2PlaylistId, chemistryData=chemistryData, user1PlaylistIsEmpty=user1PlaylistIsEmpty, user2PlaylistIsEmpty=user2PlaylistIsEmpty,
    CommonSongData=commonSongdata, songListUser1=songListUser1, songListUser2=songListUser2)
  
    
        
