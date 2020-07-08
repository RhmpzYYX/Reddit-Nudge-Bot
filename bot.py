import praw
import time
import threading
from configs import settings
from praw.exceptions import RedditAPIException

reddit = praw.Reddit(client_id=settings.get("client_id"),
                     client_secret=settings.get("client_secret"),
                     user_agent=settings.get("user_agent"),
                     username=settings.get("username"),
                     password=settings.get("password"))

subreddit = reddit.subreddit(settings.get("subreddit"))

def nudgeUsers():
    '''
    Searches through the comments of the most recent submissions for keyword !Nudge and nudges users through private messaging 
    '''
    for submission in subreddit.new(limit=36):
        for comment in submission.comments:
            if hasattr(comment, "body"):
                flag = False
                if ("!Nudge" in comment.body):
                    sentenceList = comment.body.split()
                    #Edge check if last word of the comment is !Nudge which results in an invalid user
                    if (sentenceList[-1] == "!Nudge"):
                        continue
                    author = comment.author
                    #Avoids infinite response to keyword
                    if (author == settings.get("username")):
                        continue
                    #Avoids duplicate responses to same comment containing keyword
                    for response in comment.replies:
                        if hasattr(response, "body"):
                            if (response.author == settings.get("username")):
                                flag = True
                                break
                    if (not flag):
                        print(comment.body)
                        usernameIndex = sentenceList.index("!Nudge")
                        receivingUser = sentenceList[usernameIndex+1]
                        #Corrects Reddit name formatting for underscores
                        receivingUser = receivingUser.replace("\\_", "_")
                        try:
                            comment.reply("You nudged /u/{}".format(receivingUser))
                            reddit.redditor(receivingUser).message("{} nudged you".format(author), "{}".format(comment.permalink))
                            print("Nudge successful")
                        except RedditAPIException as exception:
                            print(exception)


def instruct():
    '''
    Searches through the comments of the most recent submissions and comments the instructions for the bot if the comment only contains !NudgeBot
    '''
    for submission in subreddit.new(limit=36):
        for comment in submission.comments:
            if hasattr(comment, "body"):
                if ("!NudgeBot" in comment.body):
                    sentence = "".join(comment.body.split())
                    try:
                        if (sentence == "!NudgeBot"):
                            comment.reply("Hi! You can comment !Nudge [Username_of_user_here (without the /u/)] under a post to nudge someone :)")
                            print("Comment successful")
                    except RedditAPIException as exception:
                        print(exception)        


def main():
    thread1 = threading.Thread(target=nudgeUsers)
    thread2 = threading.Thread(target=instruct)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    finish = time.perf_counter()
    print("Finish time: {} seconds".format(finish))


if (__name__ == "__main__"):
    main()