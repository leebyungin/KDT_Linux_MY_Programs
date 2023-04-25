#openCV 임포트
import cv2		
#rasberryPi GPIO 임포트		
import RPi.GPIO as rg

#cma1에 카메라 객체 저장
cam1=cv2.VideoCapture(0)
#카메라 너비 1024, 높이 768 설정.(적절하게 설정하지 않으면 촬영이 이상하게 돼, 원의 판별 정확도가 떨어졌었습니다.)
cam1.set(cv2.CAP_PROP_FRAME_WIDTH,1024)
cam1.set(cv2.CAP_PROP_FRAME_HEIGHT,768) 

#GPIO 출력에 사용할 핀 설정
led1=27
#GPIO모드 BroadCoM으로 설정
rg.setmode(rg.BCM)
rg.setup(led1,rg.OUT)

#카메라에 감지된 게 무엇인지 저장. 0: 사각형 1: 원 2: lastState초기값
circleState=0
lastState=2

#루프 시작 알림
print('input \'q\' to exit :')
#50ms동안 키보드 입력을 감지. q입력시 while문 종료. ord()함수는 단일 문자를 아스키 코드 값으로 변환
while cv2.waitKey(50)!=ord('q'):
	
	#카메라에 찍힌걸 불러옴
	ret,frame=cam1.read() 
	#찍힌 게 없다면 break
	if not ret: break

	#이미지를 흑백으로 변환
	gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
	#이미지를 블러처리
	blur=cv2.GaussianBlur(gray,(15,15),0)

	#블러된 이미지를 화면에 보여줌
	cv2.imshow('myBlurFrame',blur)
	#흑백 이미지를 화면에 보여줌
	cv2.imshow('myGrayFrame',gray)

	#블러 처리된 이미지를 이용해 원이 찍혔는지 판별함
	circles=cv2.HoughCircles(blur,cv2.HOUGH_GRADIENT,2,100,param1=100,param2=100,minRadius=35,maxRadius=500)

	#원이라면 1, 원이 아니라면 0을 circleState에 저장함
	if circles is not None:
		circleState=1
	else:
		circleState=0

	#이번 판별 결과가 지난번 결과와 다르다면...
	if circleState!=lastState:
		#이번 판별 결과가 원이라면...
		if circleState:
			#모니터에 is circle! 출력
			print('is circle!')
			#핀에 HIGH 인가
			rg.output(led1,rg.HIGH)

		#이번 판별 결과가 원이 아니라면...
		else:
			print('is NOT circle!')
			rg.output(led1,rg.LOW)
		
		#lastState를 이번 판별 결과로 업데이트
		lastState=circleState

#카메라 인스턴스 반납
cam1.release()
#imshow로 화면에 보여주던 이미지 윈도우 제거
cv2.destroyAllWindows()
#gpio 종료
rg.cleanup()

#프로그램 종료 알림
print('program terminated')