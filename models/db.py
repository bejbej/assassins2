# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []

## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

# before define_tables()
auth.settings.extra_fields['auth_user'] = [
    Field('username', unique=True),
    Field('name', required=IS_NOT_EMPTY())
    ]
    
## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else 'smtp.gmail.com:587'
mail.settings.sender = 'you@gmail.com'
mail.settings.login = 'username:password'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.janrain_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

db.auth_user.first_name.readable = db.auth_user.first_name.writable = False 
db.auth_user.last_name.readable = db.auth_user.last_name.writable = False
auth.settings.login_next = URL("game","current")
auth.settings.logout_next = URL("default","login")
auth.settings.login_url = URL("default", "login")

db.define_table('game_status',
    Field('name', required=IS_NOT_EMPTY()),
    Field('description')
    )

db.define_table('player_status',
    Field('name', required=IS_NOT_EMPTY()),
    Field('description')
    )
    
db.define_table('player_type',
    Field('name', required=IS_NOT_EMPTY()),
    Field('description')
    )
    
db.define_table('game',
    Field('name', default='Default Game', required=IS_NOT_EMPTY()),
    Field('description', 'text', default=''),
    Field('status_id', 'reference game_status', notnull=True)
    )

db.define_table('player',
    Field('game_id', 'reference game', notnull=True),
    Field('user_id', 'reference auth_user', notnull=True),
    Field('target_id', 'reference player'),
    Field('status_id', 'reference player_status', notnull=True),
    Field('role_id', 'reference player_type', notnull=True)
    )

from gluon import current
current.db = db

db.game_status.update_or_insert(id = 1, name = 'not started', description = 'The host has not started this game')
db.game_status.update_or_insert(id = 2, name = 'started', description = 'Started')
db.game_status.update_or_insert(id = 3, name = 'finished', description = 'Finished')
db.player_status.update_or_insert(id = 1, name = 'alive')
db.player_status.update_or_insert(id = 2, name = 'dead')
db.player_type.update_or_insert(id = 1, name = 'host')
db.player_type.update_or_insert(id = 2, name = 'player')
db.player_type.update_or_insert(id = 3, name = 'banned', description = 'A player that is no longer allowed to join this game')
db.player_type.update_or_insert(id = 4, name = 'gone', description = 'A player that has left the game after it has started')
