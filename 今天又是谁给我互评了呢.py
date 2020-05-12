import requests
from lxml import etree


# 提取xpath
hre = '//td/a/@onclick'
# 提取分数的xpath
score_x = '//tbody/tr/td[4]/text()'
# 提取姓名的xpath
name_x = '//p[@clsdd]/span[1]/text()'

headers = {
    'Cookie': '',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'
}


# 登录
def login(user_name, pass_word):
    url = 'http://passport2.chaoxing.com/api/login?name=' + user_name + '&pwd=' + pass_word
    respond = requests.get(url=url, headers=headers)
    if respond.json()['result']:
        print(user_name, ':登录成功')
        # 设置cookie
        headers['Cookie'] = respond.headers["Set-Cookie"]
        return 1
    else:
        print(user_name, ':账号或密码错误')
        return 0


# 获取目标
def getTarget(url):
    # 获取work_answerid序列
    work_answerid = [url.split('workAnswerId=')[1][:8]]
    target = []
    # url 前缀
    url_left = url.split('workAnswerId=')[0] + 'workAnswerId='
    # url 后缀
    url_right = url.split('workAnswerId=')[1][8:]
    for i in work_answerid:
        # 拼凑出互评链接
        url = url_left + i + url_right
        respond = requests.get(url=url, headers=headers)
        html = etree.HTML(respond.text)
        answerids = html.xpath(hre)
        # 由于有查看与重批,设置布长为2过滤重复
        answerids = answerids[::2] if len(answerids) == 4 else answerids
        for j in answerids:
            j = j.split('workAnswerId=')[1][:8]
            # work_answerid保存
            if j not in work_answerid:
                work_answerid.append(j)
            # 筛选对象是否为你的评选人
            elif j in work_answerid[0]:
                target.append(i)
                if len(target) == 2:
                    return target
    return target


def getNameScore(target, scoreUrl, d_url):
    # 比较用
    workId = scoreUrl.split('workAnswerId=')[1][:8]
    for i in target:
        name = getName(i, scoreUrl)
        score = getScore(workId, i, d_url)
        print(name + '给你打的分是:' + score)


# 获取姓名
def getName(id, s_url):
    # s_url 前缀 分数
    s_url_left = s_url.split('workAnswerId=')[0] + 'workAnswerId='
    # url 后缀
    s_url_right = s_url.split('workAnswerId=')[1][8:]
    # 提取目标姓名
    s_url = s_url_left + id + s_url_right
    respond = requests.get(url=s_url, headers=headers)
    html = etree.HTML(respond.text)
    name = html.xpath(name_x)
    return name[0].replace('姓名：', '')


# 获取对象给你打的分
def getScore(target, id, d_url):
    # d_url 前缀 评分
    d_url_left = d_url.split('workAnswerId=')[0] + 'workAnswerId='
    # d_url 后缀
    d_url_right = d_url.split('workAnswerId=')[1][8:]
    # 提取他给你打的分
    d_url = d_url_left + id + d_url_right
    respond = requests.get(url=d_url, headers=headers)
    html = etree.HTML(respond.text)
    score = html.xpath(score_x)
    workIds = html.xpath(hre)[::2] if len(html.xpath(hre)) == 4 else html.xpath(hre)
    if len(score) < len(workIds):
        workIds = workIds[:1]
    # id是否是你的，是就说明他给你大的分
    for score_, id_ in zip(score, workIds):
        if id_.split('workAnswerId=')[1][:8] == target:
            return score_.replace('\t', '')


def main():
    try:
        user_name = input('请输入手机号：')
        pass_word = input('请输入密码：')
        s_url = input('请输入成绩页面的url：')
        d_url = input('请输入互评页面的url：')
        if login(user_name, pass_word) == 1:
            print('查询中！请耐心等待！')
            # 获取评分人
            target = getTarget(d_url)
            print('评分对象获取成功！正在查询他的信息！')
            getNameScore(target, s_url, d_url)
        input('wait')
    except BaseException as e:
        print(e)
        print('你的复制链接可能失效啦!')
        input('wait')


if __name__ == '__main__':
    main()
