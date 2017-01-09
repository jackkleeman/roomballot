from __future__ import unicode_literals, print_function

import os
import inspect
import logging
from datetime import datetime
import json
import ucam_webauth
import raven
import raven.demoserver
import raven.flask_glue
import random
import flask
from flask import Flask, request, render_template, redirect, \
                  url_for, abort, session, flash, send_from_directory
from flask_mongoengine import MongoEngine
import werkzeug
import flask_admin as fadmin
import dateutil
from flask_admin.contrib.mongoengine import ModelView
from flask_admin.actions import action
from werkzeug.datastructures import FileStorage
from wtforms import form, fields
from datetime import *; from dateutil.relativedelta import *
class Request(flask.Request):
    trusted_hosts = {'localhost', '127.0.0.1', '52.58.177.168', '149.254.57.137'}

app = Flask(__name__)
db = MongoEngine()
db.init_app(app)
# app.request_class = Request
app.config["SECRET_KEY"] = os.urandom(16)
app.add_template_global(repr, name="repr")
app.add_template_global(getattr, name="getattr")
admin = fadmin.Admin(app)

modules = {"ucam_webauth": ucam_webauth,
           "raven": raven, "raven.demoserver": raven.demoserver}

auth_decorator = raven.flask_glue.AuthDecorator()

class User(db.Document):
    crs = db.StringField(unique=True)
    position = db.StringField(unique=True)
    slot = db.DateTimeField(unique=True)
    selection = db.StringField(unique=True)
class Group(db.Document): #for first years grouping
    crs1 = db.StringField(unique=True)
    crs2 = db.StringField(unique=True)
    crs3 = db.StringField(unique=True)
    crs4 = db.StringField(unique=True)
    crs5 = db.StringField(unique=True)
    position = db.StringField(unique=True)
    slot = db.DateTimeField(unique=True)
    selection = db.StringField(unique=True)
class Room(db.Document):
    block = db.StringField(unique_with='room')
    room = db.StringField(unique_with='block')
    band = db.StringField()
    photo = db.StringField()
    available = db.BooleanField()
class UserForm(form.Form):
    crs = fields.StringField('CRS')
    position = fields.StringField('Position')
    slot = fields.DateTimeField('Time Slot')
    position = fields.StringField('Selection')
class UserView(ModelView):
    column_list = ['crs','position','slot','selection']
    column_searchable_list = ['crs','position','selection']
    column_sortable_list = ['crs','position','selection']
    column_filters = ['crs','position','selection']
    form = UserForm
    can_export= True
    page_size=1000
    @action('ballot', 'Ballot', 'Are you sure you want to Ballot selected users? Make sure you have selected all in year.')
    def action_ballot(self, ids):
        try:
            query = User.objects(id__in=ids)
            ballot = range(query.count())
            random.shuffle(ballot)
            print(ballot)
            count = 0
            for user in query:
                user.position = str(ballot[count])
                user.save()
                count += 1
            flash("{0} users were successfully Balloted.".format(count))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to ballot users. %(error)s', error=str(ex)), 'error')
    @action('timeslot', 'Time Slot', 'Are you sure you want to Time Slot selected users? Make sure you have selected all in year, and that you have edited the first slot into position .')
    def action_timeslot(self, ids):
        try:
            try:
                firstpos = User.objects.get(id__in=ids, position='0')
                genesis = firstpos.slot
                users = User.objects(id__in=ids).order_by('position')
                for user in users:
                    pos = int(user.position)
                    print(pos)
                    days = pos // 20
                    minutes = (pos % 20) * 30
                    delta = relativedelta(days=days, minutes=minutes)
                    newSlot = genesis + delta
                    user.slot = newSlot
                    user.save()
            except User.DoesNotExist:
                flash("why isnt position 0 in your selection??")
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to ballot users. %(error)s', error=str(ex)), 'error')

def photoName(obj, file_data):
    name, ext = os.path.splitext(file_data.filename)
    name = obj.block + "_" + obj.room
    return werkzeug.utils.secure_filename(name+ext)

class RoomForm(form.Form):
    block = fields.StringField('Block')
    room = fields.StringField('Room')
    band = fields.StringField('Rent Band')
    photo = fadmin.form.upload.ImageUploadField('Photo', base_path="/mnt/c/Users/jackk/Desktop/ballot/static/roomimages/", namegen=photoName, url_relative_path='../roomimages/')
    available = fields.BooleanField('Available')
class RoomView(ModelView):
    column_list = ['block', 'room', 'band','available']
    column_searchable_list = ['block','room','band']
    column_sortable_list = ['block','room','band']
    column_filters = ['block','room','band','available']
    form = RoomForm
    can_export= True
    page_size=1000
    @action('fix', 'Fix', 'Are you sure you want to remove the last letter from each room name selected?')
    def action_fix(self, ids):
        try:
            query = Room.objects(id__in=ids)
            for room in query:
                no = room.room
                no = no[:-1]
                room.room = no
                room.save()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
class GroupForm(form.Form):
    crs1 = fields.StringField('CRS1')
    crs2 = fields.StringField('CRS2')
    crs3 = fields.StringField('CRS3')
    crs4 = fields.StringField('CRS4')
    crs5 = fields.StringField('CRS5')
    position = fields.StringField('Position')
    slot = fields.DateTimeField('Time Slot')
    position = fields.StringField('Selection')
class GroupView(ModelView):
    column_list = ['crs1','crs2','crs3','crs4','crs5','position','slot','selection']
    column_searchable_list = ['crs1','crs2','crs3','crs4','crs5','position','selection']
    column_sortable_list = ['crs1','crs2','crs3','crs4','crs5','position','selection']
    column_filters = ['crs1','crs2','crs3','crs4','crs5','position','selection']
    form = GroupForm
    can_export= True
    page_size=1000
    @action('ballot', 'Ballot', 'Are you sure you want to Ballot selected users? Make sure you have selected all in year.')
    def action_ballot(self, ids):
        try:
            query = Group.objects(id__in=ids)
            ballot = range(query.count())
            random.shuffle(ballot)
            print(ballot)
            count = 0
            for user in query:
                user.position = str(ballot[count])
                user.save()
                count += 1
            flash("{0} users were successfully Balloted.".format(count))
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash(gettext('Failed to ballot users. %(error)s', error=str(ex)), 'error')
    @action('timeslot', 'Time Slot', 'Are you sure you want to Time Slot selected users? Make sure you have selected all in year, and that you have edited the first slot into position .')
    def action_timeslot(self, ids):
        try:
            try:
                firstpos = Group.objects.get(id__in=ids, position='0')
                genesis = firstpos.slot
                users = User.objects(id__in=ids).order_by('position')
                for user in users:
                    pos = int(user.position)
                    print(pos)
                    days = pos // 20
                    minutes = (pos % 20) * 30
                    delta = relativedelta(days=days, minutes=minutes)
                    newSlot = genesis + delta
                    user.slot = newSlot
                    user.save()
            except User.DoesNotExist:
                flash("why isnt position 0 in your selection??")
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
@app.route('/roomimages/<path:filename>')
def static_file(filename):
    return send_from_directory('/mnt/c/Users/jackk/Desktop/ballot/static/roomimages/', filename)

@app.route("/user/add")
def add_user():
    year = request.args.get("year")
    if year == "1":
        group = Group(crs1=session["user"], crs2=None, crs3=None, crs4=None, crs5=None, position="Ballot not yet run", slot=None, selection=None)
        group.save()
        session["ballot"] = True
        session["crs2"] = group.crs2
        session["crs3"] = group.crs3
        session["crs4"] = group.crs4
        session["crs5"] = group.crs5
        session["year"] = "1"
        session["position"] = group.position
        session["slot"] = group.slot
        session["selection"] = group.selection
    else:
        user = User(crs=session["user"], position="Ballot not yet run", slot=None, selection=None)
        user.save()
        session["ballot"] = True
        session["year"] = year
        session["position"] = user.position
        session["slot"] = user.slot
        session["selection"] = user.selection
    flash("user added")
    return redirect(url_for("home"))

@app.route("/group/add")
def add_group():
    crs2 = request.args.get("crs2")
    crs3 = request.args.get("crs3")
    crs4 = request.args.get("crs4")
    crs5 = request.args.get("crs5")
    group = Group.objects.get(crs1=session["user"])
    group.crs2 = crs2
    group.crs3 = crs3
    group.crs4 = crs4
    if crs5 != "":
        group.crs5 = crs5
    group.save()
    session["crs2"] = crs2
    session["crs3"] = crs3
    session["crs4"] = crs4
    session["crs5"] = crs5
    flash("group added")
    return redirect(url_for("home"))


@app.route("/group/select")
def select_group_room():
    if isSlot(session["user"]) and session["year"] == 1:
        selection = request.args.get("selection")
        group = Group.objects.get(crs1=session["user"])
        if group.selection:
            overwrite = group.selection
        group.selection = selection
        group.save()
        session["selection"] = selection
        print(selection)
        room = Room.objects.get(block="chad", room=str(selection))
        room.available = False
        room.save()
        if overwrite:
            oldroom = Room.objects.get(block="chad", room=str(overwrite))
            oldroom.available = True
            oldroom.save()
        return redirect(url_for("home"))


@app.route("/")
def home():
    session_ = session.copy()
    if "_ucam_webauth" in session_:
        del session_["_ucam_webauth"]
    if "_flashes" in session_:
        del session_["_flashes"]
    return render_template("home.html", session=session_)


@app.route("/map")
def map():
    session_ = session.copy()
    return render_template("map.html", session=session_)


@app.route("/rooms/<block>")
def room(block):
    return Room.objects(block=block).to_json()


@app.route("/login_raven")
def login_raven():
    u = url_for("login_raven_response", _external=True)
    r = raven.Request(url=u, desc="python-raven simple_demo")
    return redirect(str(r))


@app.route("/login_raven/response")
def login_raven_response():
    r = raven.Response(request.args["WLS-Response"])
    if r.url != request.base_url:
        print("Bad url")
        abort(400)

    issue_delta = (datetime.utcnow() - r.issue).total_seconds()
    if not -5 < issue_delta < 15:
        print("Bad issue")
        abort(403)

    if r.success:
        # a no-op here, but important if you set iact or aauth
        if not r.check_iact_aauth(None, None):
            print("check_iact_aauth failed")
            abort(403)

        session["user"] = r.principal
        session["auth"] = "raven"
        try:
            user = User.objects.get(crs=session["user"])
            session["ballot"] = True
            session["year"] = "2"
            session["position"] = user.position
            session["slot"] = user.slot
            session["selection"] = user.selection
        except User.DoesNotExist:
            try:
                group = Group.objects.get(crs1=session["user"])
                session["ballot"] = True
                session["crs2"] = group.crs2
                session["crs3"] = group.crs3
                session["crs4"] = group.crs4
                session["crs5"] = group.crs5
                session["year"] = "1"
                session["position"] = group.position
                session["slot"] = group.slot
                session["selection"] = group.selection
            except Group.DoesNotExist:
                session["ballot"] = False
                session["year"] = "Ballot pls"
                session["position"] = "Ballot pls"
                session["slot"] = None
                session["selection"] = None
        flash("Successfully logged in as {0}, Balloted: {1}, Year: {2}, Position: {3}".format(r.principal,session["ballot"],session["year"],session["position"]))
        if session["slot"] == None:
             flash("Your don't have a time slot yet")
        else:
            flash("Your time slot is: {0}".format(session["slot"]))


        return redirect(url_for("home"))
    else:
        flash("Raven authentication failed")
        return redirect(url_for("home"))

@app.route("/logout")
def logout():
    del session["user"]
    del session["auth"]
    if request.args.get("also_raven", False):
        return redirect(raven.RAVEN_LOGOUT)
    else:
        return redirect(url_for("home"))

def isSlot(crsid):
    try:
        user = User.objects.get(crs=crsid)
        if user.slot:
            return user.slot <= datetime.now() <= (user.slot + relativedelta(minutes=30))
        else:
            return False
    except User.DoesNotExist:
        user = Group.objects.get(crs1=crsid)
        if user.slot:
            return user.slot <= datetime.now() <= (user.slot + relativedelta(minutes=30))
        else:
            return False

app.jinja_env.globals.update(isSlot=isSlot)
admin.add_view(UserView(User, 'Second Years'))
admin.add_view(RoomView(Room, 'Rooms'))
admin.add_view(GroupView(Group, 'First Years'))
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True

    app.run(host="0.0.0.0", debug=True)
