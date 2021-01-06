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
from models import *

from flask_migrate import Migrate


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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

  data = []
  venues_query = Venue.query.group_by(Venue.id, Venue.city, Venue.state).all()
  current_time = datetime.now()
  print(current_time)
  num_shows = 0
  for venue in venues_query:
      shows_query = Show.query.filter_by(venue_id=venue.id).all()


      for show in shows_query:
          if show.start_time> current_time:
              num_shows += 1

  for venue in venues_query:
      data.append({
            "city":venue.city,
            "state":venue.state,
            "venues": [{
              "id": venue.id,
              "name":venue.name,
              "num_upcoming_shows": num_shows
            }]
       })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
 #  ----------------------------------------------------------------

  search_term = request.form.get('search_term', '')
  query = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
  response = {
            "count": query.count(),
            "data": query
  }
#  ----------------------------------------------------------------

  return render_template('pages/search_venues.html', results=response,search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
#  ----------------------------------------------------------------
  venues_query = Venue.query.get(venue_id)
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
      artist_query = Artist.query.filter_by(id=show.artist_id).first()
      past_shows.append({
            "artist_id": artist_query.id,
            "artist_name": artist_query.name,
            "artist_image_link": artist_query.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
      artist_query = Artist.query.filter_by(id=show.artist_id).first()
      upcoming_shows.append({
            "artist_id": artist_query.id,
            "artist_name": artist_query.name,
            "artist_image_link": artist_query.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

  data={
      "id": venues_query.id,
      "name": venues_query.name,
      "genres": venues_query.genres,
      "address": venues_query.address,
      "city": venues_query.city,
      "state": venues_query.state,
      "phone": venues_query.phone,
      "facebook_link": venues_query.facebook_link,
      "website": venues_query.website,
      "seeking_talent": venues_query.seeking_talent,
      "seeking_description": venues_query.seeking_description,
      "image_link": venues_query.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  ----------------------------------------------------------------

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm()
  try:
      # name = request.form['name']
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      address = request.form.get('address')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      seeking_talent = True if 'seeking_talent' in request.form else False
      seeking_description = request.form.get('seeking_description')
      website = request.form.get('website')
      venues_query = Venue(name=name,address=address, genres=genres, city=city, state=state, phone=phone, facebook_link=facebook_link, website=website, image_link=image_link,seeking_talent=seeking_talent, seeking_description=seeking_description)

      db.session.add(venues_query)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
#  ----------------------------------------------------------------
    try:
        query = Venue.query.filter_by(id=venue_id)
        query.delete()
        db.session.commit()
        flash('Venue ' + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' +  ' could not be deleted.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []
  artists_query = Artist.query.all()
  for artist in artists_query:
       data.append({
        "id": artist.id,
        "name": artist.name
       })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  query = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  response = {
            "count": query.count(),
            "data": query
  }

  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist_query = Artist.query.get(artist_id)
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()
  past_shows = []
  for show in past_shows_query:
      venue_query = Venue.query.filter_by(id=show.venue_id).first()
      past_shows.append({
            "venue_id": venue_query.id,
            "venue_name": venue_query.name,
            "artist_image_link": venue_query.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
      venue_query = Venue.query.filter_by(id=show.venue_id).first()
      upcoming_shows.append({
            "venue_id": venue_query.id,
            "venue_name": venue_query.name,
            "artist_image_link": venue_query.image_link,
            "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S")
        })

  data={
      "id": artist_query.id,
      "name": artist_query.name,
      "genres": artist_query.genres,
      "city": artist_query.city,
      "state": artist_query.state,
      "phone": artist_query.phone,
      "facebook_link": artist_query.facebook_link,
      "website": artist_query.website,
      "seeking_venue": artist_query.seeking_venue,
      "seeking_description": artist_query.seeking_description,
      "image_link": artist_query.image_link,
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

  artist = Artist.query.get(artist_id)

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  form = ArtistForm()
  try:
      artist = Artist.query.get(artist_id)

      artist.name = form.name.data
      artist.genres = form.genres.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.website_link = form.website_link.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website.data
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  venue = Venue.query.get(venue_id)

  form.name.data = venue.name
  form.genres.data = venue.genres
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  form = VenueForm()
  try:
      venue = Venue.query.get(venue_id)

      venue.name = form.name.data
      venue.genres = form.genres.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.phone = form.phone.data
      venue.website = form.website_link.data
      venue.facebook_link = form.facebook_link.data
      venue.image_link= form.image_link.data
      venue.seeking_talent= form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.commit()
  except:
        db.session.rollback()
  finally:
        db.session.close()



  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  form = ArtistForm()
  try:
      name = request.form.get('name')
      city = request.form.get('city')
      state = request.form.get('state')
      phone = request.form.get('phone')
      genres = request.form.getlist('genres')
      facebook_link = request.form.get('facebook_link')
      image_link = request.form.get('image_link')
      seeking_talent = True if 'seeking_talent' in request.form else False
      seeking_description = request.form.get('seeking_description')
      website = request.form.get('website')
      artists_query = Artist(name=name, genres=genres, city=city, state=state, phone=phone, website=website, facebook_link=facebook_link, image_link=image_link,seeking_venue=seeking_venue, seeking_description=seeking_description)
      db.session.add(artists_query)
      db.session.commit()

      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  shows_query = Show.query.all()
  data = []

  for show in shows_query:
      artist = Artist.query.filter_by(id=show.artist_id).first()
      venue = Venue.query.filter_by(id=show.venue_id).first()
      if show.venue_id :
          data.append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist,
            "start_time": format_datetime(str(show.start_time))
            })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm()
  try:
      venue_id = request.form.get('venue_id')
      artist_id = request.form.get('artisi_id')
      start_time = request.form.get('start_time')
      shows_query = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)

      db.session.add(shows_query)
      db.session.commit()

      flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
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
