import cv2
import mediapipe as mp
import time

#화면 캡쳐
import pyautogui
import numpy

#+++++TO-DO+++++
# 1.버퍼에 랜드마크 값 저장하고 평균 값을 구해 손떨림 보정하기
# 2.제스쳐 인식 범위를 화면의 일부로 제한. (노트북 마우스 패드처럼 하기. 지금은 카메라 끄트머리에서 커서 조작이 힘듦)
# 3.제스쳐를 바르게 인식 하기 위해 카메라는 손 보다 높은 곳에서 내려다 봐야함(카메라가 내 시점일 때). 카메라가 앞에서 나를 바라보는 시점이라면 손 보다 낮은 곳에서 올려다 봐야 함
# 4.제스쳐 인식으로 click() 함수 호출
# 5.왼 손, 오른 손에 다른 제스쳐 적용
#++++++++++++++

#--------------------------참조--------------------------
# pyautogui - https://pyautogui.readthedocs.io/en/latest/
# mediapipe hand landmarks - https://developers.google.com/mediapipe/solutions/vision/gesture_recognizer
#--------------------------------------------------------

#마우스로 사용할 손 방향 L:왼 손 R:오른 손
hand_main='R'

#===========mediapipe =============
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#==================================

#===모니터 크기 측정, 사용할 이미지 크기 설정====
ori_monitor_width,ori_monitor_height=pyautogui.size()
half_monitor_width=int(ori_monitor_width/2)
half_monitor_height=int(ori_monitor_height/2)
#==============================================

#===================스크린샷 반환=====================
# 추후 카메라 이미지와 컴퓨터 화면을 합성하여 디스플레이 하기 위함
def screenCapture():
    screen_cap=pyautogui.screenshot()
    screen_cap=numpy.array(screen_cap)
    screen_cap=cv2.cvtColor(screen_cap,cv2.COLOR_BGR2RGB)

    screen_cap=cv2.resize(screen_cap, (half_monitor_width,half_monitor_height), cv2.INTER_LINEAR)

    return screen_cap
#=====================================================

#===========카메라에서 손가락 좌표 -> 화면에서 손가락 좌표 변환=============
def handCursor(src_frame):
    cursor_x=5
    cursor_y=5
    #state 0 : 카메라에 손 안잡힘.   1 : 손 보임.     2 : 클릭 제스쳐 취함.
    state=0

    #result에 process() 결과 저장
    result = hands.process(cv2.cvtColor(src_frame, cv2.COLOR_BGR2RGB))
    #multi_hand_landmarks의 값이 존재하면? ...
    if result.multi_hand_landmarks:
        
        hand_landmarks = result.multi_hand_landmarks[0]

        #src_frame 위에 hand_landmarks이미지를 그리는 함수. 약간의 속도 향상이 있을지 몰라서 mp_drawing 코드 주석 처리함
        mp_drawing.draw_landmarks(src_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        #카메라에서 손가락 좌표 (0.0~1.0)
        cursor_x=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
        cursor_y=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

        #화면에서 좌표 (0 ~ 모니터 가로 길이, 0 ~ 모니터 세로 길이).
        cursor_x=int(cursor_x*ori_monitor_width)
        cursor_y=int(cursor_y*ori_monitor_height)

        #제스쳐 인식
        state= getGesutre(hand_landmarks)
    
    cv2.imshow('MediaPipe Hands',src_frame )
    
    #return src_frame
    return cursor_x, cursor_y, state
#===============================================

#=====================제스쳐 인식=====================
def getGesutre(hand_landmarks):
    state=1

    if(hand_main=='R'):
        #검지
        index_tip=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        index_pip=hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y
        #중지
        middle_tip=hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
        middle_pip=hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y
        #엄지
        thumb_tip=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
        thumb_ip=hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP].x

        index_tip=int(index_tip*1000)
        middle_tip=int(middle_tip*1000)
        index_pip=int(index_pip*1000)
        middle_pip=int(middle_pip*1000)
        #엄지는 짧아서 정확한 비교를 위해 더 큰 값을 곱 해야 함
        thumb_tip=int(thumb_tip*1000000)
        thumb_ip=int(thumb_ip*1000000)

        #제스쳐 인식 후 state 지정

    return state
#====================================================

#=========x,y 좌표로 마우스 커서 이동==========
def cursorMove(x,y):
    pyautogui.moveTo(x,y)
    return 0
#==============================================

#===========마우스 클릭===============
def click():
    pyautogui.click()
    return 0
#====================================

#monitorArea함수 추가로 아래 코드 주석 처리함
pyautogui.FAILSAFE=False

#=========== x,y 범위 박스 ================
def monitorArea(cursor_x,cursor_y):
    if cursor_x<=0:
        cursor_x=1
    if(cursor_y<=0):
        cursor_y=1
    #혹시 몰라 -2로 여유 잡아둠
    if(cursor_x>=ori_monitor_width-2):
        cursor_x=ori_monitor_width-2
    if(cursor_y>=ori_monitor_height-2):
        cursor_y=ori_monitor_height-2
    
    return cursor_x,cursor_y
#==========================================

#============ 카메라 대용 이미지 반환============
def fakeFrame():
    img = cv2.imread('hand.png',cv2.IMREAD_REDUCED_COLOR_2)

    return img
#===============================================

#===카메라 열고 사이즈 지정====
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,half_monitor_width )
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, half_monitor_height)
#============================

print('@@@ press \'ESC\' to quit @@@')
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ 메인 루프 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
try:
    #카메라 작동 중에...
    #i=1
    while cap.isOpened():
        #카메라 한 프레임 받아서 ret= true&false, frame= 이미지 저장
        opened, cam_frame = cap.read()

        if not opened:
            break
        
        cam_x,cam_y,state=handCursor(cam_frame)

        #screen_frame=screenCapture()
        #cv2.imshow('monitor',screen_frame)

        #state 0 : 카메라에 손 안잡힘.   1 : 손 보임.     2 : 클릭 제스쳐 취함.     + 얘네 열거형으로 관리하기
        # 아래 상태 출력 코드 함수로 만들어 관리하기
        if state==0:
            print('\r+++++ mouse mode +++++'.ljust(30),end='')
            
        elif state>=1:
            mon_x,mon_y = monitorArea(cam_x,cam_y)
            cursorMove(mon_x,mon_y)
            #end=''는 문자열 출력 후 다음 줄로 넘어가지 않고 바로 이어서 출력하도록 함. \r은 캐리지 리턴. flush=True는 버퍼 바로 출력함. rjsut(n)는 n자리 고정출력.
            #print('\rhand mouse : ',str(mon_x).rjust(4),':',str(mon_y).rjust(4), end='',flush=True)

        if cv2.waitKey(1) == 27:
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
