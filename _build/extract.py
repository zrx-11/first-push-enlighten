import os, pymupdf, json, re, sys

SRC='/home/user/.doubao/agent_mode/workspace/.sessions/38452506321646594/attachments'
PDF=os.path.join(SRC,[x for x in os.listdir(SRC) if x.endswith('z-l')][0])
ROOT='/home/user/Doubao/chats/38452506321646594/点化学习系统'

BOOKS=[
 ('01','复杂','complex',4,325),
 ('02','复杂的引擎','engines-of-complexity',326,600),
 ('03','皇帝新脑','emperors-new-mind',601,1015),
 ('04','逻辑的引擎','engines-of-logic',1016,1191),
 ('05','数学的意义','meaning-of-math',1192,1311),
 ('06','未来50年','next-fifty-years',1312,1447),
 ('07','真理与美','truth-and-beauty',1448,1599),
 ('08','下一步是什么','whats-next',1600,1709),
 ('09','物理之外的世界','world-beyond-physics',1710,1818),
 ('10','伽利略的手指','galileos-finger',1819,2169),
 ('11','四维旅行','four-dimensional-travel',2170,2353),
]
FRONT=('版权信息','总序','再版序','前言','序','序言','引言','题献','敬启读者','译者序','感谢','致谢','跋','各篇文章作者简介','插曲','尾声','综述','后记','译后记','注释','名词解释','参考文献','参考书目','译名表','附录','进一步','邓恩')

doc=pymupdf.open(PDF)
toc=doc.get_toc()

def norm(t):
    return re.sub(r'\s+','',t)

def get_units(start,end):
    # 收集 level>=2 条目
    ents=[(l,t,p) for l,t,p in toc if start<=p<=end and l>=2]
    # 有 level3 章则取 level3；否则取 level2
    lv3=[e for e in ents if e[0]==3 and re.match(r'^第\s*\d+\s*章',e[1])]
    if len(lv3)>=4:
        units=[(t,p,3) for l,t,p in ents if l==3]
        # 把 level4 视为小节，不单独成章
    else:
        units=[(t,p,2) for l,t,p in ents if l==2]
    # 过滤前后附件
    out=[u for u in units if not norm(u[0]).startswith(FRONT)]
    if len(out)<=3:
        out=[(t,pg,3) for l,t,pg in ents if l==3]
    return out

def page_text(p0,p1):
    parts=[]
    for i in range(p0,min(p1,doc.page_count)):
        parts.append(doc[i].get_text())
    return '\n'.join(parts)

books=[]
for num,title,slug,start,end in BOOKS:
    units=get_units(start,end)
    # 计算各单元页尾
    pages=[u[1] for u in units]+[end+1]
    d=os.path.join(ROOT,f'{num}-{title}','_work','raw')
    os.makedirs(d,exist_ok=True)
    BACK=('附录','参考文献','参考书目','译后记','注释','名词解释','译名表','索引','致谢','跋','后记')
    last=pages[len(units)]
    for l,t,pg in toc:
        if last>=pg>pages[len(units)-1] and norm(t).startswith(BACK):
            last=pg-1; break
    pages[len(units)]=last
    recs=[]
    for i,u in enumerate(units):
        ch=f'ch{i+1:02d}'
        txt=page_text(pages[i],pages[i+1])
        txt=re.sub(r'\n{2,}','\n',txt).strip()
        with open(os.path.join(d,ch+'.txt'),'w',encoding='utf-8') as fh:
            fh.write(f'# {u[0]}\n\n'+txt)
        recs.append({'id':ch,'title':u[0],'page':pages[i],'end':pages[i+1]-1,'chars':len(txt),
                     'head':re.sub(r'\s+',' ',txt[:200]),'mid':re.sub(r'\s+',' ',txt[len(txt)//2:len(txt)//2+150])})
    books.append({'num':num,'title':title,'slug':slug,'start':start,'end':end,'chapters':recs})
    print(f"{num} {title}: {len(recs)} 章, 字符 {sum(r['chars'] for r in recs)}")

json.dump(books,open(os.path.join(ROOT,'_build','structure.json'),'w'),ensure_ascii=False,indent=1)
