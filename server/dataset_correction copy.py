import os
import pickle

import mediapipe as mp
import cv2

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Create a Hands object
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

data = []
labels = []

# Iterate through items in DATA_DIR
for item in os.listdir(DATA_DIR):
    item_path = os.path.join(DATA_DIR, item)
    # Check if item is a directory
    if os.path.isdir(item_path):
        # Iterate through image files in the directory
        for img_file in os.listdir(item_path):
            img_path = os.path.join(item_path, img_file)
            # Check if img_file is a file
            if os.path.isfile(img_path):
                data_aux = []
                x_ = []
                y_ = []
                img = cv2.imread(img_path)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)
                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
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
                    data.append(data_aux)
                    labels.append(item)
            else:
                print(f"{img_file} is not a file. Skipping.")
    else:
        print(f"{item} is not a directory. Skipping.")

# Save the data and labels to a pickle file
with open('data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)
