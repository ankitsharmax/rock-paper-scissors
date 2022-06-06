import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
from random import randint
import numpy as np

import mysql.connector as mysql
from mysql.connector import Error

import mysql.connector as mysql
from mysql.connector import Error

rock = 0
paper = 0
scissors = 0
cRock = 0
cPaper = 0
cScissors = 0

host = 'localhost'
user = 'root'
password = 'root'
port = 3307 # change a/c to your db port

# Connect to Database
try:
    conn = mysql.connect(host=host, user=user,  
                        password=password,port=port)
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS rockPaperScissors")
        print("Database is created")
        conn.close()
except Error as e:
    print("Error while connecting to MySQL", e)

# Create Table
try:
    conn = mysql.connect(host='localhost', database='rockPaperScissors', user='root', password='root',port=3307)
    if conn.is_connected():
        cursor = conn.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        # create table used_bikes
        cursor.execute("CREATE TABLE IF NOT EXISTS game(value varchar(255) NOT NULL, count int NOT NULL)")
        print("Required table avialable....")
        cursor.execute("SELECT * FROM game")
        row = cursor.fetchall()
        if len(row) == 0:
            sql = ("INSERT INTO game(value, count) VALUES (%s,%s)")
            val = [("rock",0),("paper",0),("scissors",0)]
            try:
                cursor.executemany(sql,val)
                conn.commit()
                print("Ready to start")
            except:
                conn.rollback()
                print("Connection Error")
        cursor.execute("SELECT * FROM game")
        row = cursor.fetchall()
        print(row)
        for e in row:
            if e[0] == "rock":
                rock = e[1]
            elif e[0] == "paper":
                paper = e[1]
            elif e[0] == "scissors":
                scissors = e[1]
        
        
except Error as e:
            print("Error while connecting to MySQL", e)

def compScreen(image_height, image_width,_):
    return np.zeros((image_height, image_width,_))

def randomize():
  comp = randint(0,3)
  if comp == 0:
    return "rock"
  elif comp == 1:
    return "scissors"
  else:
    return "paper"

def getHandMoves(hand_landmarks):
  landmarks = hand_landmarks.landmark
  if all([landmarks[i].y < landmarks[i+3].y for i in range(5,20,4)]): return "rock"
  elif landmarks[13].y < landmarks[16].y and landmarks[17].y < landmarks[20].y and landmarks[8].y < landmarks[6].y and landmarks[12].y < landmarks[10].y: return "scissors"
  elif all([landmarks[i].y < landmarks[i-1].y for i in range(8,21,4)]): return "paper"
 
cap = cv2.VideoCapture(0)

prevGameText = ""
gameText = ""
compText = ""
res = True
score = {"p":0,"c":0}
max_num_hands = 1

with mp_hands.Hands(
    model_complexity=0,
    max_num_hands = max_num_hands,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    image = cv2.flip(image, 1)
    cv2.putText(image,"Player",(50,50),cv2.FONT_HERSHEY_SIMPLEX, 1,
                  (0,255,255), 2, cv2.LINE_AA)
    h, w,_ = image.shape
    compImg = compScreen(h, w,_)
    if not success:
      break

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)
    
    image.flags.writeable = True

    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
    
      hls = results.multi_hand_landmarks
      if hls or len(hls)==2:
        p1_move = getHandMoves(hls[0])
      else:
        res = False
      if res:
        prevGameText = gameText
        gameText = p1_move
        if prevGameText != gameText:
          prevCompText = compText
          compText = randomize()
          if prevGameText == "rock": rock += 1
          elif prevGameText == "paper": paper += 1
          elif prevGameText == "scissors": scissors += 1

          if gameText == "rock" and compText == "paper":
              score["c"] += 1
          if gameText == "paper" and compText == "scissors":
              score["c"] += 1
          if gameText == "scissors" and compText == "rock":
              score["c"] += 1
          if compText == "rock" and gameText == "paper":
              score["p"] += 1
          if compText == "paper" and gameText == "scissors":
              score["p"] += 1
          if compText == "scissors" and gameText == "rock":
              score["p"] += 1
      
      cv2.putText(image,gameText,(170,50),cv2.FONT_HERSHEY_SIMPLEX, 1,
                  (0,255,255), 2, cv2.LINE_AA)
    cv2.putText(image,"Press Q to exit",(50,450),cv2.FONT_HERSHEY_SIMPLEX, 1,
                  (0,255,255), 2, cv2.LINE_AA)
    output = np.zeros((h,w*2,3),dtype='uint8')
    output[0:h,0:w] = image
    if compText == "rock":
      temp = cv2.imread(f"images/{compText}.png")
      compImg = temp
    elif compText == "paper":
      temp = cv2.imread(f"images/{compText}.png")
      compImg = temp
    elif compText == "scissors":
      temp = cv2.imread(f"images/{compText}.png")
      compImg = temp
    cv2.putText(compImg,"Computer",(50,50),cv2.FONT_HERSHEY_SIMPLEX, 1,
                  (0,255,255), 2, cv2.LINE_AA)
    cv2.putText(compImg,f"player:{score['p']} comp:{score['c']}",(50,450),cv2.FONT_HERSHEY_SIMPLEX, 1,
                  (0,255,255), 2, cv2.LINE_AA)
    output[0:h,w:w*2] = compImg
    cv2.imshow('Game Screen', output)

    
    if cv2.waitKey(1) & 0xFF == ord('q'):
      sql = "UPDATE game set count = %s where value = %s"
      val = [(rock,"rock"),(paper,"paper"),(scissors,"scissors")]
      try:
          cursor.executemany(sql,val)
          conn.commit()
          print("Data Stored in db")
      except:
          conn.rollback()
          print("Connection Error")
      try:
          cursor.execute("SELECT * FROM game")
          row = cursor.fetchall()
          print(row)
      except:
          print("Connection Error")
      if score["p"] > score["c"]:
          print("Player Won!!")
      elif score["p"] < score["c"]:
          print("Computer Won!!")
      else:
          print("Game Draw")
      break
cap.release()
cv2.destroyAllWindows()
