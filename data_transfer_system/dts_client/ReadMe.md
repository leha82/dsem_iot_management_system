
# 라즈베리파이 블루투스 설정

1. 블루투스 패키지 설정
  $ sudo apt install bluetooth blueman bluez
  $ sudo apt install python-bluetooth
  $ sudo reboot
  
2. 블루투스 모듈 설치
  $ sudo apt install bluetooth bluez libbluetooth-dev
  $ sudo apt install sudo python3 -m pip install pybluez
  
3. 블루투스 다시 연결
  $ sudo nano /boot/config.txt 
  // 위 파일로 이동 후 아래 문장을 지우고 재부팅
     # disable Bluetooth
     # dtoverlay=pi3-disable-bt

4. 라즈베리파이 블루투스 페어링하기
  $ sudo bluetoothctl
  # scan on
  # pair [블루투스 모듈 Mac 주소]  // 패스워드는 기본 '1234'
