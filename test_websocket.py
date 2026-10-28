#!/usr/bin/env python3
"""
Test script to verify WebSocket connection and messaging
"""
import asyncio
import websockets
import json
import base64
import numpy as np
import cv2

async def test_websocket():
    # Create a test image (red square) like before
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[:] = [0, 0, 255]  # Red in BGR

    # Encode as JPEG
    _, buffer = cv2.imencode('.jpg', img)
    img_bytes = buffer.tobytes()

    # Encode to base64
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    # Prepare the message to send
    message = {
        "frame": img_base64
    }

    try:
        # Connect to the WebSocket endpoint
        uri = "ws://localhost:8000/ws/1"
        print(f"Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("Connected to WebSocket")

            # Send the test message
            message_json = json.dumps(message)
            await websocket.send(message_json)
            print(f"Sent message: {message_json[:100]}...")

            # Wait for response
            response = await websocket.recv()
            print(f"Received response: {response}")

            # Parse and display the response
            try:
                response_data = json.loads(response)
                print(f"Parsed response: {json.dumps(response_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response is not valid JSON: {response}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_websocket())