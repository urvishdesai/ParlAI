import os
import praw
import pprint
from praw.models import MoreComments
import datetime as dt
import time
###########################################################################################
#Wrapping quotations of previous comments/replies within quotes
def quotes(text):
    while '>' in text :
        quote_start = text.find('>')
        quote_end = text[quote_start:].find('\n') + quote_start
        text = text.replace('>','"',1)
        text = text[:quote_end] + '"-' + text[quote_end+1:]
    return text.lower()

#Formatting a comment tree in a DFS manner as per ParlAI's specifications
def process_comments(comment_tree, text, file_ptr):
    for comment in comment_tree:
        if type(comment).__name__ == "Comment" :
            #If reached the leaf of the comment tree, write into file 
            if(not comment.replies) :
                #Limit on the number of comments on a thread to avoid lengthy ones
                if (len(text) < 7) :
                    for i in range(len(text)-1) :
                        file_ptr.write("\ntext: " + text[i].replace("\n"," ").replace("\t"," ") + "\tlabels: " + text[i+1].replace("\n"," ").replace("\t"," "))
                    file_ptr.write("\ntext: " + text[-1].replace("\n"," ").replace("\t"," ") + "\tlabels: " + quotes(comment.body).replace("\n"," ").replace("\t"," "))
                    file_ptr.write("\tepisode_done:True\n")
            #If there are child nodes in the comment thread
            else :
                #If the comment is not deleted/removed or not too long, processing its replies
                if (comment.body != '[deleted]' and len(comment.body) < 120) :
                    process_comments(comment.replies,text + [quotes(comment.body)],file_ptr)
                else:
                    process_comments(comment.replies, text, file_ptr)
        #If there are more comments (at same level) to be processed
        elif type(comment).__name__ == "MoreComments":
            process_comments(comment.comments(),text,file_ptr)
###########################################################################################
#Initialize Reddit object to query into the subreddit
reddit = praw.Reddit(client_id = 'YOyRRjx4uICZSQ',
                     client_secret = 'u4CXyYGC0lc6THzWoJ9Njcgj93o',
                     user_agent = 'my user agent')
                     
subreddit = reddit.subreddit('changemyview')
num_processed = 0
mod_count = 0
flag = True
path = "./val_data/"    #./train_data/   ./test_data/
#os.mkdir(path)
file_ptr = open(path + "10k_shortened_val_data.txt",'w')
for i in range(5) :
    file_name = "./val_data/Batch" + str(i) + ".txt"            #"./train_data/Batch"   "./test_data/Batch"
    fp = open(file_name,'r')
    for line in fp :
        submission = reddit.submission(id = line)
        if (submission.title[:4].lower() == '[mod'):
            mod_count += 1
            num_processed -= 1
            continue
        text = [submission.title.lower() + " " + submission.selftext.lower()]
        print ("Post ",line," formatted")
        process_comments(submission.comments,text,file_ptr)
        num_processed += 1
        if (num_processed == 300) :
            flag = False
            break
    print ("Number of posts processed = ",num_processed)
    print ("Batch",i,"processed") 
    if (flag == False) :
        break
file_ptr.close()
