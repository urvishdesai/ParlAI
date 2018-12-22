import praw
import pprint
from praw.models import MoreComments
import datetime as dt
import requests

#Initialize Reddit object to query into the subreddit
reddit = praw.Reddit(client_id='YOyRRjx4uICZSQ',
                     client_secret='u4CXyYGC0lc6THzWoJ9Njcgj93o',
                     user_agent='my user agent')
#############################################################################################
#Writing the post IDs of a batch onto a file to be used later to retrieve their posts
def file_write(file_name,ids_datetime) :
    fp = open(file_name,'w')
    for x in ids_datetime :
        fp.write(x[0] + "\n")   

#Obtaining IDs of posts within the required date range
def get_ids(resp_json_data) :
    ids_datetime = []
    global reddit
    for x in resp_json_data :
        sub = reddit.submission(x['id'])
        #Ignoring posts with no comments or deleted content
        if (x['num_comments'] != 0 and sub.selftext != '[removed]' and sub.selftext != '[deleted]') :
            ids_datetime.append([x['id'],x['created_utc']])
#            print(x['id'])
    return ids_datetime

#Obtaining post objects for each of the posts within the required date range
def get_posts_for_time_period(sub, beginning, end=int(dt.datetime.now().timestamp())):
    url = "https://apiv2.pushshift.io/reddit/submission/search/" \
               "?subreddit={0}" \
               "&limit=1000" \
               "&after={1}" \
               "&before={2}".format(sub, beginning, end)
    response = requests.get(url)
    resp_json = response.json()    
    return get_ids(resp_json['data'])
##############################################################################################
beginning_timestamp = int(dt.datetime(year=2013, month=1, day=1).timestamp())
end_timestamp = int(dt.datetime(year=2015, month=9, day=1).timestamp())
ids_datetime = get_posts_for_time_period("changemyview", beginning_timestamp, end_timestamp)

i = 0
num_posts = 0
while len(ids_datetime) :
    file_name = "Batch" + str(i) + ".txt"
    print ("Batch ",i,": Number of post_ids rerieved = ",len(ids_datetime))
    num_posts += len(ids_datetime)
    file_write(file_name,ids_datetime)
    beginning_timestamp = ids_datetime[-1][1]                           #Timestamp of last post of previous batch
#    print (dt.datetime.fromtimestamp(beginning_timestamp))
    ids_datetime = get_posts_for_time_period(sub="changemyview", beginning=beginning_timestamp, end=end_timestamp)
    i += 1
print (num_posts)
