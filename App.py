import os
from datetime import datetime

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/flasksql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)

# init marshmallow
ma = Marshmallow(app)


# Models


class Conference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    talks = db.relationship('Talk', backref='conference', lazy=True)


class Talk(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    duration = db.Column(db.String(120), nullable=False)
    date_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    speakers = db.relationship('Speaker', backref='talk', lazy=True)
    participants = db.relationship('Participant', backref='talk', lazy=True)
    conference_id = db.Column(db.Integer, db.ForeignKey('conference.id'),
        nullable=False)


class Speaker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    talk_id = db.Column(db.Integer, db.ForeignKey('talk.id'),
                              nullable=False)


class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    talk_id = db.Column(db.Integer, db.ForeignKey('talk.id'),
                              nullable=False)

# Serializers/Schema


class ConferenceSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Conference
        fields = ('title', 'description', 'start_date', 'end_date')


class TalkSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Talk
        fields = ('title', 'description', 'start_date', 'end_date', 'conference_id')


class SpeakerSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Speaker
        fields = ('username', 'email', 'talk_id')


class ParticipantSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Participant
        fields = ('username', 'email', 'talk_id')


# init Schema
conference_schema = ConferenceSchema()
conferences_schema = ConferenceSchema(many=True)
talk_schema = TalkSchema()
talks_schema = TalkSchema(many=True)
speaker_schema = SpeakerSchema()
speakers_schema = SpeakerSchema(many=True)
participant_schema = ParticipantSchema()
participants_schema = ParticipantSchema(many=True)


# Get all conferences
@app.route('/conferences', methods=['GET'])
def get_conferences():
    all_confs = Conference.query.all()
    result = conferences_schema.dump(all_confs)
    return jsonify(result.data)


# Create a Conference
@app.route('/create_conf', methods=['POST'])
def add_conference():
    title = request.json['title']
    description = request.json['description']
    start_date = request.json['start_date']
    end_date = request.json['end_date']

    new_conf = Conference(title, description,
                          datetime.strptime(start_date, format='%b %d %Y'),
                          datetime.strptime(end_date, format='%b %d %Y'))
    db.session.add(new_conf)
    db.session.commit()
    return conference_schema.jsonify(new_conf)


# Update a Conference
@app.route('/update_conf/<id>', methods=['PUT'])
def update_conf(id):
    conf = Conference.query.get(id)
    title = request.json['title']
    description = request.json['description']
    start_date = request.json['start_date']
    end_date = request.json['end_date']

    conf.title = title
    conf.description = description
    conf.start_date = datetime.strptime(start_date, format='%b %d %Y')
    conf.end_date = datetime.strptime(end_date, format='%b %d %Y')

    db.session.commit()
    return conference_schema.jsonify(conf)


# Get all talks from a conferences
@app.route('/talks_from_conf/<id>', methods=['GET'])
def get_talks_from_conference(id):
    talks = Talk.query.filter_by(conference_id=id)
    return talks_schema.jsonify(talks)


# Create a Talk
@app.route('/create_talk', methods=['POST'])
def add_talk():
    title = request.json['title']
    description = request.json['description']
    duration = request.json['duration']
    date_time = request.json['date_time']
    conf_title = request.json['conf_title']

    conference = Conference.query.filter_by(title=conf_title).first()

    new_talk = Talk(title, description, duration,
                    datetime.strptime(date_time, format='%b %d %Y %I:%M%p'),
                    conference=conference)

    db.session.add(new_talk)
    db.session.commit()
    return talk_schema.jsonify(new_talk)


# Update a Talk
@app.route('/update_talk/<id>', methods=['PUT'])
def update_talk(id):
    talk = Talk.query.get(id)
    title = request.json['title']
    description = request.json['description']
    duration = request.json['duration']
    date_time = request.json['date_time']
    conf_title = request.json['conf_title']

    conference_id = Conference.query.filter_by(title=conf_title).first().id

    talk.title = title
    talk.description = description
    talk.duration = duration
    talk.date_time = datetime.strptime(date_time, format='%b %d %Y %I:%M%p')
    talk.conference_id = conference_id

    db.session.commit()
    return talk_schema.jsonify(talk)


# Update Speaker in given Talk
@app.route('/update_speaker/<talk_id>/<sp_id>', methods=['PUT'])
def update_talk(talk_id, sp_id):
    speaker = Speaker.query.get(sp_id)
    speaker.talk_id = talk_id

    db.session.commit()
    return speaker_schema.jsonify(speaker)


# Update Participant in given Talk
@app.route('/update_participant/<talk_id>/<pt_id>', methods=['PUT'])
def update_talk(talk_id, pt_id):
    participant = Participant.query.get(pt_id)
    participant.talk_id = talk_id

    db.session.commit()
    return participant_schema.jsonify(participant)


# Run server


if __name__ == "__main__":
    app.run(debug=True)