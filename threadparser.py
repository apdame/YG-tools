'''
Parses Yahoo Groups messages originally in JSON into e-mail readable format.
Must be placed in folder with JSON files to parse - however, could easily be
modified to work from single location.
'''

import json
import glob, os
import email
import html
import re

redacted = input("Should the archive be redacted [enter Y / N]? ")
seen = set()
threads = dict()
subjects = dict()

def redact(jsonMsg, jsonStr, mid):
    global msg

    #If chosen, redact identifying information from message headers to limit mass
    #data scraping.
    if redacted.lower() == "y" or "yes":
        msgcontent = email.message_from_string(jsonStr)
        #Use email module to parse and redact headers with possible identifying info
        #Note that content of headers is somewhat inconsistent from message to message,
        #so deletion is inclusive for all possible headers with identifying information.
        #Even if redaction is not chosen, headers do not in many cases contain
        #full e-mail addresses, but only the handle before "@".
        del msgcontent['from'], msgcontent['to'], msgcontent['cc'], msgcontent['return-path'], msgcontent['x-sender'], msgcontent['X-Yahoo-Profile']
        msgstr = "Post #%s:\n\n%s" % (mid, msgcontent)
        #Unescape HTML character codes
        msg = html.unescape(msgstr)
    else:
        msgcontent = email.message_from_string(jsonStr)
        msgstr = "Post #%s:\n\n%s" % (mid, msgcontent)
        #Unescape HTML character codes
        msg = html.unescape(msgstr)

    return msg

def threadparse(tid, mid, msg, threadSub):
    #Collects messages into threads, based on existing thread ID,
    #which is identical to the Message ID of the first message in
    #the thread. Also assigns each thread a subject for use in the
    #filename.
    if tid in seen:
        threads[tid].append(msg)
    else:
        threads[tid] = [msg]
        subjects[tid] = threadSub
    #Adds message to set of processed messages, so downthread messaages
    #can be matched with the initial post.
    seen.add(mid)

def parser():
    global jsonMsg
    global jsonStr
    global tid
    global mid
    global subject

    read_files = glob.glob("*.json")
    threads = dict()
    for f in read_files:
        with open(f, 'r', encoding="utf8") as current_file:
            #Collect data for functions
            raw = current_file.read()
            jsonMsg = json.loads(raw)
            #Collect Topic ID numbers
            tid = str(jsonMsg['ygData']['topicId'])
            #Collect Message ID numbers
            mid = str(jsonMsg['ygData']['msgId'])
            #Get raw email from JSON
            jsonStr = str(jsonMsg['ygData']['rawEmail'])
            #Get message subject
            if 'subject' in jsonMsg['ygData']:
                threadSub = str(jsonMsg['ygData']['subject'])
            else:
                threadSub = "No Subject"
            #Process text
            redact(jsonMsg, jsonStr, mid)
            threadparse(tid, mid, msg, threadSub)

    return jsonMsg
    return jsonStr
    return tid
    return mid
    return threadSub

def main():
    parser()
    #Write each thread to an individual, labeled textfile
    for key, value in threads.items():
        #Get and clean up subjects for file title
        if key in subjects:
            titleSub = str(subjects[key])
            #Shorten title to fit filename length limits
            titleShort = titleSub[:100] + (titleSub[100:] and '...')
            #Escape unusable characters from filename, like "?"
            title = re.sub('[^\w\-_\. ]', '_', titleShort)
        with open('Thread #%s - %s.txt' % (key, title), 'w', encoding='utf-8') as msgfile:
            #Write thread to textfile
            threadcount = len(value)
            msgfile.write("Number of Posts in Thread: %s\n\n" % threadcount)
            for item in value:
                if item in value[:-1]:
                    msgfile.write("%s\n\n-------Next Post in Thread-------\n\n" % item)
                else:
                    msgfile.write("%s" % item)

if __name__=="__main__":
   main()
