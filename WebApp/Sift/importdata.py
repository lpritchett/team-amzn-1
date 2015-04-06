__author__ = 'MaxGoovaerts'

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except:
    pass

# from models import *
import logging
from time import time
from datetime import datetime

DATA_FILES = ['data/expSForums' + str(i) + '.cvs' for i in range(1, 11)]


def get_post_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT Count(*) FROM sellerforums.Post")
    return cur.fetchone()


def commitPost(post, conn):
    cur = conn.cursor()
    query = "INSERT INTO Post (threadId, messageId, forumId, userId, categoryId, subject, body, postedByModerator," \
            " resolutionState, helpfulAnswer, correctAnswer, userName, userPoints, creationDate, modificationDate, locale) VALUES "
    query += "(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        # posts need to be encoded to avoid weird character breaking errors
        cur.execute(query, (post[0], post[1], post[2], post[3], post[4], post[5].encode('utf-8', 'ignore'), post[6].encode('utf-8', 'ignore'),
                            post[7], post[8], post[9], post[10], post[11].encode('utf-8', 'ignore'), post[12], post[13], post[14], post[15]))
        conn.commit()
        return 0
    except:
        return 1
        pass
    return 0

# this function converts the provided time format to the mysql date format
# necessary for storing properly


def convertTime(input):
    date_obj = datetime.strptime(input, '%m/%d/%y')
    return date_obj.strftime('%Y/%m/%d')


def main():
    # Display progress logs on stdout
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s')

    # print("Creating Database")
    #conn = pymysql.connect(host='sellerforums.cqtoghgwmxut.us-west-2.rds.amazonaws.com', port=3306, user='teamamzn', passwd='TeamAmazon2015!', db='sellerforums')
    conn = pymysql.connect(host='siftmsu.cqtoghgwmxut.us-west-2.rds.amazonaws.com',
                           port=3306, user='teamamzn', passwd='TeamAmazon2015!', db='sellerforums')

    print("Importing Data")
    # set up variables
    t0 = time()
    i = 0
    j = 500
    errors = 0
    cur = conn.cursor()
    cur.execute(
        "SELECT threadId, messageId from Post ORDER by postId desc LIMIT 1")
    delta = cur.fetchone()
    caughtup = 1
    # if(delta is None):
    #    caughtup = 1
    # else:
    #    delta = str(delta[0]) + str(delta[1])
    #    caughtup = 0

    for f in DATA_FILES:
        p = 0
        print("Reading Data File: " + str(f))
        with open(f, encoding="utf-8", errors="surrogateescape") as data_file:
            while True:
                parse = lambda i: i if '=' in i else '=\n'
                data = [parse(data_file.readline()).split('=', 1)[1].rstrip()
                        for i in range(17)][:-1]

                # confirm that not eof
                if data[0]:
                    i += 1
                    p += 1
                else:
                    break

                if(caughtup == 1):
                    data[13] = convertTime(data[13])
                    data[14] = convertTime(data[14])
                    errors += commitPost(data, conn)

                if(caughtup == 0):
                    comp = str(data[0]) + str(data[1])
                    if(delta == comp):
                        caughtup = 1
                        print("CAUGHT UP~~~~~~~~~~~~~")
                if (i - j == 0):
                    j += 300
                    print("% of file: " + str(round(p / 600.0, 3)) + " post: " + str(i) +
                          " time: " + str(round(time() - t0, 2)) + " errors: " + str(errors))

        print("Successfully read " + str(i) + " posts")
    print("Data Imported:")
    print(get_post_count(conn))
    print("done in %fs" % (time() - t0))
    conn.close()

# Only run the main function if this code is called directly
# Not if it's imported as a module
if __name__ == '__main__':
    main()
