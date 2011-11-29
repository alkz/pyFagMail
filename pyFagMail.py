
#===============================================================================
#
#	 FILE:  pyFagMail.py
#
#	USAGE:  python pyFagMail.py <confFile>
#
#   DESCRIPTION:  This script simply connects to your IMAP email server and 
#                 downloads emails, I wrote this stuff just because I've been 
#                 annoying each time open my browser, connect to gmail and 
#                 check my email.
#                 With this shit and screen I can check them more quickly when 
#                 I'm working.
#                 To make work this gay you need to give it a .conf file.
#
#                 Example of confFile:
#           
#                     imap   imap.gayland.gay
#                     port   993
#
#                     account    fag@faggotree.fg
#                     psw        squirtle
#
#                     n_emails   15
#                     mailbox    INBOX 
#                     max_col    106    # Max length for each rows 
#                     refresh    15     # Refresh email
#
#
#      OPTIONS:  ---
# REQUIREMENTS:  ---
#	NOTES:  ---
#       AUTHOR:  alkz
#      COMPANY:  faggotree
#      VERSION:  0.2
#      CREATED:  01/11/2011 23:36:35
#     REVISION:  ---
#      LICENCE:  GNU GPL v.3
#===============================================================================


import imaplib
import email
import sys
import os
import signal



if (len(sys.argv) < 2):
    print "Gimme the .conf file FAG"
    print "Usage: python pyFagMail.py <confFile>"
    sys.exit(-1)

f = file(sys.argv[1], 'r')
s = f.read()
l = s.split('\n')

conf = {}
for e in l:
    if (e != ''):
        tmp = e.split()
        conf[tmp[0].strip()] = tmp[1].strip()



Colors = {  
            'RED': '\033[31m',
            'BLINK': '\033[5m',
            'LIGHTBLUE': '\033[1;34m',
            'ENDC': '\033[0m'
         }
choice = 0



def getMails(imap, total):
    global conf

    mails = []
    for n in range( int(conf['n_emails']) ):
        curr = imap.fetch(total-n, '(RFC822)')[1][0][1]
        msg = email.message_from_string(curr)
        s = ''
        try:
            if (msg['Content-type'].find('multipart') >= 0):
                for p in msg.walk():
                    if(p.get_content_type() == 'text/plain'):
                        s += p.get_payload()
            else:
                s += msg.get_payload()
        except:
            pass    

        msg['Content'] = s
        mails.append(msg)

    return mails 



def adjustS(s):
    global conf

    i = s.find('<')
    if (i >= 0):
        j = s.find('>', i+1)
        new_s = "From: " + s[i+1:j] + s[j+1:]
    else:
        new_s = s

    if(len(new_s) > int(conf['max_col'])):
        new_s = new_s[:int(conf['max_col'])-3] + "..."
    return new_s



def getInput():
    try:
        return raw_input()
    except:
        pass
    return

    


#===============================================================================



signal.signal(signal.SIGALRM, getInput)

print ("Connecting..."),

try:
    sock = imaplib.IMAP4_SSL(conf['imap'], int(conf['port']))
    sock.login(conf['account'], conf['psw'])
except:
    print ("Could not connect")
    sys.exit(0);

print ("Connected!")
print ("Gettin' mails...")
prev = int(sock.select(conf['mailbox'])[1][0])
mails = getMails(sock, prev)


while (1):

    changed = False
    num = int(sock.select(conf['mailbox'])[1][0])

    if (num != prev):
        diff = num - prev
        prev = num
        changed = True
        mails = getMails(sock, num)
    
    os.system('clear')
    print "# Last " + conf['n_emails'] + " Emails #\n"
    i = 0
    for mail in mails:
        toPrint = "From: " + mail['From'] + " | Subject: " + mail['Subject'] + " | Date: " + mail['Date']
        toPrint = adjustS(toPrint)
        if (changed and diff):
            print "[" + str(i) + "]" + " - " + Colors['LIGHTBLUE'] + Colors['BLINK'] + toPrint[:len(toPrint)-5] + Colors['RED'] + " NEW!" + Colors['ENDC'] 
            diff -= 1
        else:
            print "[" + str(i) + "]" + " - " + toPrint
        i += 1
    
    if not changed:
        signal.alarm(int(conf['refresh']))
        choice = getInput()
        signal.alarm(0)
    else:
        choice = getInput()
        
    if (choice == 'e'):
        sock.logout()
        sys.exit(0)

    elif(choice == '\n' or choice == '' or choice == None):
        continue

    elif (int(choice) < int(conf['n_emails']) and int(choice) >= 0):
        os.system('clear')
        tmpF = open("tmpF", "w")
        print >> tmpF, mails[int(choice)]['Content']
        os.system("more tmpF")
        raw_input()

    
