from game_repo import *
from player_repo import *

#Pages

def index():
    return

@auth.requires_login()
def current():
    games = db((db.game.id == db.player.game_id) & (db.player.user_id == auth.user_id)).select(db.game.ALL)
   
    return dict(games = games)
    
def info():
    game = GetGame(request.args[0])
    
    if game is None:
        return response.render('game/notfound.html')
    
    players = GetPlayersByGame(game.id)

    return dict(game = game, players = players)
    
#Partial Pages
    
def _gamebuttons():
    game = GetGame(request.args[0])
    player = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    btn = {'join':False, 'leave':False, 'start':False, 'delete':False, 'edit':False}
    
    if auth.user is None:
        return dict(game = game, btn = btn)
    
    if player is None and game.status_id.name == 'not started':
        btn['join'] = True
        
    if player is not None and player.role_id.name != 'host':
        btn['leave'] = True
    
    if (player is not None) and (player.role_id.name == 'host'):
        btn['delete'] = True
        btn['edit'] = True
        if game.status_id.name == 'not started':
            btn['start'] = True
    
    return dict(game = game, btn = btn)

def _playerinfo():
    if not auth.user_id:
        return ''

    game = GetGame(request.args[0])
    player = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if not player:
        return ''
    
    if game.status_id.name == 'not started':
        return ''
    
    return dict(game = game, player = player)
    
#Ajax
@auth.requires_login()
def deletegame():
    game = GetGame(request.post_vars.id)
    
    player = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if player is None:
        return dict(success = False)
    if not player.role_id == db.player_type(db.player_type.name == 'host'):
        return dict(success = False)
        
    db(db.game.id == game.id).delete()
    return dict(success = True)

@auth.requires_login()
def joingame():
    game = GetGame(request.post_vars.id)
    
    player = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if player:
        return dict(success = False)

    id = db.player.insert(game_id = game.id, user_id = auth.user_id, role_id = 2, status_id = 1)
    return dict(success = True)

@auth.requires_login()
def leavegame():
    game = GetGame(request.post_vars.id)
    
    player = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if not player:
        return dict(success = False)
    
    if player.role_id.name == 'host':
        return dict(success = False)
        
    db(db.player.id == player.id).delete()
    
    
    return dict(success = True)

@auth.requires_login()
def startgame():
    game = GetGame(request.post_vars.id)
    
    hostplayer = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if hostplayer is None:
        return dict(success = False)
    if not hostplayer.role_id.name == 'host':
        return dict(success = False)
        
    players = db(db.player.game_id == game.id).select(orderby='<random>')

    player = players[-1]
    target = players[0]
    player.update_record(target_id = target.id, status_id = 1)
    
    for i in range (0, len(players)-1):
		player = players[i]
		target = players[i+1]
		player.update_record(target_id = target.id, status_id = 1)
    
    game.update_record(status_id = 2)

    return dict(success = True)

@auth.requires_login()
def killplayer():
    player = db.player(request.post_vars.id)
    game = GetGame(player.game_id)
    hostplayer = db.player((db.player.user_id == auth.user_id) & (db.player.game_id == game.id))
    
    if player.user_id == auth.user_id:
        pass
    elif hostplayer is not none:
        pass
    else:
        return dict(success = False, message = 'Nice try buddy')
    
    if game.status_id.name == 'started':
        db(db.player.target_id == player.id).update(target_id = player.target_id)
        player.update_record(target_id = player.id, status_id = 2)
        CheckEndGame(game.id)
    
    return dict(success = True)

#Private?
    
def CheckEndGame(game_id):
    aliveplayers = db((db.player.status_id.name == 'alive') & (db.player.game_id == game_id)).select()
    if len(aliveplayers) <= 1:
        db(db.game.id == game_id).update(status_id = 3)
    return
    