from time import sleep
import cv2 as cv
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
import cvzone
from playsound import playsound

# Loading Video from Webcam
vid_capture=cv.VideoCapture(0)
vid_capture.set(3,1280)
vid_capture.set(4,720)

# Checking to type elsewhere
doType=False

# Creating Keys for the Keyboard
class Button():
    def __init__(self,position,text,size=[70,70]):
        self.position=position
        self.text=text
        self.size=size

# Drawing all the keys on the screen
def keyDrawing(frame,buttonList):
    for button in buttonList:
        rect_x,rect_y=button.position
        width,height=button.size

        cvzone.cornerRect(frame,(button.position[0],button.position[1],button.size[0],button.size[1]),20,rt=0)
        cv.rectangle(frame,button.position,(rect_x+width,rect_y+height),(0,0,180),cv.FILLED)
        cv.putText(frame,button.text,(rect_x+15,rect_y+50),fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,fontScale=3,color=(255,255,255),thickness=2)
    return frame

# To take Virtual Keyboard input outside
keyboard=Controller()

def keyTyper(button,doType):
    if doType:
        keyboard.press(button)

keys_keyboard=[["Q","W","E","R","T","Y","U","I","O","P"],
               ["A","S","D","F","G","H","J","K","L",";","<--"],
               ["Z","X","C","V","B","N","M",",",".","/"],["______________"]]

# Text that is generated by the keyboard
text_written=""

# Defining properties of the keys
buttonList=[]
for i in range(len(keys_keyboard)):
        for j,key in enumerate(keys_keyboard[i]):
            if key=="<--":
                buttonList.append(Button([100*j+40,100*i+50],key,[200,70]))
            elif key==keys_keyboard[-1][-1]:
                buttonList.append(Button([100*j+50,100*i+50],key,[800,70]))
            else:
                buttonList.append(Button([100*j+50,100*i+50],key))

# Loading Hand Detection module
detector=HandDetector(detectionCon=0.8,maxHands=2)

while True:

    # Obtaining individual frames
    isTrue,frame=vid_capture.read()
    # Flipping image for better handling of Keyboard by the user
    frame=cv.flip(frame,1)

    ## hands=detector.findHands(frame,draw=False,flipType=False)
    hands,frame=detector.findHands(frame,flipType=False)

    frame=keyDrawing(frame,buttonList)

    #In case a hand is detected
    if hands:
        hand1=hands[0]
        lmList=hand1["lmList"]  #Landmark list of 1 hand
        bbox=hand1["bbox"]  #Bounding box of 1 hand

        for button in buttonList:

            # x,y coordinates of the buttons
            rect_x,rect_y=button.position
            width,height=button.size

            # x,y coordinates of index finger
            finger_x,finger_y=lmList[8][0],lmList[8][1]

            # Index finger is within a button's region
            if rect_x<finger_x<(rect_x+width) and rect_y<finger_y<(rect_y+height):

                # Increase in button size
                cvzone.cornerRect(frame,(button.position[0]-10,button.position[1]-10,button.size[0]+20,button.size[1]+20),20,rt=0)
                cv.rectangle(frame,(button.position[0]-10,button.position[1]-10),(rect_x+width+10,rect_y+height+10),(0,0,80),cv.FILLED)
                cv.putText(frame,button.text,(rect_x+15,rect_y+50),fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,fontScale=3,color=(255,255,255),thickness=2)      

                # Calculation of distance between index and middle finger
                finger_length,inf=detector.findDistance((lmList[8][0],lmList[8][1]),(lmList[12][0],lmList[12][1]))
                print(finger_length)

                # In case of key click
                if finger_length<45:

                    # Change in key color
                    cv.rectangle(frame,(button.position[0]-10,button.position[1]-10),(rect_x+width+10,rect_y+height+10),(0,255,0),cv.FILLED)
                    cv.putText(frame,button.text,(rect_x+15,rect_y+50),fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,fontScale=3,color=(255,255,255),thickness=2)
                    
                    # Generation of text
                    if button.text=="<--":
                        text_written=text_written[:-1]
                        keyTyper("\b",doType)
                    elif button.text==keys_keyboard[-1][-1]:
                        text_written+=" "
                        keyTyper(" ",doType)
                    else:
                        text_written+=button.text
                        keyTyper(button.text,doType)
                    
                    # Playing sound for key click
                    playsound("ActualClick.mp3")
                    # sleep(0.1)

    # Text and Text box creation
    cv.rectangle(frame,(50,450),(1000,550),(153,153,153),cv.FILLED)
    cv.putText(frame,text_written,(60,515),fontFace=cv.FONT_HERSHEY_COMPLEX_SMALL,fontScale=3,color=(255,255,255),thickness=2)

    # Display of resultant frame 
    cv.imshow("Camera Capture",frame)

    # Escape condition
    if cv.waitKey(20) & 0xFF==ord('d'):
        break