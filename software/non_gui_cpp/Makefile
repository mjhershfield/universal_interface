SHELL=cmd

all:
	make clean
	make library
	make gui
	make notification_testing

library: ./src/lycan.cpp ./src/lycan.h
	g++ -g -c ./src/lycan.cpp -L ./build -l FTD3XX -o ./build/lycan.o
	ar rcs ./build/liblycan.a ./build/lycan.o

gui: ./src/gui.cpp
	g++ -g ./src/gui.cpp -L ./build -l lycan -l FTD3XX -o ./build/gui

notification_testing: ./src/notification_testing.cpp
	g++ ./src/notification_testing.cpp -L ./build -l lycan -l FTD3XX -o ./build/notification_testing

clean:
	cd build && del *.a && del *.o && del *.exe