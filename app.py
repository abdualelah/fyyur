#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy.orm import relationship, backref

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column("genres" ,db.ARRAY(db.String), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = relationship('Show' ,backref='Venue' ,lazy=True )

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column("genres" ,db.ARRAY(db.String), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = relationship('Show' ,backref='Artist' ,lazy=True )

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer ,db.ForeignKey('Artist.id')  )
    venue_id = db.Column(db.Integer ,db.ForeignKey('Venue.id') )
    start_date = db.Column(db.DateTime )
    artist = db.relationship('Artist',backref=backref("Venue_assoc"),lazy =True)
    venue = db.relationship('Venue',backref=backref("Artist_assoc"),lazy =True)

  


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.



  cities = db.session.query(Venue.city , Venue.state).distinct().all()
  data = []
  for city in cities:
    venues_temp =[]
    venues = Venue.query.filter(Venue.city ==  city[0] , Venue.state== city[1]).all()
    for venue in venues:
      venue.num_shows = 0
      for show in venue.shows:
        if(show.start_date >= datetime.now()):
          venue.num_shows+=1
    venues.sort(key=lambda x: x.num_shows , reverse= False)
    for venue in venues:
      temp ={
        'id' : venue.id,
        'name':venue.name,
        'num_upcoming_shows':venue.num_shows
      }
      venues_temp.append(temp)
    city_temp = {
      "city": city[0],
      "state": city[1],
      "venues":venues_temp
    }
    data.append(city_temp)
  print(data)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  venues_temp = []
  query = request.form.get('search_term')
  results   = Venue.query.filter(Venue.name.ilike('%'+query+'%')).all()
  for result in results:
    result.num_upcoming_shows = 0
    for show in result.shows:
      if show.start_date > datetime.now():
        result.num_upcoming_shows +=1
    temp = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.num_upcoming_shows,
    }
    venues_temp.append(temp)

  response={
    "count": len(results),
    "data":venues_temp
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  upcoming_shows = []
  past_shows = []
  
  for show in venue.shows:
      temp ={
      "artist_id": show.artist.id,
      "artist_name":  show.artist.name,
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": str( show.start_date)
    }
      if show.start_date > datetime.now():
        upcoming_shows.append(temp)
      else:
        past_shows.append(temp)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  name = request.form.get("name")
  city = request.form.get("city")
  state = request.form.get("state")
  phone = request.form.get("phone")
  address = request.form.get("address")
  facebook_link = request.form.get("facebook_link")
  genres = request.form.getlist("genres")
  venue = Venue(name = name , city = city  , state = state , phone=phone , genres = genres , facebook_link = facebook_link , address=address)
  try:
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Venue ' + request.form['name'] + ' was not successfully listed!' , category='error')
  finally:
    db.session.close()

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash('Venue was deleted!')
  except:
    db.session.rollback()
    flash('Venue was  not deleted!' , category='error')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/venues.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists :
    temp = {
      "id" : artist.id ,
      "name" :artist.name
    }
    data.append(temp)
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists_temp = []
  query = request.form.get('search_term')
  results   = Artist.query.filter(Artist.name.ilike('%'+query+'%')).all()
  for result in results:
    result.num_upcoming_shows = 0
    for show in result.shows:
      if show.start_date > datetime.now():
        result.num_upcoming_shows +=1
    temp = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.num_upcoming_shows,
    }
    artists_temp.append(temp)

  response={
    "count": len(results),
    "data":artists_temp
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter(Artist.id == artist_id).first()
  upcoming_shows = []
  past_shows = []
  
  for show in artist.shows:
    if show.start_date > datetime.now() :
      temp ={
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "start_time": str(show.start_date)
      }
      upcoming_shows.append(temp)
    
    else:
      temp ={
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "start_time": str(show.start_date)
      }
      past_shows.append(temp)


  data={
    "id": artist.id,
    "name":artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "facebook_link": artist.facebook_link,
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  art = Artist.query.filter(Artist.id == artist_id).first()
  artist={
    "id": art.id,
    "name": art.name,
    "genres": art.genres,
    "city": art.city,
    "state": art.state,
    "phone": art.phone,
    "website": None,
    "facebook_link": art.facebook_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    art = Artist.query.filter(Artist.id == artist_id).first()
    art.name = request.form.get('name')
    art.phone = request.form.get('phone')
    art.facebook_link = request.form.get('facebook_link')
    art.city = request.form.get('city')
    art.state = request.form.get('state')
    art.geners =request.form.getlist('state')
    db.session.commit()
    flash('Done')
  except expression as identifier:
    db.session.rollback()
    flash('Error')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  ven = Venue.query.filter(Venue.id ==venue_id ).first()
  venue={
    "id": ven.id,
    "name": ven.name,
    "genres": ven.genres,
    "address": ven.address,
    "city": ven.city,
    "state": ven.state,
    "phone": ven.phone,
    "facebook_link": ven.facebook_link,
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    ven = Venue.query.filter(Venue.id == venue_id).first()
    ven.name = request.form.get('name')
    ven.phone = request.form.get('phone')
    ven.facebook_link = request.form.get('facebook_link')
    ven.city = request.form.get('city')
    ven.state = request.form.get('state')
    ven.genres =request.form.getlist('genres')
    ven.address= request.form.get('address')
    db.session.commit()
    flash('Done')
  except expression as identifier:
    db.session.rollback()
    flash('Error')
  finally:
    db.session.close()
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  name = request.form.get("name")
  city = request.form.get("city")
  state = request.form.get("state")
  phone = request.form.get("phone")
  facebook_link = request.form.get("facebook_link")
  genres = request.form.getlist("genres")
  artist = Artist(name = name , city = city  , state = state , phone=phone , genres = genres , facebook_link = facebook_link)
  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' was not successfully listed!' , category='error')
  finally:
    db.session.close()
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data=[]
  for show in shows :
    temp ={
    "venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": str(show.start_date)
    }
    data.append(temp)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')
  show = Show(artist_id = artist_id , venue_id =venue_id , start_date=start_time)
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show was not successfully listed!')

  finally:
    db.session.close()

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
