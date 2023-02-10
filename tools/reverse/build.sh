#! /bin/sh

set -e

[ -f "reverseme.exe" ] && rm reverseme.exe
[ -f "project.zip" ] && rm project.zip

[ ! -f "reverseme.c" ] && echo ! Cannot find the file 'reverseme.c' && exit 1

echo 1* Building binary reverseme.exe
gcc reverseme.c -o reverseme.exe

echo 2* Compressing project.zip
echo password : 'gokayak'
zip -re project.zip reverseme.exe

