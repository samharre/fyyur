from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='venues', lazy=True, cascade='all, delete-orphan')
    

    def get_upcoming_shows(self):
        upcoming_shows = list(filter(lambda show: show.start_time >= datetime.today(), self.shows)) 
        return sorted(upcoming_shows, key=lambda show: show.start_time)  


    def get_past_shows(self):
        past_shows = list(filter(lambda show: show.start_time < datetime.today(), self.shows)) 
        return sorted(past_shows, key=lambda show: show.start_time)


    def get_info_venue(self):
        upcoming_shows = [show.get_info_show() for show in self.get_upcoming_shows()]
        past_shows = [show.get_info_show() for show in self.get_past_shows()]
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'genres': self.genres.split(',') if self.genres else [],
            'phone': self.phone,
            'address': self.address,
            'website': self.website,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'seeking_talent': self.seeking_talent,
            'seeking_description': self.seeking_description,
            'upcoming_shows': upcoming_shows,
            'past_shows': past_shows,
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows_count': len(past_shows)
        }


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))

    shows = db.relationship('Show', backref='artists', lazy=True, cascade='all, delete-orphan')

    
    def get_upcoming_shows(self):
        upcoming_shows = list(filter(lambda show: show.start_time >= datetime.today(), self.shows)) 
        return sorted(upcoming_shows, key=lambda show: show.start_time)  


    def get_past_shows(self):
        past_shows = list(filter(lambda show: show.start_time < datetime.today(), self.shows)) 
        return sorted(past_shows, key=lambda show: show.start_time) 


    def get_info_artist(self):
        upcoming_shows = [show.get_info_show() for show in self.get_upcoming_shows()]
        past_shows = [show.get_info_show() for show in self.get_past_shows()]
        return {
            'id': self.id,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'genres': self.genres.split(',') if self.genres else [],
            'phone': self.phone,
            'website': self.website,
            'image_link': self.image_link,
            'facebook_link': self.facebook_link,
            'seeking_venue': self.seeking_venue,
            'seeking_description': self.seeking_description,
            'upcoming_shows': upcoming_shows,
            'past_shows': past_shows,
            'upcoming_shows_count': len(upcoming_shows),
            'past_shows_count': len(past_shows)
          }


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship('Venue')
    artist = db.relationship('Artist')


    def get_info_show(self):
      return {
        'artist_id': self.artist_id,
        'artist_name': self.artist.name,
        'artist_image_link': self.artist.image_link,
        'venue_id': self.venue_id,
        'venue_name': self.venue.name,
        'venue_image_link': self.venue.image_link,
        'start_time': str(self.start_time)
      }