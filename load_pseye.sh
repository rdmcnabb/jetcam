#!/bin/bash
# Load PS Eye kernel modules
# Run with: sudo bash load_pseye.sh
# To make permanent, see install instructions below.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODULE_DIR="$SCRIPT_DIR/kernel_module/gspca"

echo "Loading PS Eye kernel modules..."

modprobe videodev
modprobe videobuf2-common
modprobe videobuf2-v4l2
modprobe videobuf2-vmalloc

insmod "$MODULE_DIR/gspca_main.ko" && echo "  gspca_main loaded"
insmod "$MODULE_DIR/gspca_ov534.ko" && echo "  gspca_ov534 loaded"

sleep 1
if [ -e /dev/video0 ]; then
    echo "SUCCESS: PS Eye available at /dev/video0"
else
    echo "WARNING: /dev/video0 not found - check dmesg for errors"
fi

# To load automatically on boot:
#   sudo cp kernel_module/gspca/gspca_main.ko /lib/modules/$(uname -r)/extra/
#   sudo cp kernel_module/gspca/gspca_ov534.ko /lib/modules/$(uname -r)/extra/
#   sudo depmod -a
#   echo -e "gspca_main\ngspca_ov534" | sudo tee /etc/modules-load.d/pseye.conf
