from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError
from models import connect_db, db, User
from forms import LoginForm, SignUpForm, GetUser1, GetUser2
from appFunctions import *
import requests
import re



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
CommonSongData = []


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///capstone_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

app.app_context().push()
connect_db(app)


toolbar = DebugToolbarExtension(app)

authToken = ""

@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


################################################################################


@app.route("/register", methods=["GET", "POST"])
def signup():
  """register page and handles form submission"""


  form = SignUpForm()

  if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup_page.html', form=form)

        do_login(user)

        return redirect("/")

  return render_template("signup_page.html", form=form)

################################################################################

@app.route("/login", methods=["GET", "POST"])
def login():
  """Login page and handles form submission"""

  form = LoginForm()

  if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')
  

  return render_template("Login_page.html", form=form)

################################################################################


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash("Goodbye!", "info")
    return redirect('/')

################################################################################


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
            writeDataToPickle(USER1_PLAYLIST, new_playlist)
            if len(new_playlist) == 0:
                session[USER1_HAS_EMPTY_PLAYLIST] = True
            else:
                session[USER1_HAS_EMPTY_PLAYLIST] = False
        else:
            writeDataToPickle(USER2_PLAYLIST, new_playlist)
            if len(new_playlist) == 0:
                session[USER2_HAS_EMPTY_PLAYLIST] = True
            else:
                session[USER2_HAS_EMPTY_PLAYLIST] = False

    except Exception as e:
        print(e)
        flash("Invalid Spotify link", 'danger')
        
    
    return redirect('/')

##############################################################################

@app.route("/getPlaylistItems/<string:userId>/<string:playlistId>", methods=["GET"])
def getPlaylistItems(userId, playlistId):
    """gets all songs in the playlist, and gets the first 1000 songs in the playlist with offset function. All data is saved in pickle file"""

    selectedPlayList = ''
    new_songList = []
    try:
        if userId == "user1":
            playListUser = getDataFromPickle(USER1_PLAYLIST)
        else:
            playListUser = getDataFromPickle(USER2_PLAYLIST)
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
        writeDataToPickle(USER1_SONGLIST, new_songList)
        session[USER1_SELECTED_PLAYLIST_ID] = playlistId
    else:
        writeDataToPickle(USER2_SONGLIST, new_songList)
        session[USER2_SELECTED_PLAYLIST_ID] = playlistId

    return redirect("/")



@app.route("/compareUsersPlaylists", methods=["GET", "POST"])
def comparePlaylists():
    """Gathers users playlists data and compares them"""

    songListUser1 = getDataFromPickle(USER1_SONGLIST)
    songListUser2 = getDataFromPickle(USER2_SONGLIST)

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
    global CommonSongData
    CommonSongData = [song for song in uniqueSongDataUser1 if song['id'] in songData2Ids]

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
    writeDataToPickle(USER1_PLAYLIST, [])
    writeDataToPickle(USER2_PLAYLIST, [])

    writeDataToPickle(USER1_SONGLIST, [])
    writeDataToPickle(USER2_SONGLIST, [])

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

    global CommonSongData
    CommonSongData = []
    return redirect('/')

##################################################################
@app.route("/", methods=["GET", "POST"])
def home_page():
    """home page, also all data is sent to this route"""
    
    form1 = GetUser1()
    form2 = GetUser2()


    
    playListUser1 = getDataFromPickle(USER1_PLAYLIST)
    playListUser2 = getDataFromPickle(USER2_PLAYLIST)

    filledBothSongList = False
    songListUser1 = getDataFromPickle(USER1_SONGLIST)
    songListUser2 = getDataFromPickle(USER2_SONGLIST)


    if len(songListUser1) != 0 and len(songListUser2) != 0:
        filledBothSongList = True
    else:
        filledBothSongList = False

    selectedUser1PlaylistId = getSelectedUserPlaylistDataFromSession(USER1_SELECTED_PLAYLIST_ID)
    selectedUser2PlaylistId = getSelectedUserPlaylistDataFromSession(USER2_SELECTED_PLAYLIST_ID)

    
    chemistryData = getChemistryData(CHEMISTRY_DATA)

    user1PlaylistIsEmpty = checkIfUserPlaylistIsEmpty(USER1_HAS_EMPTY_PLAYLIST)
    user2PlaylistIsEmpty = checkIfUserPlaylistIsEmpty(USER2_HAS_EMPTY_PLAYLIST)

        
    global CommonSongData
    print(CommonSongData)
    if g.user:
        return render_template('home.html', form1=form1, form2=form2, playListUser1=playListUser1, playListUser2=playListUser2, showCompareBtn=filledBothSongList, selectedUser1PlaylistId=selectedUser1PlaylistId, selectedUser2PlaylistId=selectedUser2PlaylistId, chemistryData=chemistryData, user1PlaylistIsEmpty=user1PlaylistIsEmpty, user2PlaylistIsEmpty=user2PlaylistIsEmpty,
        CommonSongData=CommonSongData)
  
    else:
        return render_template("home_anon.html")
