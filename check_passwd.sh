#!/usr/bin/env bash

if [[ ! $(whoami) =~ "root" ]]; then
echo ""
echo "**********************************"
echo "*** This should be run as root ***"
echo "**********************************"
echo ""
exit
fi

if [[ -z $1 ]]; then
echo "Usage: ./check_passwd.sh USERNAME"
exit
fi

user_data=`cat /etc/shadow | grep $1`
password_data=`echo "$user_data" | awk -F':' ' { print $2 } '`
salt=`echo "$password_data" | awk -F'$' ' { print $3 } '`
hash=`echo "$password_data" | awk -F'$' ' { print $4 } '`
echo "$password_data"
echo "$hash"
openssl passwd -1 -salt $salt
