#!/bin/bash
#
# ssh_passwordless_login.sh
#
# via http://www.thegeekstuff.com/2008/11/3-steps-to-perform-ssh-login-without-password-using-ssh-keygen-ssh-copy-id/

ssh-copy-id -i ~/.ssh/id_rsa.pub pi@192.168.1.169
