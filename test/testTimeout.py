#coding:utf8
import os
import urllib2
import time
import socket
import logging
from logging.handlers import SMTPHandler
import smtplib
from email.mime.text import MIMEText

lastTime = 0
while True:
    try:
        ret = urllib2.urlopen("http://localhost:9003/login", None, 15)
        code = ret.getcode()
        print code, ret
    except socket.timeout, e:
        print "connection time out"
        print "trying restart server"


        now = time.localtime()
        cur = time.time()
        if cur - lastTime >= 3600:
            lastTime = cur

            fromAddr = "liyonghelpme@gmail.com"
            toAddrs = ['233242872@qq.com']

            #msg = ('From: %s\r\nTo: %s\r\n' % (fromAddr, ','.join(toAddrs)))
            msg = "server break at %d %d %d %d %d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min)
            msg = MIMEText(msg)
            msg['Subject'] = "server break down"
            msg['From'] = 'liyonghelpme@gmail.com'
            msg['To'] = toAddrs[0]
            smtpClient = smtplib.SMTP('localhost')
            smtpClient.set_debuglevel(1)
            smtpClient.sendmail(fromAddr, toAddrs, msg.as_string())
            smtpClient.quit()

        hostPort = 9003
        os.system('netstat -anp | grep %s > tempPort' % (hostPort))
        l = open('tempPort').readlines()
        print('tempPort', l)
        pid = None
        if len(l) > 0:
            for i in l:
                if i[:3] == 'tcp':
                    i = i.split()
                    pid = int(i[6].split('/')[0])
                    break
        if pid != None:
            os.system('kill %d' % (pid))
        os.system("cd ../;  python app.py & ")
        

    except urllib2.URLError, e:
        print "urlerror"
        print e.reason
        #通常的404 错误
    except KeyboardInterrupt:
        break
    except:
        print "other errors"
        
    time.sleep(5)

        