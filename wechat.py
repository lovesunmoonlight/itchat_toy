# -*- coding: utf-8 -*-
#微信接口
#2017.9.21 由于推送网站不稳定，必须要有json获取失败的异常处理

import requests
import itchat
import threading
from time import ctime,sleep
import datetime
import urllib.request
import urllib.parse
import json
import random

city_list=["沈阳","武汉","哈尔滨","深圳","上海","兰州","成都","天津"]

threads = [] #线程列表

flag=True #推送线程标志
flag1=False #机器人线程标志
flag3=False #自动回复线程标志

target="filehelper" #推送对象

#给指定昵称的人发送消息
def send_message(name_arg,mes):
	
	#给文件助手发
	if name_arg=="filehelper":	
		itchat.send_msg(msg=mes, toUserName=name_arg) 
		return 
	else:	
		#给群发
		group=itchat.search_chatrooms(name=name_arg)
		if group!=None:
			name_arg=group[0]["UserName"]
			itchat.send_msg(msg=mes, toUserName=name_arg)
			return

		#给朋友发	
		#person=itchat.search_friends(name=name_arg)
		#if person!=None:
		#	name_arg=person[0]["UserName"]
		#	itchat.send_msg(msg=mes, toUserName=name_arg)



#登录时的回调函数
def lc():
    print("finish login")

#主线程
def auto_reply_thread():
    itchat.run()

#推送线程
def info_push_thread():
	global flag
	while flag==True:
		cur_time=datetime.datetime.now()
		if check_int_minute(cur_time)==8:
			send_sayings()
			sleep(1)
		elif check_int_minute(cur_time)==9:
			send_weather(city_list[random.randint(0,7)]) #随机一个城市
			sleep(1)
		elif check_int_minute(cur_time)==10:
			send_history_today()
			sleep(1)
		elif check_int_minute(cur_time)==11:
			send_news_hot()
			sleep(1)
		elif check_int_minute(cur_time)==12:
			send_movie_week()
			sleep(1)
		elif check_int_minute(cur_time)==23:
			send_say_goodnight()
			sleep(1)

#机器人线程
def robot_thread():
	global flag1
	if flag1==True:
		@itchat.msg_register(itchat.content.TEXT,isFriendChat=True, isGroupChat=False, isMpChat=False)
		def tuling_reply(msg):
			group=itchat.search_chatrooms(userName=msg['FromUserName'])
			if group!=None and group['NickName']==target:
				reply = get_response(msg['Text'])
				return reply
			return None

#点歌线程
def music_thread():
	@itchat.msg_register(itchat.content.SHARING,isFriendChat=False, isGroupChat=False, isMpChat=True)
	def return_from_mp(msg):
    	#公众号名
		org=itchat.search_mps(name=msg['FromUserName'])
		if org!=None and msg["User"]["NickName"]=="QQ音乐":
			print("ggggg")
			#reply = get_response(msg['Text'])
			#return reply
			print(msg['MsgType'])
			itchat.send(msg=msg,toUserName=target)
			print("ggggg")

def test_thread():
	@itchat.msg_register(itchat.content.SHARING,isFriendChat=True, isGroupChat=False, isMpChat=False)
	def receive():
		pass


#检查时间
def check_int_minute(cur_time):
	hour=cur_time.hour
	minute=cur_time.minute
	second=cur_time.second

	if minute==0 and second==0 and hour==8: #8点
		return 8
	elif minute==0 and second==0 and hour==9: #9点
		return 9
	elif minute==0 and second==0 and hour==10: #10点
		return 10
	elif minute==0 and second==0 and hour==11: #11点
		return 11
	elif minute==0 and second==0 and hour==12: #12点
		return 12
	elif minute==0 and second==0 and hour==22: #22点
		return 22
	elif minute==0 and second==0 and hour==23: #23点
		return 23
	return 0

#鸡汤推送
def send_sayings():
    showapi_appid="xxx"  #替换此值
    showapi_sign="xxx"   #替换此值
    url="http://route.showapi.com/1211-1"
    send_data = urllib.parse.urlencode([
        ('showapi_appid', showapi_appid)
        ,('showapi_sign', showapi_sign)
                    ,('count', "1") #默认获取一条
     
    ])
 
    req = urllib.request.Request(url)
    try:
       response = urllib.request.urlopen(req, data=send_data.encode('utf-8'), timeout = 10) # 10秒超时反馈
    except Exception as e:
        print(e)
        send_message(target,"很不幸，此条鸡汤推送失败了")
    result = response.read().decode('utf-8')
    result_json = json.loads(result)

    result_data=result_json["showapi_res_body"]["data"]

    ans=""
    for v in result_data:
        ans+="鸡汤时间："+"\n"
        ans+=v["english"]+"\n"
        ans+=v["chinese"]

    send_message(target,ans)

#天气推送
def send_weather(location):
    
    key="xxx" #心知天气key，替换此值
    language="zh-Hans"
    url="https://api.seniverse.com/v3/weather/now.json" #心知天气url入口

    #获取指定城市天气实况
    try:
    	result = requests.get(url, params={
        	'key': key,
        	'location': location,
        	'language': language,
        	'unit': "c" #摄氏度
    	}, timeout=1)
    except Exception as e:
    	print(e)
    	send_message(target,"很不幸，天气信息获取失败了") 

    result=result.json()

    #解码json数据
    dic = result
    city=dic["results"][0]["location"]["name"] #城市
    weather_info=dic["results"][0]["now"]["text"] #天气
    temperature=dic["results"][0]["now"]["temperature"] #温度
    feels_like=dic["results"][0]["now"]["feels_like"] #体感温度
    humidity=dic["results"][0]["now"]["humidity"] #相对湿度
    wind_direction=dic["results"][0]["now"]["wind_direction"] #风向
    visibility=dic["results"][0]["now"]["visibility"] #能见度

    time_str=dic["results"][0]["last_update"] #时间字符串
    day=time_str[:10] #日期
    time=time_str[11:19] #时间

    weather_dict={}
    weather_dict["city"]=city
    weather_dict["weather_info"]=weather_info
    weather_dict["temperature"]=temperature
    weather_dict["feels_like"]=feels_like
    weather_dict["humidity"]=humidity
    weather_dict["wind_direction"]=wind_direction
    weather_dict["visibility"]=visibility
    weather_dict["day"]=day
    weather_dict["time"]=time

    #将天气结果字典转为字符串
    ans=""

    ans+="随机城市天气实况:"+"\n"
    ans+="城市:"+weather_dict["city"]+"\n"
    ans+="天气:"+weather_dict["weather_info"]+"\n"
    ans+="温度:"+weather_dict["temperature"]+"摄氏度"+"\n"
    ans+="体感温度:"+weather_dict["feels_like"]+"\n"
    ans+="相对湿度:"+weather_dict["humidity"]+"%"+"\n"
    ans+="风向:"+weather_dict["wind_direction"]+"\n"
    ans+="能见度:"+weather_dict["visibility"]+"公里"+"\n"
    ans+="数据更新时间:"+weather_dict["day"]+" "+weather_dict["time"]

    send_message(target,ans)   

#结束语
def send_say_goodnight():
	ans="该休息了，大家晚安！"
	send_message(target,ans)

#图灵机器人接口
def get_response(msg):
    # 构造要发送给服务器的数据
    KEY  = 'xxx' #图灵机器人key，替换此值
    apiUrl = 'http://www.tuling123.com/openapi/api'
    data = {
        'key'    : KEY,
        'info'   : msg,
        'userid' : 'wechat-robot',
    }
    try:
        r = requests.post(apiUrl, data=data).json()
        # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
        return r.get('text')
    # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
    # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
    except:
        # 将会返回一个None
        return

#历史上的今天推送
def send_history_today():
	showapi_appid="xxx"  #替换此值
	showapi_sign="xxx"   #替换此值
	url="http://route.showapi.com/119-42"
	send_data = urllib.parse.urlencode([
    	('showapi_appid', showapi_appid)
    	,('showapi_sign', showapi_sign)
                    	,('date', "")
     
  	])
 
	req = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(req, data=send_data.encode('utf-8'), timeout = 10) # 10秒超时反馈
	except Exception as e:
		print(e)
		send_message(target,"很不幸，历史上的今天获取失败了") 
	result = response.read().decode('utf-8')
	result_json = json.loads(result)

	result_data=result_json["showapi_res_body"]["list"] #结果是一个字典组成的列表，每一项是一个事件

	date_now=datetime.datetime.today()
	
	m=str(date_now.month)
	d=str(date_now.day)

	ans="历史上的今天:"+"\n"

	#取前30条记录
	for v in result_data[:30]:
		year=v["year"]
		title=v["title"]
		ans+=year+"."+m+"."+d+" "+title+"\n"

	send_message(target,ans) 

#热点新闻推送
def send_news_hot():
	showapi_appid="xxx"  #替换此值
	showapi_sign="xxx"   #替换此值

	n=10 #默认10条新闻
	url="http://route.showapi.com/738-1"
	send_data = urllib.parse.urlencode([
    	('showapi_appid', showapi_appid)
    	,('showapi_sign', showapi_sign)
                    ,('n', n)
     
  	])
 
	req = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(req, data=send_data.encode('utf-8'), timeout = 10) # 10秒超时反馈
	except Exception as e:
		print(e)
		send_message(target,"很不幸，热点新闻获取失败了")

	result = response.read().decode('utf-8')
	result_json = json.loads(result)

	result_data=result_json["showapi_res_body"]["list"]

	ans="热点新闻："+"\n"

	for v in result_data[:10]:
		num=v["id"]
		title=v["title"]
		url=v["url"]
		ans+=num+"."+title+"\n"
		ans+="点击查看详细"+" "+url+"\n"
	
	send_message(target,ans) 

#电影周榜推送
def send_movie_week():
	showapi_appid="xxx"  #替换此值
	showapi_sign="xxx"   #替换此值
	url="http://route.showapi.com/578-1"

	send_data = urllib.parse.urlencode([
    	('showapi_appid', showapi_appid)
    	,('showapi_sign', showapi_sign)
     
  	])
 
	req = urllib.request.Request(url)
	try:
		response = urllib.request.urlopen(req, data=send_data.encode('utf-8'), timeout = 10) # 10秒超时反馈
	except Exception as e:
		print(e)
		send_message(target,"很不幸，热点电影获取失败了")
	result = response.read().decode('utf-8')
	result_json = json.loads(result)

	result_data=result_json["showapi_res_body"]["datalist"]

	result_data=bubble_sort(result_data)

	ans="热点电影："+"\n"

	for v in result_data:
		ans+="排名"+":"+v["Rank"]+" "+v["MovieName"]+"\n"
		ans+="本周票房"+":"+v["WeekAmount"]+"万"+"\n"
		ans+="总票房"+":"+v["SumWeekAmount"]+"万"+"\n"+"\n"

	send_message(target,ans)

#按照周票房排名冒泡排序
def bubble_sort(array):
	for i in range(len(array)):
		for j in range(i):
			tmp1=array[j]["Rank"]
			tmp2=array[j + 1]["Rank"]
			tmp1=int(tmp1)
			tmp2=int(tmp2)
			if tmp1>tmp2:
				array[j], array[j + 1] = array[j + 1], array[j] 
	return array

#自动回复线程
def auto_reply_thread():
	global flag3
	while flag3==True:
		@itchat.msg_register(itchat.content.TEXT,isFriendChat=True, isGroupChat=False, isMpChat=False)
		def auto_reply():
			respond=r'对不起，目前不方便回复信息，请留言或一会儿发送。--自动回复'
			return respond

#主循环
@itchat.msg_register(itchat.content.TEXT,isFriendChat=True, isGroupChat=False, isMpChat=False)
def tuling_reply(msg):

	#文件传输助手
	if msg['ToUserName']=="filehelper":
		if msg['Text']=="#打开信息推送":
			global flag
			flag=True
			t1 = threading.Thread(target=info_push_thread,name="push thread") #推送线程
			t1.start()
			itchat.send_msg(msg="打开信息推送成功", toUserName="filehelper")

		elif msg['Text']=="#关闭信息推送":
			global flag
			flag=False
			itchat.send_msg(msg="关闭信息推送成功", toUserName="filehelper")

		elif msg['Text']=="#打开机器人":
			global flag1
			flag1=True
			t2 = threading.Thread(target=robot_thread,name="robot thread") #机器人线程
			t2.start()
			itchat.send_msg(msg="打开机器人成功", toUserName="filehelper")
		
		elif msg['Text']=="#关闭机器人":
			global flag1
			flag1=False
			itchat.send_msg(msg="关闭机器人成功", toUserName="filehelper")

		elif msg['Text']=="#打开2":
			itchat.send_msg(msg="打开2成功", toUserName="filehelper")

		elif msg['Text']=="#关闭2":
			itchat.send_msg(msg="关闭2成功", toUserName="filehelper")
		elif msg['Text'][0]=="*":
			song_name=msg['Text'][1:]
			org=itchat.search_mps(name="QQ音乐")
			if org!=None and org[0]['NickName']=='QQ音乐':
				itchat.send_msg(msg=song_name,toUserName=org[0]['UserName'])

		elif msg['Text']=="#打开自动回复":
			global flag
			flag3=True
			t2 = threading.Thread(target=auto_reply_thread,name="auto_reply thread") #自动回复线程
			t2.start()
			itchat.send_msg(msg="打开自动回复成功", toUserName="filehelper")

		elif msg['Text']=="#关闭自动回复":
			global flag
			flag3=False
			itchat.send_msg(msg="关闭自动推送成功", toUserName="filehelper")

		else:
			print(msg['MsgType'])
			print(msg['Content'])
        
	return None

itchat.auto_login(loginCallback=lc,hotReload=True)

t1 = threading.Thread(target=auto_reply_thread,name="main thread") #主线程
threads.append(t1)

for t in threads:
    t.setDaemon(True)
    t.start()

for t in threads:
    t.join()
