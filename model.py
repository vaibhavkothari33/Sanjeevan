import pickle
import cv2
import mediapipe as mp
import numpy as np
import warnings
import time
from fastapi import FastAPI, WebSocket

# Suppress warnings related to deprecated functions
warnings.filterwarnings("ignore", category=UserWarning, message="SymbolDatabase.GetPrototype() is deprecated")

app = FastAPI()

# Load the trained model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Dictionary mapping class indices to labels
labels_dict = {
    0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
    10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
    19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z', 26: 'Thank You', 27: 'I love You', 
    28: 'No', 29: 'Good Night', 30: 'Be Safe', 31: 'Are', 32: 'Peace', 33: 'Goodbye', 
    34: 'Hello', 35: 'Take Care', 36: 'All The Best', 37: 'Yes', 38: 'Sorry', 39: 'Please',
    40: 'HackFest', 41: 'Welcome', 42: 'We', 43: 'When', 44: 'To', 45: 'LeetRankers', 
    46: 'In', 47: 'Am'
}

async def process_video(websocket: WebSocket):
    print("Accepting WebSocket connection...")
    await websocket.accept()
    time.sleep(2)
    print("WebSocket connection accepted.")
    
    previous_character = None 
    cap = cv2.VideoCapture(0)  # Capture video from the default camera

    while True:
        data_aux = []
        x_ = []
        y_ = []

        ret, frame = cap.read()  # Read a frame from the camera
        if not ret:
            break

        # Resize the frame to make it smaller (200x150)
        frame = cv2.resize(frame, (250, 200))

        # Convert the frame to JPEG
        ret, jpeg = cv2.imencode(".jpg", frame)
        if not ret:
            break

        # Convert the JPEG image to bytes and send it to the client
        frame_bytes = jpeg.tobytes()
        await websocket.send_bytes(frame_bytes)

        # Process the frame for hand gesture recognition
        H, W, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Collect hand landmark data for prediction
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    data_aux.append(x - min(x_))
                    data_aux.append(y - min(y_))

            # Define bounding box for hand landmarks
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) + 10
            y2 = int(max(y_) * H) + 10

            # Make prediction
            prediction = model.predict([np.asarray(data_aux)])
            predicted_character = labels_dict[int(prediction[0])]

            if predicted_character != previous_character:
                print("Predicted Hand Sign:", predicted_character)
                previous_character = predicted_character

                # Send the predicted character as a plain string
                await websocket.send_text(predicted_character)


        # Send the processed frame bytes to the WebSocket client
        ret, jpeg = cv2.imencode(".jpg", frame)
        if ret:
            frame_bytes = jpeg.tobytes()
            await websocket.send_bytes(frame_bytes)

# WebSocket endpoint for video feed
@app.websocket("/video-feed")
async def video_feed(websocket: WebSocket):
    await process_video(websocket)


