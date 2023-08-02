import requests, bs4, re
import queue

#webbrowser: 测试用
import webbrowser

class Node:
    """记录每一个视频（节点）的信息"""
    def __init__(self, bv, len):
        res = requests.get('https://www.bilibili.com/video/BV' + bv)
        self.soup = bs4.BeautifulSoup(res.text, 'html.parser')
        self.bv = bv
        self.score = 999
        self.get_web_informations()
        self.len = len

    def __lt__(self, other):
        return self.len + self.score < other.len + other.score

    def get_web_informations(self):
        self.title = self.soup.select('h1[class="video-title"]')[0].get('title')
        self.firstTag = self.soup.select('.firstchannel-tag a')[0].getText()
        self.secondTag = self.soup.select('.secondchannel-tag a')[0].getText()
        self.tags = [t.getText() for t in self.soup.select('.ordinary-tag a')]
        self.newchTag = [t.getText() for t in self.soup.select('.newchannel-tag a')]

    def get_relate_video(self):
        self.urls = [t.get('href') for t in self.soup.select('.video-page-card-small .info > a')]
        bv_mode = re.compile(r'BV(\w\w\w\w\w\w\w\w\w\w)')
        self.next = [bv_mode.search(t).group(1) for t in self.urls]
        return self.next

    def evaluate(self, goal):
        """get the evaluation function for"""
        score = 0
        if self.firstTag != goal.firstTag:
            score += 1
        if self.secondTag != goal.secondTag:
            score += 2
        for tag in self.tags:
            if tag not in goal.tags:
                score += 1
        for tag in self.newchTag:
            if tag not in goal.newchTag:
                score += 1
        self.score = score


start_bv = input("请输入开始bv号（不含BV两字）:")
fin_bv = input("请输入终点bv号（不含BV两字）:")

res = requests.get('https://www.bilibili.com/video/BV' + start_bv)
res.raise_for_status()

goal = Node(fin_bv, 0)
start = Node(start_bv, 0)
start.score = 0

#记录相关信息
soup = bs4.BeautifulSoup(res.text, 'html.parser')

open_set = queue.PriorityQueue()
map = {}
parents = {}
titles = {}
succeed = False

open_set.put(start)
map[start.bv] = 'open'
parents[start_bv] = 'start'

titles[start_bv] = start.title
titles[fin_bv] = goal.title

while not open_set.empty():
    new = open_set.get()
    if new.bv == goal.bv:
        succeed = True
        print('succeeded.')
        break
    else:
        map[new.bv] = 'close'
        for bvs in new.get_relate_video():
            try:
                status = map[bvs]
            except KeyError:
                parents[bvs] = new.bv
                try:
                    ele = Node(bvs, new.len+1)
                except IndexError:
                    pass
                else:     
                    ele.evaluate(goal)
                    open_set.put(ele)
                    map[bvs] = 'open'
                    titles[bvs] = ele.title

chain = []
if succeed:
    chain.append(goal.bv)
    item = parents[goal.bv]
    while item != 'start':
        chain.append(item)
        item = parents[item]
    for bv in chain[::-1]:
        print("BV"+bv + "   " + titles[bv])
else:
    print("未找到合适的速通路径。")