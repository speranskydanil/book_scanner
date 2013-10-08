#!/bin/sh

if [ $(whoami) != 'root' ]
then
  echo 'you must be root user'
  exit
fi

echo
echo 'updating sources'
echo '--------------------------------------------------------------------------------'
echo

apt-get update

echo
echo 'removing gphoto2 if exists'
echo '--------------------------------------------------------------------------------'
echo

apt-get remove -y gphoto2

echo
echo 'installing dependencies'
echo '--------------------------------------------------------------------------------'
echo

apt-get install -y libltdl-dev libusb-dev libexif-dev libpopt-dev

echo
echo 'creating temporary directory'
echo '--------------------------------------------------------------------------------'
echo

mkdir gphoto2-temporary-directory
cd gphoto2-temporary-directory

echo
echo 'downloading libusb 1.0.11'
echo '--------------------------------------------------------------------------------'
echo

wget http://ftp.de.debian.org/debian/pool/main/libu/libusbx/libusbx_1.0.11.orig.tar.bz2
tar xjvf libusbx_1.0.11.orig.tar.bz2
cd libusbx-1.0.11

echo
echo 'installing libusb 1.0.11'
echo '--------------------------------------------------------------------------------'
echo

./configure
make
make install
cd ..


echo
echo 'downloading libgphoto2 2.5.2'
echo '--------------------------------------------------------------------------------'
echo

wget http://downloads.sourceforge.net/project/gphoto/libgphoto/2.5.2/libgphoto2-2.5.2.tar.bz2
tar xjf libgphoto2-2.5.2.tar.bz2
cd libgphoto2-2.5.2

echo
echo 'installing libgphoto2 2.5.2'
echo '--------------------------------------------------------------------------------'
echo

./configure
make
make install
cd ..

echo
echo 'downloading gphoto2 2.5.2'
echo '--------------------------------------------------------------------------------'
echo

wget http://downloads.sourceforge.net/project/gphoto/gphoto/2.5.2/gphoto2-2.5.2.tar.gz
tar xzvf gphoto2-2.5.2.tar.gz
cd gphoto2-2.5.2

echo
echo 'installing gphoto2 2.5.2'
echo '--------------------------------------------------------------------------------'
echo

./configure
make
make install
cd ..

echo
echo 'linking libraries'
echo '--------------------------------------------------------------------------------'
echo

ldconfig

echo
echo 'removing temporary files'
echo '--------------------------------------------------------------------------------'
echo

cd ..
rm -rf gphoto2-temporary-directory

echo
echo 'done'
echo '--------------------------------------------------------------------------------'
echo

gphoto2 --version
gphoto2 --help

