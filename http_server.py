from flask import Flask, request, jsonify
from dylr.core import record_manager, monitor
from dylr.core.room import Room
from dylr.util import logger
import asyncio
import websockets

app = Flask(__name__)

@app.route('/start_recording', methods=['POST'])
def start_recording():
    data = request.json
    room_id = data.get('room_id')
    room_name = data.get('room_name', 'Unknown')
    
    if not room_id:
        return jsonify({'error': 'room_id is required'}), 400

    room = record_manager.get_room(room_id)
    if room is None:
        room = Room(room_id, room_name, True, True, False)
        record_manager.rooms.append(room)
        logger.info_and_print(f'Added new room: {room_name}({room_id})')
    
    monitor.check_room(room)
    return jsonify({'message': f'Started recording for room: {room_name}({room_id})'}), 200

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    data = request.json
    room_id = data.get('room_id')
    
    if not room_id:
        return jsonify({'error': 'room_id is required'}), 400

    room = record_manager.get_room(room_id)
    if room is None:
        return jsonify({'error': f'No active recording for room: {room_id}'}), 400

    recording = record_manager.get_recording(room)
    if recording is not None:
        recording.stop_recording_video()
        recording.stop_recording_danmu()
        recording.stop_one()
        return jsonify({'message': f'Stopped recording for room: {room_id}'}), 200
    else:
        return jsonify({'error': f'No active recording for room: {room_id}'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
