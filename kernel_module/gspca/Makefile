KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

obj-m += gspca_main.o
obj-m += gspca_ov534.o

gspca_main-objs := gspca.o autogain_functions.o
gspca_ov534-objs := ov534.o

EXTRA_CFLAGS += -I$(PWD)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	sudo cp gspca_main.ko gspca_ov534.ko /lib/modules/$(shell uname -r)/extra/
	sudo depmod -a

load:
	sudo modprobe videodev
	sudo insmod gspca_main.ko
	sudo insmod gspca_ov534.ko

unload:
	-sudo rmmod gspca_ov534
	-sudo rmmod gspca_main
