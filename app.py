#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging, sys
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime(timezone=False), nullable=False)
    artist = db.relationship('Artist', back_populates='shows')
    venue = db.relationship('Venue', back_populates='shows')

    def __repr__(self):
      return f'<Show ID: {self.id} Artist ID: {self.artist_id} Venue ID: {self.venue_id}>'

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.Text()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', back_populates='venue', lazy=True, cascade='all, delete', passive_deletes=True)

    def __repr__(self):
      return f'<Venue: {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.Text()), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', back_populates='artist', lazy=True, cascade='all, delete', passive_deletes=True)

    def __repr__(self):
      return f'<Artist: {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
migrate = Migrate(app, db)

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
  data = []
  areas = Venue.query.distinct('city', 'state').all()
  for area in areas:
    record = {'city': area.city, 'state': area.state}
    record['venues'] = []
    venues = Venue.query.filter(Venue.city == area.city, Venue.state == area.state).all()
    for venue in venues:
      num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.datetime.now()).count()
      record['venues'].append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': num_upcoming_shows})
    data.append(record)
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_results = {}
  search_results['data'] = []
  search_term = request.form.get('search_term', '')
  
  venues = Venue.query.filter(Venue.name.ilike('%'+search_term+'%')).all()
  search_results['count'] = len(venues)
  for venue in venues:
    num_upcoming_shows = Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.datetime.now()).count()
    search_results['data'].append({'id': venue.id, 'name': venue.name, 'num_upcoming_shows': num_upcoming_shows})
  
  return render_template('pages/search_venues.html', results=search_results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if venue is None:
    return not_found_error('Venue ID does not exist')
  data = venue.__dict__
  data['past_shows'] = []
  data['upcoming_shows'] = []
  
  past_shows = Show.query.join('artist').with_entities(
    Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time).filter(
    Show.venue_id == venue.id,
    Show.start_time <= datetime.datetime.now()
  ).all()
  data['past_shows_count'] = len(past_shows)
  for show in past_shows:
    data['past_shows'].append({'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': show.artist_image_link, 'start_time': str(show.start_time)})
  
  upcoming_shows = Show.query.join('artist').with_entities(
    Artist.id.label('artist_id'), Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link'), Show.start_time).filter(
    Show.venue_id == venue.id,
    Show.start_time > datetime.datetime.now()
  ).all()
  data['upcoming_shows_count'] = len(upcoming_shows)
  for show in upcoming_shows:
    data['upcoming_shows'].append({'artist_id': show.artist_id, 'artist_name': show.artist_name, 'artist_image_link': show.artist_image_link, 'start_time': str(show.start_time)})
  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    address = request.form.get('address', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website = request.form.get('website', '')
    seeking_talent = request.form.get('seeking_talent') != None
    seeking_description = request.form.get('seeking_description', '')
        
    venue = Venue(name=name,
                  city=city,
                  state=state,
                  address=address,
                  phone=phone,
                  genres=genres,
                  image_link=image_link,
                  facebook_link=facebook_link,
                  website=website,
                  seeking_talent=seeking_talent,
                  seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be listed.')
    abort(500)

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash('Venue successfully deleted.')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be deleted.')
    abort(500)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking an artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Artist.query.filter(Artist.id == artist_id).delete()
    db.session.commit()
    flash('Artist successfully deleted.')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be deleted.')
    abort(500)
  # BONUS CHALLENGE: Implement a button to delete an Artist on a Artist Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by('id').all()
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_results = {}
  search_results['data'] = []
  search_term = request.form.get('search_term', '')

  artists = Artist.query.filter(Artist.name.ilike('%'+search_term+'%')).all()
  search_results['count'] = len(artists)
  for artist in artists:
    num_upcoming_shows = Show.query.filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.datetime.now()).count()
    search_results['data'].append({'id': artist.id, 'name': artist.name, 'num_upcoming_shows': num_upcoming_shows})
  
  return render_template('pages/search_artists.html', results=search_results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  if artist is None:
    return not_found_error('Artist ID does not exist')
  
  data = artist.__dict__
  data['past_shows'] = []
  data['upcoming_shows'] = []
  
  past_shows = Show.query.join('venue').with_entities(
    Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), Show.start_time).filter(
    Show.artist_id == artist.id,
    Show.start_time <= datetime.datetime.now()
  ).all()
  data['past_shows_count'] = len(past_shows)
  for show in past_shows:
    data['past_shows'].append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'venue_image_link': show.venue_image_link, 'start_time': str(show.start_time)})
  
  upcoming_shows = Show.query.join('venue').with_entities(
    Venue.id.label('venue_id'), Venue.name.label('venue_name'), Venue.image_link.label('venue_image_link'), Show.start_time).filter(
    Show.artist_id == artist.id,
    Show.start_time > datetime.datetime.now()
  ).all()
  data['upcoming_shows_count'] = len(upcoming_shows)
  for show in upcoming_shows:
    data['upcoming_shows'].append({'venue_id': show.venue_id, 'venue_name': show.venue_name, 'venue_image_link': show.venue_image_link, 'start_time': str(show.start_time)})
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.address = request.form.get('address', '')
    artist.phone = request.form.get('phone', '')
    artist.genres = request.form.getlist('genres')
    artist.image_link = request.form.get('image_link', '')
    artist.facebook_link = request.form.get('facebook_link', '')
    artist.website = request.form.get('website', '')
    artist.seeking_venue = request.form.get('seeking_venue') != None
    artist.seeking_description = request.form.get('seeking_description', '')
    
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + artist.name + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be updated.')
    abort(500)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.genres = request.form.getlist('genres')
    venue.image_link = request.form.get('image_link', '')
    venue.facebook_link = request.form.get('facebook_link', '')
    venue.website = request.form.get('website', '')
    venue.seeking_talent = request.form.get('seeking_talent') != None
    venue.seeking_description = request.form.get('seeking_description', '')
    
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + venue.name + ' was successfully updated!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Venue could not be updated.')
    abort(500)

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  try:
    name = request.form.get('name', '')
    city = request.form.get('city', '')
    state = request.form.get('state', '')
    phone = request.form.get('phone', '')
    genres = request.form.getlist('genres')
    image_link = request.form.get('image_link', '')
    facebook_link = request.form.get('facebook_link', '')
    website = request.form.get('website', '')
    seeking_venue = request.form.get('seeking_venue') != None
    seeking_description = request.form.get('seeking_description', '')

    artist = Artist(name=name,
                  city=city,
                  state=state,
                  phone=phone,
                  genres=genres,
                  image_link=image_link,
                  facebook_link=facebook_link,
                  website=website,
                  seeking_venue=seeking_venue,
                  seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + name + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Artist could not be listed.')
    abort(500)

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
  data = []
  shows = Show.query.order_by('venue_id').all()
  for show in shows:
    data.append({'venue_id': show.venue.id,
                 'venue_name': show.venue.name,
                 'artist_id': show.artist.id,
                 'artist_name': show.artist.name,
                 'artist_image_link': show.artist.image_link,
                 'start_time': str(show.start_time)})

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  try:
    artist_id = request.form.get('artist_id', '')
    venue_id = request.form.get('venue_id', '')
    start_time = request.form.get('start_time', '')

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
    abort(500)
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