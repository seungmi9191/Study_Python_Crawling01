
import requests
from datetime import datetime, timedelta
import json

BASE_URL_FB_API = "https://graph.facebook.com/v3.0"
ACCESS_TOKEN = "EAACEdEose0cBAOYDjaVUNWA8628whZAXufYON3PQ4AdZC6x9XdsmKsXScS3WYORS9pWhsNZBr4IAwraSDhNxFDmtEXwWM0CRcQ5432vh1CPCzyaW6tvEGSRwpIXxhoorcZAWqh3RdWCNC3gYs4H7eBjOQpI4j694AfP5w5pXyCvYGO4ZApv4VZBPPo97GpQ1DZBswvu48Gd7mcCP6W1RRhYAhXeKuwdvccZD"
LIMIT_REQUEST = 10

pagename = "chosun"
from_date = "2018-05-01"
to_date = "2018-05-23"

#사이트의 url을 던져주면 json으로 데이터를 리턴해줌
def get_json_result(url) :

    try :
        #get방식으로 url을 요청해서 응답을 response에 담음
        response = requests.get(url)

        #만약 요청한 url 주소가 없을 때 오류나는 것을 방지
        if response.status_code == 200 :
            json_result = response.json() #성공이면 요청에서 json을 받아서 json_result에 담음
            return json_result

    except Exception as e : #통신상 오류나면 현재시간과 url 정보를 담아줌
        return '%s : Error for request[%s]' %(datetime.now(), url)

#매개변수 pagename은 변수명으로 id값은 숫자로 받아와야하기때문에 그 값을 넣어준다.
#url을 던져주면 id값을 리턴해준다.
def fb_name_to_id(pagename) :

    #기본주소
    base = BASE_URL_FB_API
    #id값
    node = "/%s" %pagename
    #파라미터
    param = "/?access_token=%s" %ACCESS_TOKEN
    #url 완성하기
    url = base + node + param

    json_reuslt = get_json_result(url)
    #print(json_reuslt)

    return json_reuslt['id']


#url을 던져줘서 특정기간 내의 포스트를 가져오자.
#페이지네임, 시작날짜, 끝날짜를 주면 json 형태로 데이터를 리턴해줌

def fb_post_list(pagename, from_date, to_date) :

    #page_id를 받아와야함
    page_id = fb_name_to_id(pagename)

    base = BASE_URL_FB_API
    node = '/%s/posts' % page_id
    fields = '/?fields=id,message,link,name,type,shares,' + \
             'created_time,comments.limit(0).summary(true),' + \
             'reactions.limit(0).summary(true)'
    duration = '&since=%s&until=%s' % (from_date, to_date)
    parameters = '&limit=%s&access_token=%s' % (LIMIT_REQUEST, ACCESS_TOKEN)

    url = base + node + fields + duration + parameters

    #받아온 데이터에 딸려온 next값을 계속 받아야함
    postList=[]
    isNext = True #무한대 돌리기
    while isNext :
        temPostList = get_json_result(url)
        for post in temPostList["data"] :
            # message_str = post["message"]
            # print(message_str)

            postVo = preprocess_post(post)
            postList.append(postVo)

        paging = temPostList.get("paging").get("next")
        if paging != None :
            url = paging
        else :
            isNext = False

    # save results to file - postList를 던져주면 json으로 바꿔줌 -> d:/저장경
    with open("/Users/WOOSEUNGMI/Desktop/2018/javaStudy/facebook/" + pagename + ".json", 'w', encoding='utf-8') as outfile:
        json_string = json.dumps(postList, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(json_string)

    return postList

    # jsonPosts = get_json_result(url)
    #return jsonPosts


#json데이터를 주면 내가 원하는 5개만 뽑아내는 함수
def preprocess_post(post) :

    #작성일 +9시간 해줘야함(표준시간으로)
    created_time = post["created_time"]
    created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+0000')
    created_time = created_time + timedelta(hours=+9)
    created_time = created_time.strftime('%Y-%m-%d %H:%M:%S')


    #공유 수
    if "shares" not in post :
        shares_count = 0
    else :
        shares_count = post["shares"]["count"] #있으면 가져온 실제 숫자를 넣음

    #리액션 수
    if "reactions" not in post :
        reactions_count = 0
    else :
        reactions_count = post["reactions"]["summary"]["total_count"]

    # 댓글 수
    if "comments" not in post:
        comments_count = 0
    else:
        comments_count = post["comments"]["summary"]["total_count"]

    # 메세지 수
    if "message" not in post:
        message_str = ""
    else:
        message_str = post["message"]

    postVo = {
                "created_time":created_time,
                "shares_count": shares_count,
                "reactions_count": reactions_count,
                "comments_count": comments_count,
                "message_str": message_str
             }

    return postVo

jsonData = fb_post_list(pagename, from_date, to_date)
print(jsonData)


# result = fb_name_to_id("chosun")
# print(result)