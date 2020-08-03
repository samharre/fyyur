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
from model import db, Venue, Artist, Show
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

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
  areas = Venue.query.order_by(Venue.state, Venue.city, Venue.name).all()
  data = []
  prev_city = None
  prev_state = None

  for area in areas:
    if area.city != prev_city or area.state != prev_state:
      data.append(
        {'city': area.city, 'state': area.state, 'venues':[]}
      )
    data[len(data)-1]['venues'].append(
      {
        'id': area.id, 
        'name': area.name, 
        'num_upcoming_shows': len(area.get_upcoming_shows())
      }
    )
    prev_city = area.city
    prev_state = area.state

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).order_by(Venue.name).all()
  response = {
    'count': len(venues),
    'data': []
  }
  for venue in venues:
    response['data'].append(
      {
        'id': venue.id, 
        'name': venue.name, 
        'num_upcoming_shows': len(venue.get_upcoming_shows())
      }
    )

  return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)
  data = venue.get_info_venue()

  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    form = request.form
    genres = form.getlist('genres')
    
    venue = Venue(
      name = form.get('name'),
      city = form.get('city'),
      state = form.get('state'),
      genres =  ','.join(genres),
      address = form.get('address'),
      phone = form.get('phone'),
      website = form.get('website'),
      facebook_link = form.get('facebook_link'),
      image_link = form.get('image_link'),
      seeking_talent = True if form.get('seeking_talent') else False,
      seeking_description = form.get('seeking_description')
    )
    db.session.add(venue)
    db.session.commit()
    flash(f'Venue "{venue.name}" was successfully listed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue "{venue.name}" could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/delete', methods=['POST', 'DELETE'])
def delete_venue(venue_id):
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    flash(f'Success deleting Venue "{venue.name}"')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue "{venue.name}" could not be deleted.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    venue = venue.get_info_venue()
    form = VenueForm(data=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    flash(f'Venue id {venue_id} not found!')
    return render_template('pages/home.html')


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try:
    form = request.form
    venue = Venue.query.get(venue_id)
    venue.name = form.get('name')
    venue.city = form.get('city')
    venue.state = form.get('state')
    genres = form.getlist('genres')
    venue.genres =  ','.join(genres)
    venue.address = form.get('address')
    venue.phone = form.get('phone')
    venue.website = form.get('website')
    venue.facebook_link = form.get('facebook_link')
    venue.image_link = form.get('image_link')
    venue.seeking_talent = True if form.get('seeking_talent') else False
    venue.seeking_description = form.get('seeking_description')

    db.session.add(venue)
    db.session.commit()
    flash(f'Venue "{venue.name}" was successfully updated!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Venue "{venue.name}" could not be updated.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', '')
  artists = db.session.query(Artist.id, Artist.name).\
      filter(Artist.name.ilike(f'%{search_term}%')).\
      order_by(Artist.name).all()

  response = {
    'count': len(artists),
    'data': artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)
  data = artist.get_info_artist()
  
  return render_template('pages/show_artist.html', artist=data)


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    form = request.form

    genres = form.getlist('genres')
    artist = Artist(
      name = form.get('name'),
      city = form.get('city'),
      state = form.get('state'),
      genres = ','.join(genres),
      phone = form.get('phone'),
      website = form.get('website'),
      facebook_link = form.get('facebook_link'),
      image_link = form.get('image_link'),
      seeking_venue = True if form.get('seeking_venue') else False,
      seeking_description = form.get('seeking_description')
    )

    db.session.add(artist)
    db.session.commit()
    flash(f'Artist "{artist.name}" was successfully listed!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist "{artist.name}" could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Edit Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    artist = artist.get_info_artist()
    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    flash(f'Artist id {artist_id} not found!')
    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try:
    form = request.form
    artist = Artist.query.get(artist_id)
    artist.name = form.get('name')
    artist.city = form.get('city')
    artist.state = form.get('state')
    genres = form.getlist('genres')
    artist.genres = ','.join(genres)
    artist.phone = form.get('phone')
    artist.website = form.get('website')
    artist.facebook_link = form.get('facebook_link')
    artist.image_link = form.get('image_link')
    artist.seeking_venue = True if form.get('seeking_venue') else False
    artist.seeking_description = form.get('seeking_description')

    db.session.add(artist)
    db.session.commit()
    flash(f'Artist "{artist.name}" was successfully updated!')
  except:
    db.session.rollback()
    flash(f'An error occurred. Artist "{artist.name}" could not be updated.')
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  shows = Show.query.order_by(Show.start_time).all()
  data = [show.get_info_show() for show in shows]

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    form = request.form
    show = Show(
      venue_id = form.get('venue_id'), 
      artist_id = form.get('artist_id'), 
      start_time = form.get('start_time')
    )
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()

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
