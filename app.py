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
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
db = SQLAlchemy(app)
migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows=db.relationship('Show',backref='Venue',lazy=True)
    genres=db.Column(db.ARRAY(db.String))
    website=db.Column(db.String(500))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))

    def __init__(self,id,name,city,state,address,phone,image_link,facebook_link,genres,website,seeking_talent=False,seeking_description=''):
    	self.id=id
    	self.name=name
    	self.city=city
    	self.state=state
    	self.address=address
    	self.phone=phone
    	self.image_link=image_link
    	self.facebook_link=facebook_link
    	self.genres=genres
    	self.website=website
    	self.seeking_talent=seeking_talent
    	self.seeking_description=seeking_description


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows=db.relationship('Show',backref='Artist',lazy=True)
    website=db.Column(db.String(500))
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(500))

    def __init__(self,id,name,city,state,phone,image_link,facebook_link,genres,website,seeking_venue=False,seeking_description=''):
    	self.id=id
    	self.name=name
    	self.city=city
    	self.state=state
    	self.phone=phone
    	self.image_link=image_link
    	self.facebook_link=facebook_link
    	self.genres=genres
    	self.website=website
    	self.seeking_venue=seeking_venue
    	self.seeking_description=seeking_description
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
	__tablename__='Show'
	id=db.Column(db.Integer,primary_key=True)
	artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'),nullable=False)
	venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'),nullable=False)
	start_time=db.Column(db.DateTime)

	def __init__(self,id,artist_id,venue_id,start_time):
		self.id=id
		self.artist_id=artist_id
		self.venue_id=venue_id
		self.start_time=start_time

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
  data=[]
  q1=Venue.query.with_entities(func.count(Venue.id),Venue.state,Venue.city).group_by(Venue.city,Venue.state).all()
  for i in q1:
    q2=Venue.query.filter_by(city=i.city).all()
    venue_info=[]
    for j in q2:
      q3=Show.query.filter(Show.venue_id==j.id).filter(Show.start_time>datetime.now()).all()
      venue_info.append({
        "id":j.id,
        "name":j.name,
        "num_upcoming_shows":q3.count()
        })
    data.append({
      "city":i.city,
      "state":i.state,
      "venues":venue_info
      })

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  q1=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  data=[]
  for i in q1:
    q2=Show.query.filter(Show.venue_id==i.id).filter(Show.start_time>datetime.now()).all()
    data.append({
      "id":i.id,
      "name":i.name,
      "num_upcoming_shows":q2.count()
      })
  response={
    "count":q1.count(),
    "data":data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data=[]
  q1=Venue.query.get(venue_id)
  if not q1:
    return render_template('errors/404.html')
  upcoming=Show.query.filter(Show.venue_id==venue_id).join(Artist).filter(Show.start_time>datetime.now()).all()
  upcoming_data=[]
  for i in upcoming:
    upcoming_data.append({
      "artist_id": i.artist_id,
      "artist_name":i.artist.name ,
      "artist_image_link": i.artist.image_link,
      "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  past=Show.query.filter(Show.venue_id==venue_id).join(Artist).filter(Show.start_time<datetime.now()).all()
  past_data=[]
  for i in past:
    past_data.append({
      "artist_id": i.artist_id,
      "artist_name":i.artist.name ,
      "artist_image_link": i.artist.image_link,
      "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  data.append({
    "id":q1.id,
    "name":q1.name,
    "genres":q1.genres,
    "address":q1.address,
    "city":q1.city,
    "state":q1.state,
    "phone":q1.phone,
    "website":q1.website,
    "facebook_link":q1.facebook_link,
    "seeking_talent":q1.seeking_talent,
    "seeking_description":q1.seeking_description,
    "image_link":q1.image_link,
    "past_shows":past_data,
    "upcoming_shows":upcoming_data,
    "past_shows_count":past.count(),
    "upcoming_shows_count":upcoming.count()
    })
  
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]

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
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error= False
  try:
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    address=request.form['address']
    phone=request.form['phone']
    genres=request.form.getlist('genres')
    image_link=request.form['image_link']
    facebook_link=request.form['facebook_link']
    website=request.form['website']
    seeking_talent=True if 'seeking_talent' in request else False
    seeking_description=request.form['seeking_description']

    venue=Venue(name=name,city=city,state=state,address=address,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_talent=seeking_talent,seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit() 
  except:
    error=True
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  q1=Venue.query.get(venue_id)
  if q1:
    db.session.delete(q1)
    db.session.commit()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  q1=Artist.query.with_entities(Artist.id,Artist.name).all()
  for i in q1:
    data.append({
      "id":i.id,
      "name":i.name
      })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term=request.form.get('search_term','')
  q1=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  data=[]
  for i in q1:
    q2=Show.query.filter(Show.venue_id==i.id).filter(Show.start_time>datetime.now()).all()
    data.append({
      "id":i.id,
      "name":i.name,
      "num_upcoming_shows":q2.count()
    })
  response={
    "count":q1.count(),
    "data":data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  data=[]
  q1=Artist.query.get(artist_id)
  if not q1:
    return render_template('errors/404.html')
  upcoming=Show.query.filter(Show.venue_id==artist_id).join(Venue).filter(Show.start_time>datetime.now()).all()
  upcoming_data=[]
  for i in upcoming:
    upcoming_data.append({
      "venue_id": i.venue_id,
      "venue_name":i.venue.name ,
      "venue_image_link": i.venue.image_link,
      "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  past=Show.query.filter(Show.venue_id==artist_id).join(Venue).filter(Show.start_time<datetime.now()).all()
  past_data=[]
  for i in past:
    past_data.append({
      "venue_id": i.venue_id,
      "venue_name":i.venue.name ,
      "venue_image_link": i.venue.image_link,
      "start_time": i.start_time.strftime('%Y-%m-%d %H:%M:%S')
      })
  data.append({
    "id":q1.id,
    "name":q1.name,
    "genres":q1.genres,
    "city":q1.city,
    "state":q1.state,
    "phone":q1.phone,
    "website":q1.website,
    "facebook_link":q1.facebook_link,
    "seeking_venue":q1.seeking_venue,
    "seeking_description":q1.seeking_description,
    "image_link":q1.image_link,
    "past_shows":past_data,
    "upcoming_shows":upcoming_data,
    "past_shows_count":past.count(),
    "upcoming_shows_count":upcoming.count()
    })
  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  q1=Artist.query.get(artist_id)
  if q1:
    form.name.data: q1.name
    form.genres.data: q1.genres
    form.city.data: q1.city
    form.state.data: q1.state
    form.phone.data: q1.phone
    form.website.data: q1.website
    form.facebook_link.data: q1.facebook_link
    form.seeking_venue.data: q1.seeking_venue
    form.seeking_description.data: q1.seeking_description
    form.image_link.data: q1.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.get(artist_id)
  error= False
  try:
    artist.name=request.form['name']
    artist.city=request.form['city']
    artist.state=request.form['state']
    artist.phone=request.form['phone']
    artist.genres=request.form.getlist('genres')
    artist.image_link=request.form['image_link']
    artist.facebook_link=request.form['facebook_link']
    artist.website=request.form['website']
    artist.seeking_venue=True if 'seeking_venue' in request else False
    artist.seeking_description=request.form['seeking_description']

    db.session.commit() 
  except:
    error=True
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # called upon submitting the new artist listing form

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  q1=Venue.query.get(venue_id)
  if q1:
    form.name.data: q1.name
    form.genres.data: q1.genres
    form.city.data: q1.city
    form.state.data: q1.state
    form.phone.data: q1.phone
    form.address.data: q1.address
    form.website.data: q1.website
    form.facebook_link.data: q1.facebook_link
    form.seeking_venue.data: q1.seeking_venue
    form.seeking_description.data: q1.seeking_description
    form.image_link.data: q1.image_link
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error=False
  venue=Venue.query.get(venue_id)
  error= False
  try:
    venue.name=request.form['name']
    venue.city=request.form['city']
    venue.state=request.form['state']
    venue.address=request.form['address']
    venue.phone=request.form['phone']
    venue.genres=request.form.getlist('genres')
    venue.image_link=request.form['image_link']
    venue.facebook_link=request.form['facebook_link']
    venue.website=request.form['website']
    venue.seeking_talent=True if 'seeking_talent' in request else False
    venue.seeking_description=request.form['seeking_description']

    db.session.commit() 
  except:
    error=True
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error= False
  try:
    name=request.form['name']
    city=request.form['city']
    state=request.form['state']
    phone=request.form['phone']
    genres=request.form.getlist('genres')
    image_link=request.form['image_link']
    facebook_link=request.form['facebook_link']
    website=request.form['website']
    seeking_venue=True if 'seeking_venue' in request else False
    seeking_description=request.form['seeking_description']

    artist=Artist(name=name,city=city,state=state,phone=phone,genres=genres,image_link=image_link,facebook_link=facebook_link,website=website,seeking_venue=seeking_venue,seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit() 
  except:
    error=True
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
 
  data=[]
  q1=Show.query.join(Artist).join(Venue).all()
  for i in q1:
    data.append({
      "venue_id": i.venue_id,
      "venue_name": i.venue.name,
      "artist_id": i.artist_id,
      "artist_name": i.artist.name,
      "artist_image_link": i.artist.image_link,
      "start_time":i.start_time
      })
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
  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  error=False
  try:
    artist_id=request.form['artist_id']
    venue_id=request.form['venue_id']
    start_time=request.form['start_time']
    show=Show(artist_id=artist_id,venue_id=venue_id,start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    error=True
    flash('An error occurred. Show could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if not error:
    flash('Show was successfully listed!')
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
