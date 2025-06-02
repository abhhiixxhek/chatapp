from website import create_app,db,Workspace, User, Channel, Chats
from flask_socketio import SocketIO, send, emit, join_room
from flask import session
from flask_login import login_user, logout_user, login_required, current_user
import random  
import string
from flask import Blueprint, render_template, session, redirect, request

app = create_app()

socketio = SocketIO(app,logger=True, engineio_logger=True)

@socketio.on('sendimage')
def sendimage(data):
    print("hello")
    chat_id = session.get('imageid')
    if not chat_id:
        print(f"Error: 'imageid' not found in session.")
        return

    chat_entry = Chats.query.filter_by(id=chat_id).first()

    if chat_entry:
        session['imageid'] = -1 # Clear it once processed or if invalid

        data_to_emit = {
            'id': chat_entry.id,
            'message_content': chat_entry.message, # This is the Cloudinary URL
            'username': chat_entry.username,
            'wid': chat_entry.wid,
            'channel_id': chat_entry.channel_id,
            'image': 1, # This is an image message
            'timestamp': chat_entry.timestamp.isoformat() if chat_entry.timestamp else None
        }

        workspace = Workspace.query.filter_by(id=chat_entry.wid).first()
        if workspace:
            join_room(workspace.name)
            emit('receiveMessage', data_to_emit, broadcast=True, room=workspace.name)
        else:
            print(f"Error: Workspace not found for chat entry ID {chat_entry.id} with WID {chat_entry.wid}")
    else:
        print(f"Error: Chat entry not found for imageid {chat_id}")
        session['imageid'] = -1 # Clear invalid ID from session


@socketio.on('message')
def handle_message(data):
    print(data)
    # Standardize to current_user
    username = current_user.name
    user = User.query.filter_by(name = username).first()
    if user.workspace_list:
        wlist = user.workspace_list.split()
        wid = int(wlist[0])
        room = Workspace.query.filter_by(id = wid).first()
        join_room(room.name)
    send({"msg": data['data'], "wid":"1", "channel_d":"2"})

@socketio.on('createWorkspace')
def handle_createWorkspace(data):
    print(data)
    if not data or 'name' not in data or not data['name'].strip():
        emit('error', {'msg': 'Workspace name is required.'}, room=request.sid)
        return

    w = Workspace()
    w.admin_username = current_user.name # Standardize to current_user
    w.name = data['name'].strip()
    joining_code = random_string(4,2)
    w.joining_code = joining_code
    db.session.add(w)
    db.session.commit()
    room = Workspace.query.filter_by(name = data['name']).first()
    user = User.query.filter_by(name = current_user.name).first() # Standardize to current_user

    new_workspace_id = str(room.id)
    current_ids = user.workspace_list.split() if user.workspace_list else []
    if new_workspace_id not in current_ids:
        current_ids.append(new_workspace_id)
        user.workspace_list = " ".join(current_ids) + " " # Ensure trailing space

    db.session.commit()
    print("hello",user.workspace_list)
    join_room(room.name)
    updated_data = { # Use a new dict to avoid modifying input `data` directly if not intended
        "name":data['name'],
        "admin_username": current_user.name, # Standardize to current_user
        "id": room.id, 
        "joining_code": joining_code,
    }
    emit('createWorkspaceJS',updated_data, broadcast=True)

@socketio.on('createChannel')
def handle_createChannel(data):
    if not data or 'name' not in data or not data['name'].strip() or 'wid' not in data:
        emit('error', {'msg': 'Channel name and workspace ID are required.'}, room=request.sid)
        return

    c = Channel()
    c.admin_username = current_user.name # Standardize to current_user
    c.name = data['name'].strip()
    c.wid = data['wid']

    room = Workspace.query.filter_by(id = data['wid']).first()
    if not room:
        emit('error', {'msg': 'Workspace not found for channel creation.'}, room=request.sid)
        return

    db.session.add(c)
    db.session.commit() # c.id should be populated here

    updated_data = {
        "name": c.name, # Use c.name for consistency
        "admin_username": c.admin_username,
        "id": c.id,       # Use c.id directly
        "wid": c.wid,
    }
    emit('createChannelJS', updated_data, room=room.name, broadcast= True)

@socketio.on('join')
def joinRoom(data):
    if not data or ('wid' not in data and 'name' not in data):
        # Depending on how this event is used, direct error emission might or might not be needed.
        # For now, just log and prevent crash.
        print("Error: joinRoom called with insufficient data.")
        return

    room = None
    if data.get('wid'):
        room = Workspace.query.filter_by(id = data['wid']).first()
    elif data.get('name'): # This case might be problematic if names aren't unique
        room = Workspace.query.filter_by(name = data['name']).first()

    if room:
        join_room(room.name)
    else:
        print(f"Error: Workspace not found for joinRoom with data: {data}")
        # Optionally emit error to client if this action is directly user-initiated with feedback expectation
        # emit('error', {'msg': 'Workspace to join not found.'}, room=request.sid)

@socketio.on('getChannels')
def sendChannels(data):
    if not data or 'wid' not in data:
        emit('getChannelsJS', {"channels":[], "channelCount":0, "name":""}) # Send empty response
        return

    wid = data['wid']
    room = Workspace.query.filter_by(id = wid).first()

    if not room:
        emit('getChannelsJS', {"channels":[], "channelCount":0, "name":""}) # Send empty response
        return

    Channels = Channel.query.filter_by(wid = wid).all()
    ch = []
    ChannelCount = len(Channels) # Use len(Channels) instead of another query
    # The original structure ch.append({i: {details}}) creates a list of dicts where key is index.
    # A list of dicts [{details}, {details}] is more common.
    for idx, channel_obj in enumerate(Channels): # Changed c to channel_obj for clarity
        ch.append({
            'id': channel_obj.id,
            'name': channel_obj.name,
            'admin_username': channel_obj.admin_username,
            'wid': channel_obj.wid
            # Removed the outer dict keyed by index 'i' for a simpler list of channels
        })
    emit('getChannelsJS', {"channels":ch, "channelCount":ChannelCount, "name":room.name})

@socketio.on('getWorkspaceName')
def get_workspaceName(data):
    if not data or 'wid' not in data:
        emit('changeWorkspaceName', {"name":"Error", "joining_id" :""}) # Send error response
        return

    wid = data['wid']
    room = Workspace.query.filter_by(id = wid).first()

    if not room:
        emit('changeWorkspaceName', {"name":"Not Found", "joining_id" :""}) # Send error response
        return

    print(wid) # Original print
    print("hello",room.joining_code) # Original print
    emit('changeWorkspaceName', {"name":room.name, "joining_id" :room.joining_code})

@socketio.on('chatmsg')
def chat_msg(data):
    if not data or \
       'msg' not in data or \
       'wid' not in data or \
       'channel_id' not in data:
        emit('error', {'msg': 'Message content, workspace ID, and channel ID are required.'}, room=request.sid)
        return

    # Optional: check if data['msg'] is empty if that's not allowed.
    # if not data['msg'].strip():
    #     emit('error', {'msg': 'Message cannot be empty.'}, room=request.sid)
    #     return

    workspace = Workspace.query.filter_by(id=data['wid']).first()
    if not workspace:
        emit('error', {'msg': 'Workspace not found for chat message.'}, room=request.sid)
        return
    # Could also check if channel exists, though messages are tied to WID/CID.

    c = Chats()
    c.message = data['msg']
    c.username = current_user.name # Standardize to current_user
    c.wid = data['wid']
    c.channel_id = data['channel_id']
    c.image = 0

    # Prepare data for emitting, ensuring username is from current_user
    emit_data = {
        'msg': data['msg'],
        'username': current_user.name, # Standardize to current_user
        'wid': data['wid'],
        'channel_id': data['channel_id'],
        'image': 0,
        'id': c.id # Assuming you want to send the chat id back
    }
    # emit_data preparation was already good.
    # db.session.add(c) and db.session.commit() are fine.
    # The room for join_room is the workspace.name, which is workspace.name.
    db.session.add(c)
    db.session.commit()

    emit_data = {
        'message_content': c.message,
        'username': c.username,
        'wid': c.wid,
        'channel_id': c.channel_id,
        'image': c.image,
        'id': c.id,
        'timestamp': c.timestamp.isoformat() if c.timestamp else None
    }
    print(c) # Original print
    join_room(workspace.name) # Use workspace.name from fetched workspace
    emit('receiveMessage', emit_data, broadcast= True, room=workspace.name)

@socketio.on('getMessages')
def sendMessages(data):
    if not data or 'wid' not in data or 'channel_id' not in data:
        emit('receiveMessageJS', {"chats":[], "channel_id":None, "name":"Error"}) # Send empty/error response
        return

    workspace = Workspace.query.filter_by(id=data['wid']).first()
    channel = Channel.query.filter_by(id=data['channel_id'], wid=data['wid']).first() # Ensure channel belongs to workspace

    if not workspace or not channel:
        emit('receiveMessageJS', {"chats":[], "channel_id":data.get('channel_id'), "name":"Not Found"}) # Send empty/error response
        return

    chats = Chats.query.filter_by(wid = data['wid'], channel_id = data['channel_id']).order_by(Chats.timestamp.asc()).all()
    chatscount = len(chats) # Already correct

    # Simplified ch list structure as in getChannels
    ch = []
    for chat_obj in chats: # Changed c to chat_obj for clarity
        ch.append({
            'id': chat_obj.id,
            'message_content': chat_obj.message,
            'username': chat_obj.username,
            'wid': chat_obj.wid,
            'channel_id': chat_obj.channel_id,
            'image': chat_obj.image,
            'timestamp': chat_obj.timestamp.isoformat() if chat_obj.timestamp else None
        })

    join_room(workspace.name) # Use workspace.name
    emit('receiveMessageJS', {"chats":ch, "channel_id":channel.id, "name":channel.name}, broadcast= True, room=workspace.name)

@socketio.on('joinWorkspace')
def addWorkspace(data):
    if not data or 'name' not in data or not data['name'].strip() or \
       'code' not in data or not data['code'].strip():
        emit('error', {'msg': 'Workspace name and joining code are required.'}, room=request.sid)
        return

    user = User.query.filter_by(name = current_user.name).first() # Standardize to current_user

    # Use stripped data for query
    workspace_to_join = Workspace.query.filter_by(name=data['name'].strip(), joining_code=data['code'].strip()).first()

    if not workspace_to_join:
        emit('error', {"msg": "Invalid workspace name or joining code.", "username": current_user.name}, room=request.sid)
        return

    # The rest of the addWorkspace logic was already good.
    room_obj = workspace_to_join
    join_room(room_obj.name)
    new_workspace_id = str(room_obj.id)
    current_ids = user.workspace_list.split() if user.workspace_list else []
    if new_workspace_id in current_ids:
        emit('error', {"msg":"You have already joined the workspace!", "username":current_user.name}, room=request.sid)
    else:
        current_ids.append(new_workspace_id)
        user.workspace_list = " ".join(current_ids) + " "
        db.session.commit()
        emit('workspaceJoined', {"wid": room_obj.id, "username":current_user.name, "name": room_obj.name,}, room=request.sid)

def random_string(letter_count, digit_count):  
    str1 = ''.join((random.choice(string.ascii_letters) for x in range(letter_count)))  
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))  
  
    sam_list = list(str1) # it converts the string to list.  
    random.shuffle(sam_list) # It uses a random.shuffle() function to shuffle the string.  
    final_string = ''.join(sam_list)  
    return final_string 

@app.errorhandler(405)
  
# inbuilt function which takes error as parameter
def not_found(e):
  return render_template("/views/404.html")

@app.errorhandler(404)
  
# inbuilt function which takes error as parameter
def not_found(e):
  return render_template("/views/404.html")

@app.errorhandler(500)
def internal_server_error(e):
  # Optionally, log the error e
  return render_template("/views/500.html"), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
