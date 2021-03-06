#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template
#from datetime import datetime
#from flask import Flask, request, flash, url_for, redirect, \
#     render_template, abort
from flaskext import *
from module import *

import MySQLdb
import os, sys, time, datetime
import json
import logging
from calendar import monthrange
import config
import module

"""
HOST = 'localhost'
DATABASE = 'nozomi'
DEBUG = True
PASSWORD = '2e4n5k2w2x'
"""


reload(sys)
sys.setdefaultencoding('utf-8') 

app = Flask(__name__)
app.config.from_object("config")


def getConn():
    return MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')

dailyModule = DailyModule("nozomi_user_login")
achieveModule = AchieveModule("nozomi_achievement")

statlogger = logging.getLogger("STAT")
f = logging.FileHandler("stat.log")
statlogger.addHandler(f)
formatter = logging.Formatter("%(asctime)s\t%(message)s")   
f.setFormatter(formatter)
statlogger.setLevel(logging.INFO)

crystallogger = logging.getLogger("CRYSTAL")
f = logging.FileHandler("crystal_stat.log")
crystallogger.addHandler(f)
formatter = logging.Formatter("%(asctime)s\t%(message)s")   
f.setFormatter(formatter)
crystallogger.setLevel(logging.INFO)


debugLogger = logging.FileHandler("error2.log")
debugLogger.setLevel(logging.INFO)
app.logger.addHandler(debugLogger)



@app.errorhandler(501)
def user_not_login(error):
    return redirect(url_for('login'))

dataBuilds = [
              [1, 170018, 1, 1, 0, 1500, "{\"oil\":1000,\"food\":1000}"],
              [2, 110009, 2, 0, 0, 0, ""],
              [3, 130025, 2002, 1, 0, 400, "{\"resource\":500}"],
              [4, 250019, 2005, 1, 0, 400, "{\"resource\":100}"],
              [5, 240023, 2004, 1, 0, 250, "{\"resource\":1}"],
              [6, 180025, 1000, 1, 0, 400, ""],
              [7, 150030, 3000, 1, 0, 400, ""],
              [8, 10031, 1004, 1, 0, 400, ""],
              [9, 350003, 1003, 0, 0, 0, ""],
              [10, 40008, 4013, 1, 0, 0, ""],
              [11, 60005, 4007, 1, 0, 0, ""],
              [12, 90009, 4012, 1, 0, 0, ""],
              [13, 90011, 4006, 1, 0, 0, ""],
              [14, 110006, 4014, 1, 0, 0, ""],
              [15, 110012, 4009, 1, 0, 0, ""],
              [16, 140009, 4002, 1, 0, 0, ""],
              [17, 140011, 4004, 1, 0, 0, ""],
              [18, 170008, 4012, 1, 0, 0, ""],
              [19, 160004, 4007, 1, 0, 0, ""],
              [20, 30017, 4008, 1, 0, 0, ""],
              [21, 30024, 4000, 1, 0, 0, ""],
              [22, 20036, 4009, 1, 0, 0, ""],
              [23, 60029, 4001, 1, 0, 0, ""],
              [24, 100036, 4001, 1, 0, 0, ""],
              [25, 130033, 4003, 1, 0, 0, ""],
              [26, 180035, 4002, 1, 0, 0, ""],
              [27, 100021, 4007, 1, 0, 0, ""],
              [28, 250012, 4001, 1, 0, 0, ""],
              [29, 300017, 4014, 1, 0, 0, ""],
              [30, 300023, 4012, 1, 0, 0, ""],
              [31, 220003, 4004, 1, 0, 0, ""],
              [32, 270006, 4002, 1, 0, 0, ""],
              [33, 250030, 4009, 1, 0, 0, ""],
              [34, 250035, 4004, 1, 0, 0, ""],
              [35, 210038, 4008, 1, 0, 0, ""],
              [36, 350001, 4008, 1, 0, 0, ""],
              [37, 350007, 4008, 1, 0, 0, ""],
              [38, 370001, 4012, 1, 0, 0, ""],
              [39, 370007, 4013, 1, 0, 0, ""],
              [40, 330003, 4001, 1, 0, 0, ""],
              [41, 390003, 4000, 1, 0, 0, ""],
              [42, 330005, 4012, 1, 0, 0, ""],
              [43, 390005, 4012, 1, 0, 0, ""],
              [44, 370020, 4004, 1, 0, 0, ""],
              [45, 370024, 4012, 1, 0, 0, ""],
              [46, 340029, 4001, 1, 0, 0, ""],
              [47, 360033, 4003, 1, 0, 0, ""],
              [48, 330036, 4008, 1, 0, 0, ""],
              [49, 370037, 4014, 1, 0, 0, ""],
              [50, 20002, 4003, 1, 0, 0, ""]
              ]

def getUserInfos(uid):
    r = queryOne("SELECT name, score, clan FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2])

def getUserAllInfos(uid):
    r = queryOne("SELECT name, score, clan, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], guide=r[3], crystal=r[4], lastSynTime=r[5], shieldTime=r[6], zombieTime=r[7], obstacleTime=r[8])

def updateUserInfoById(params, uid):
    sql = "UPDATE nozomi_user SET "
    isFirst = True
    paramList = []
    for key, value in params.items():
        if isFirst:
            isFirst = False
        else:
            sql = sql+","
        sql = sql + key + "=%s"
        paramList.append(value)
    sql = sql + " WHERE id=%s"
    paramList.append(uid)
    update(sql, paramList)

def getJsonObj(string):
    if string=="":
        return None
    else:
        return json.loads(string)
    
def getUserBuilds(uid):
    builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM nozomi_build WHERE id=%s AND state=0", (uid))
    return builds

def deleteUserBuilds(uid, buildIndexes):
    params = []
    for bindex in buildIndexes:
        params.append([uid, bindex])
    executemany("UPDATE nozomi_build SET state=1 WHERE id=%s AND buildIndex=%s", params)

def updateUserBuilds(uid, datas):
    params = []
    for data in datas:
        params.append([uid, data[0], data[1], data[2], data[3], data[4], data[5], data[6]])
    executemany("INSERT INTO nozomi_build (id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend) VALUES(%s,%s,%s,0,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE grid=VALUES(grid),state=0,bid=VALUES(bid),level=VALUES(level),`time`=VALUES(time),hitpoints=VALUES(hitpoints),extend=VALUES(extend);", params)

def getUserResearch(uid):
    researches = queryOne("SELECT research FROM nozomi_research WHERE id=%s", (uid))
    return json.loads(researches[0])

def updateUserResearch(uid, researches):
    update("UPDATE nozomi_research SET research=%s WHERE id=%s", (json.dumps(researches), uid))
    
def updateUserBuildHitpoints(uid, datas):
    params = []
    for data in datas:
        params.append([data[1], uid, data[0]])
    executemany("UPDATE nozomi_build SET hitpoints=%s WHERE id=%s AND buildIndex=%s", params)

def getUidByName(account):
    ret = queryOne("SELECT id FROM nozomi_user WHERE account=%s", (account))
    if ret==None:
        return 0
    else:
        return ret[0]

def initUser(username, nickname):
    print "initUser", username, nickname
    regTime = int(time.mktime(time.localtime()))
    initScore = 500
    uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, score, crystal, shieldTime) VALUES(%s, %s, %s, 500, 497, 0)", (username, regTime, nickname))
    myCon = getConn()
    module.UserRankModule.initUserScore(myCon, uid, initScore)
    module.UserRankModule.updateScore(myCon, uid, initScore)
    myCon.commit()
    myCon.close()

    updateUserBuilds(uid, dataBuilds)
    update("INSERT INTO nozomi_research (id, research) VALUES(%s, '[1,1,1,1,1,1,1,1,1,1]')", (uid))
    newUserState(uid)
    
    return uid

def updateUserState(uid, eid):
    updateUserOnline(uid)
    if eid!=0:
        clearUserAttack(eid)

def setUserClan(uid, cid):
    update("UPDATE nozomi_user SET clan=%s WHERE id=%s", (cid, uid))

def createClan(uid, name, ctype, minScore):
    cid = insertAndGetId("INSERT INTO nozomi_clan (name, type, minScore, creator, members, score) VALUES (%s, %s, %s, %s, 1, 0)", (name, ctype, minScore, uid))
    setUserClan(uid, cid)
    return cid

def addClanMember(cid, uid):
    setUserClan(uid, cid)
    update("UPDATE nozomi_clan SET members=members+1 WHERE id=%s", (cid))

def getClanInfo(cid):
    return queryOne("SELECT name, type, minScore, creator, members, score FROM nozomi_clan WHERE id=%s", (cid))

def getClanMembers(cid):
    ret = queryAll("SELECT id, name, score FROM nozomi_user WHERE clan=%s", (cid))
    return [dict(id=r[0], name=r[1], score=r[2]) for r in ret]

@app.route("/getBattleHistory", methods=['GET'])
def getBattleHistory():
    uid = int(request.args['uid'])
    ret = queryAll("SELECT info, eid, time, videoId, reverged FROM nozomi_battle_history WHERE uid=%s" , (uid))
    if ret==None:
        return "[]"
    else:
        return json.dumps([[json.loads(r[0]), r[1], r[2], r[3], r[4]] for r in ret])

@app.route("/findClans", methods=['GET'])
def findClans():
    ret = queryAll("SELECT id, name, type, minScore, creator, members, score FROM nozomi_clan LIMIT 50")
    if ret==None:
        return "[]"
    return json.dumps([dict(id=r[0], name=r[1], type=r[2], minScore=r[3], members=r[5], score=r[6]) for r in ret])

@app.route("/getClanInfos", methods=['GET'])
def getClanInfos():
    cid = int(request.args['cid'])
    clanInfo = getClanInfo(cid)
    ret = dict(id=cid, name=clanInfo[0], type=clanInfo[1], minScore=clanInfo[2], creator=clanInfo[3], members=clanInfo[4], score=clanInfo[5])
    ret['memberInfos'] = getClanMembers(cid)
    return json.dumps(ret)

@app.route("/createClan", methods=['POST'])
def createSelfClan():
    if 'uid' not in request.form:
        return json.dumps(dict(code=401, msg="user id require"))
    if 'name' not in request.form:
        return json.dumps(dict(code=401, msg="clan name require"))
    uid = int(request.form['uid'])
    name = request.form['name']
    cid = createClan(uid, name, 0, 0)
    return json.dumps(dict(code=0, cid=cid))

@app.route("/searchClan", methods=['GET'])
def searchClan():
    match = request.args['match']
    ret = queryAll("SELECT id, name, type, minScore, creator, members, score FROM nozomi_clan WHERE name LIKE %s", ("%"+match+"%"))
    if ret==None:
        return "[]"
    return json.dumps([dict(id=r[0], name=r[1], type=r[2], minScore=r[3], members=r[5], score=r[6]) for r in ret])

@app.route("/joinClan", methods=['POST'])
def joinClan():
    if 'cid' not in request.form:
        return json.dumps(dict(code=401, msg="clan id require"))
    if 'uid' not in request.form:
        return json.dumps(dict(code=401, msg="user id require"))
    cid = int(request.form['cid'])
    uid = int(request.form['uid'])
    clanInfo = getClanInfo(cid)
    if clanInfo==None or clanInfo[1]==2:
        return json.dumps(dict(code=1, msg="This clan is closed"))
    elif clanInfo[4]==50:
        return json.dumps(dict(code=2, msg="Clan is full"))
    userInfo = getUserInfos(uid)
    if userInfo==None:
        return json.dumps(dict(code=3, msg="User not exsited"))
    elif userInfo[2]<clanInfo[2]:
        return json.dumps(dict(code=4, msg="Score is limited"))
    if userInfo[5]==0:
        if clanInfo[1]==1:
            #add msg to clan
            return json.dumps(dict(code=0, type=1, cid=cid))
        else:
            addClanMember(cid, uid)
            #add msg to clan
            return json.dumps(dict(code=0, type=0, cid=cid))
    else:
        return json.dumps(dict(code=2, msg="User was already in a clan"))

@app.route("/login", methods=['POST', 'GET'])
def login():
    print 'login', request.form
    if 'username' in request.form:
        username = request.form['username']
        uid = getUidByName(username)
        ret = dict(code=0, uid=uid)
        if uid==0:
            print "new user"
            nickname = request.form['nickname']
            uid = initUser(username, nickname)
            
            achieveModule.initAchieves(uid)
            ret['uid'] = uid
        else:
            days = dailyModule.dailyLogin(uid)
            if days>0:
                ret['days']=days

        if False:

            con = MySQLdb.connect(host="192.168.3.105", user='root', passwd="badperson", db="nozomi", charset='utf8')
            sql = 'select * from nozomi_params'
            con.query(sql)
            res = con.store_result().fetch_row(0, 1)
            params = dict()
            for r in res:
                params[r['key']] = int(r['value'])
            sql = 'select * from nozomi_zombie_attack'
            con.query(sql)
            res = con.store_result().fetch_row(0, 1)
            waves = []
            for i in range(9):
                waves.append([])
                for j in range(1):
                    waves[i].append([])
                    for k in range(8):
                        waves[i][j].append(0)
            for r in res:
                item = waves[int(r['nozomi_level'])-1][int(r['attack_wave'])-1]
                for i in range(8):
                    item[i] = int(r['zombie%d_num' % (i+11)])
            params['attackWaves'] = waves
            ret['params'] = params
            con.close()

        return json.dumps(ret)
    else:
        #time.sleep(209) 
        return "{'code':401}"
        #测试timeout
        #pass

@app.route("/getData", methods=['GET'])
def getData():
    print 'getData', request.args
    uid = int(request.args.get("uid"))
    data = None
    if "login" in request.args:
        state = getUserState(uid)
        if 'attackTime' in state:
            return json.dumps(state)
        data = getUserAllInfos(uid)
        data['serverTime'] = int(time.mktime(time.localtime()))
        if data['lastSynTime']==0:
            data['lastSynTime'] = data['serverTime']
        data['achieves'] = achieveModule.getAchieves(uid)
    else:
        data = getUserInfos(uid)
    data['builds'] = getUserBuilds(uid)
    data['researches'] = getUserResearch(uid)
    return json.dumps(data)

@app.route("/reverge", methods=['GET'])
def revergeGetData():
    uid = int(request.args.get("uid"))
    eid = int(request.args.get("eid"))
    state = getUserState(eid)
    if 'attackTime' in state:
        return json.dumps(dict(code=1))
    elif 'onlineTime' in state:
        return json.dumps(dict(code=2))
    elif 'shieldTime' in state:
        return json.dumps(dict(code=3))
    else:
        data = getUserInfos(eid)
        data['builds'] = getUserBuilds(eid)
        data['code'] = 0
        return json.dumps(data)

@app.route("/getReplay", methods=['GET'])
def getReplay():
    vid = int(request.args.get("vid"))
    return queryOne("SELECT replay FROM nozomi_replay WHERE id=%s", (vid))[0]

@app.route("/synData", methods=['POST'])
def synData():
    print 'synData', request.form
    uid = int(request.form.get("uid", 0))
    if uid==0:
        return json.dumps({'code':401})
    if 'delete' in request.form:
        delete = json.loads(request.form['delete'])
        deleteUserBuilds(uid, delete)
    if 'update' in request.form:
        update = json.loads(request.form['update'])
        updateUserBuilds(uid, update)
    if 'achieves' in request.form:
        achieves = json.loads(request.form['achieves'])
        achieveModule.updateAchieves(uid, achieves)
    if 'research' in request.form:
        researches = json.loads(request.form['research'])
        updateUserResearch(uid, researches)
    userInfoUpdate = dict(lastSynTime=int(time.mktime(time.localtime())))
    if 'userInfo' in request.form:
        userInfo = json.loads(request.form['userInfo'])
        userInfoUpdate.update(userInfo)
        if 'shieldTime' in userInfo:
            setUserShield(uid, userInfo['shieldTime'])
    updateUserInfoById(userInfoUpdate, uid)
    updateUserState(uid, int(request.form.get("eid", 0)))
    if 'stat' in request.form:
        statlogger.info("%d\t%s" % (uid, request.form['stat']))
    if 'crystal' in request.form:
        ls = json.loads(request.form['crystal'])
        for l in ls:
            crystallogger.info("%d\t%s" % (uid, json.dumps(l)))
    return json.dumps({'code':0})

@app.route("/synBattleData", methods=['POST'])
def synBattleData():
    print 'synBattleData', request.form
    uid = int(request.form.get("uid", 0))
    eid = int(request.form.get("eid", 0))
    if uid==0 or eid==0:
        return json.dumps({'code':401})
    incScore = int(request.form.get("score", 0))

    if eid>1:
        if 'delete' in request.form:
            delete = json.loads(request.form['delete'])
            deleteUserBuilds(eid, delete)
        if 'update' in request.form:
            #print("test_update", request.form['update'])
            up = json.loads(request.form['update'])
            updateUserBuilds(eid, up)
        if 'hits' in request.form:
            hits = json.loads(request.form['hits'])
            updateUserBuildHitpoints(eid, hits)
        baseScore = getUserInfos(eid)['score']
        userInfoUpdate=dict(score=baseScore+incScore)
        if 'shieldTime' in request.form:
            t = int(request.form['shieldTime'])
            userInfoUpdate['shieldTime'] = t
            setUserShield(eid, t)
        updateUserInfoById(userInfoUpdate, eid)
    updateUserState(uid, eid)
    reverged = 0
    if 'isReverge' in request.form:
        reverged = 1
        print("Clear Reverge")
        update("UPDATE nozomi_battle_history SET reverged=1 WHERE uid=%s AND eid=%s", (uid, eid))
    if eid>1 and 'history' in request.form:
        videoId = 0
        if 'replay' in request.form:
            videoId = insertAndGetId("INSERT INTO nozomi_replay (replay) VALUES(%s)", (request.form['replay']))
        update("INSERT INTO nozomi_battle_history (uid, eid, videoId, `time`, `info`, reverged) VALUES(%s,%s,%s,%s,%s,%s)", (eid, uid, videoId, int(time.mktime(time.localtime())), request.form['history'], reverged))
    return json.dumps({'code':0})

@app.route("/findEnemy", methods=['GET'])
def findEnemy():
    selfUid = int(request.args.get('uid', 0))
    print("selfUid", selfUid)
    isGuide = request.args.get('isGuide')
    uid = 1
    if isGuide==None:
        uid = findAMatch(selfUid, int(request.args.get('baseScore', 0)), 1000)
    print("Find Enemy:%d" % uid)

    if uid != 0:
        data = getUserInfos(uid)
        data['builds'] = getUserBuilds(uid)
        data['userId'] = uid
        updateUserState(selfUid, int(request.args.get("eid", 0)))
    else: #cant find a enemy
        data = {'code':1}
    return json.dumps(data)

@app.route("/sendFeedback", methods=['POST'])
def sendFeedback():
    uid = int(request.form.get('uid', 0))
    if uid!=0:
        text=request.form.get('text')
        if text!=None:
            update("INSERT INTO nozomi_feedback (uid, text) VALUES (%s,%s)", (uid, text))
            return json.dumps(dict(code=0))
    return json.dumps(dict(code=401))
    
app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = config.HOSTPORT)
