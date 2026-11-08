"""把 _content/<slug>.json 编译成点化知识库（Markdown + manifest.json）。

用法：python3 build_content.py <slug>
"""
import json, os, re, sys, glob

ROOT = '/home/user/Doubao/chats/38452506321646594/点化学习系统'
CONTENT = os.path.join(ROOT, '_content')

def clean_label(s):
    s = s.replace('|', '／').replace('(', '（').replace(')', '）').replace('[', '【').replace(']', '】').replace('"', '＂')
    return s.strip()

def diagram(ch):
    secs = ch.get('secs', [])
    if ch.get('dia'):
        return ch['dia'].strip()
    names = [clean_label(s['h']) for s in secs[:4]]
    if not names:
        return None
    lines = ['flowchart LR']
    for i, n in enumerate(names):
        lines.append(f'  n{i+1}["{n}"]')
        if i:
            lines.append(f'  n{i} --> n{i+1}')
    return '\n'.join(lines)

def chapter_md(bk, ch, n):
    L = []
    L.append(f"# 第 {n} 章：{clean_t(ch['t'])}\n")
    L.append(f"- **难度**：{'★'*ch.get('d',1)}{'☆'*(3-ch.get('d',1))} ｜ **预估学时**：{ch.get('h',1)} 小时 ｜ **前置**：{ch.get('prereq','无')}\n")
    L.append('## 学习目标\n')
    for o in ch.get('obj', []):
        L.append(f'- {o}')
    L.append('\n## 一句话核心\n')
    L.append(ch['core'] + '\n')
    L.append('## 零基础讲解\n')
    for i, s in enumerate(ch.get('secs', []), 1):
        lvl = s.get('d', 1)
        tag = {1: '基础', 2: '进阶', 3: '高难'}.get(lvl, '基础')
        L.append(f"### 概念 {i}：{s['h']}（难度：{tag}）\n")
        L.append(s['p'].strip() + '\n')
    dg = diagram(ch)
    if dg:
        L.append('## 图示\n')
        L.append('```mermaid\n' + dg + '\n```\n')
        L.append(ch.get('diaNote') or '看图说明：方框是本章的概念顺序，箭头表示后一个概念必须建立在前一个之上。读图时先确认每个方框你都说得出一句白话定义，再往下看。\n')
    if ch.get('ana') or ch.get('ex'):
        L.append('## 类比与实例\n')
        if ch.get('ana'):
            L.append('- **类比**：' + ch['ana'].strip())
        if ch.get('ex'):
            L.append('- **实例**：' + ch['ex'].strip())
        L.append('')
    L.append('## 常见误解\n')
    for m in ch.get('mis', []):
        L.append(f'- {m}')
    L.append('\n## 自测题（答案）\n')
    for i, q in enumerate(ch.get('quiz', []), 1):
        L.append(f"{i}. {q['q']}")
        for j, o in enumerate(q.get('o', [])):
            L.append(f"   - {'ABCD'[j]}. {o}")
        ans = q.get('a', 0)
        if isinstance(ans, list):
            atxt = '、'.join('ABCD'[k] for k in ans)
        else:
            atxt = 'ABCD'[ans] if q.get('o') else str(ans)
        L.append(f"   - **答案**：{atxt}；**解析**：{q.get('e','')}")
    L.append('\n## 复习锚点\n')
    for a in ch.get('anchor', []):
        L.append(f'- {a}')
    return '\n'.join(L) + '\n'

def skill_md(bk):
    L = ['---', f"name: {bk['title']}（点化学习总纲）", '---', '', f"# {bk['title']} 点化学习系统", '']
    L.append('## 这本书在讲什么\n')
    L.append(bk['summary'].strip() + '\n')
    L.append('## 全书心智模型\n')
    L.append('```mermaid')
    L.append(bk.get('mindmap') or 'flowchart TD\n  A["主线"] --> B["章节"]')
    L.append('```\n')
    L.append('## 学习路径（推荐顺序）\n')
    L.append('| 步骤 | 章节 | 主题 | 前置 | 检查点 |')
    L.append('|---|---|---|---|---|')
    for i, ch in enumerate(bk['chapters'], 1):
        L.append(f"| {i:02d} | {ch['id']} | {ch['t']} | {ch.get('prereq','无')} | 完成本章自测 ≥2 题 |")
    L.append('\n## 章节索引\n')
    for i, ch in enumerate(bk['chapters'], 1):
        f = chapter_file(bk, ch, i)
        L.append(f"- 第 {i} 章 {ch['t']}（难度 {'★'*ch.get('d',1)}）→ {f}")
    L.append('\n## 前置知识（零基础缺口补讲）\n')
    L.append('| 缺口 | 对应补讲位置 | 学完标志 |')
    L.append('|---|---|---|')
    for g in bk.get('prereqTable', []):
        L.append(f"| {g[0]} | {g[1]} | {g[2]} |")
    L.append('\n## 术语表 / 模式库 / 速查表 入口\n')
    L.append('- 术语：[glossary.md](glossary.md)')
    L.append('- 模式与框架：[patterns.md](patterns.md)')
    L.append('- 速查：[cheatsheet.md](cheatsheet.md)')
    L.append('- 测验：[quiz.md](quiz.md)')
    L.append('- 抽认卡：[flashcards.md](flashcards.md)')
    L.append(f"\n> 单书伴侣：`{bk['slug']}学习伴侣.html`（双击即可离线学习）")
    return '\n'.join(L) + '\n'

def chapter_file(bk, ch, n):
    slug = re.sub(r'^第\s*\d+\s*章[：: ]*', '', ch['t'])
    slug = re.sub(r'[^\w\u4e00-\u9fa5-]+', '-', slug).strip('-')[:20]
    return f"chapters/{ch['id']}-{slug}.md"

def concept_pages(bk):
    out = {}
    for c in bk.get('concepts', []):
        L = [f"# {c['t']}\n", f"- **难度**：{c.get('dl','进阶')} ｜ **涉及章节**：{'、'.join('第 '+x[2:]+' 章' for x in c['ch'])}\n",
             '## 一句话定义\n', c['def'].strip() + '\n', '## 为什么重要\n', c['why'].strip() + '\n',
             '## 图示\n', '```mermaid', c.get('dia') or 'flowchart LR\n  n1["前置"] --> n2["本概念"] --> n3["后续用途"]', '```\n',
             '## 详解\n', c['body'].strip() + '\n', '## 常见误解\n', f"- {c.get('mis','别以为它只是个术语——它是后面几章论证的地基。')}\n",
             '## 在书中出现的脉络\n', '| 章节 | 语境 | 关键结论 |', '|---|---|---|']
        for row in c.get('trace', []):
            L.append(f"| {row[0]} | {row[1]} | {row[2]} |")
        L.append('\n## 相关概念\n')
        L.append('- ' + '、'.join(c.get('rel', ['—'])))
        out[f"concepts/{c['id']}-{re.sub(r'[^\w\u4e00-\u9fa5-]+','-',c['t'])[:16]}.md"] = '\n'.join(L) + '\n'
    return out

def glossary_md(bk):
    L = ['# 术语表', '', '| 术语 | 白话定义 | 首次出现 | 章节 |', '|---|---|---|---|']
    for t in bk.get('glossary', []):
        cid = t[2]
        idx = int(cid[2:])
        L.append(f"| **{t[0]}** | {t[1]} | {cid} | 第 {idx} 章 |")
    return '\n'.join(L) + '\n'

def patterns_md(bk):
    L = [f"# {bk['title']} 模式与框架库", '']
    for p in bk.get('patterns', []):
        L.append(f"## {p['kind']}：{p['t']}\n")
        L.append(p['body'].strip() + '\n')
    return '\n'.join(L)

def cheat_md(bk):
    L = ['# 速查表', '', '| 场景 | 内容 |', '|---|---|']
    for row in bk.get('cheat', []):
        L.append(f"| {row[0]} | {row[1]} |")
    return '\n'.join(L) + '\n'

def quiz_md(bk):
    L = [f"# {bk['title']} 测验", '']
    for i, ch in enumerate(bk['chapters'], 1):
        L.append(f"## 第 {i} 章测验：{clean_t(ch['t'])}\n")
        for j, q in enumerate(ch.get('quiz', []), 1):
            L.append(f"### Q{j}. {q['q']}\n")
            if q.get('o'):
                for k, o in enumerate(q['o']):
                    L.append(f"- {'ABCD'[k]}. {o}")
            ans = q.get('a', 0)
            atxt = '、'.join('ABCD'[k] for k in ans) if isinstance(ans, list) else ('ABCD'[ans] if q.get('o') else ans)
            L.append(f"\n**答案**：{atxt}\n\n**解析**：{q.get('e','')}\n")
    L.append('## 综合测验（多章联考）\n')
    for j, q in enumerate(bk.get('finalQuiz', []), 1):
        L.append(f"### Q{j}. {q['q']}\n")
        for k, o in enumerate(q.get('o', [])):
            L.append(f"- {'ABCD'[k]}. {o}")
        ans = q.get('a', 0)
        atxt = '、'.join('ABCD'[k] for k in ans) if isinstance(ans, list) else 'ABCD'[ans]
        L.append(f"\n**答案**：{atxt}\n\n**解析**：{q.get('e','')}\n")
    L.append('## 最终检验\n')
    L.append(bk.get('finalTask', '').strip())
    return '\n'.join(L) + '\n'

def flashcards_md(bk):
    L = [f"# {bk['title']} 抽认卡", '']
    for i, ch in enumerate(bk['chapters'], 1):
        L.append(f"## 第 {i} 章\n")
        cards = []
        cards.append((f"第 {i} 章一句话核心是什么？", ch['core']))
        for s in ch.get('secs', [])[:3]:
            cards.append((f"{s['h']}——用一句话说清它是什么？", re.split(r'[。；]', s['p'])[0] + '。'))
        for m in ch.get('mis', [])[:1]:
            cards.append((f"第 {i} 章最容易搞错的地方？", m))
        for k, (f_, b_) in enumerate(cards, 1):
            L.append(f"### 卡片：{f_}")
            L.append(f"- **背面**：{b_}")
            L.append(f"- **标签**：{ch['id']}, 第{i}章")
            L.append(f"- **章节**：{ch['id']}\n")
    return '\n'.join(L)

def clean_t(t):
    return re.sub(r'^第\s*\d+\s*章[：: ]*', '', t).strip()

def manifest(bk):
    chs = []
    for i, ch in enumerate(bk['chapters'], 1):
        chs.append({'id': ch['id'], 'title': f"第 {i} 章 {clean_t(ch['t'])}", 'file': chapter_file(bk, ch, i), 'difficulty': ch.get('d', 1)})
    qs = []
    for ch in bk['chapters']:
        for j, q in enumerate(ch.get('quiz', []), 1):
            item = {'id': f"{ch['id']}-q{j}", 'chapterId': ch['id'], 'type': 'single',
                    'question': q['q'], 'options': q.get('o', []), 'answer': q.get('a', 0), 'explain': q.get('e', '')}
            qs.append(item)
    for j, q in enumerate(bk.get('finalQuiz', []), 1):
        qs.append({'id': f"zx-q{j}", 'chapterId': '__all__', 'type': 'single', 'question': q['q'],
                   'options': q.get('o', []), 'answer': q.get('a', 0), 'explain': q.get('e', '')})
    cards = []
    k = 0
    for i, ch in enumerate(bk['chapters'], 1):
        k += 1
        cards.append({'id': f"f{k:03d}", 'chapterId': ch['id'], 'front': f"第 {i} 章一句话核心是什么？", 'back': ch['core'], 'tags': [ch['id']]})
        for s in ch.get('secs', [])[:3]:
            k += 1
            cards.append({'id': f"f{k:03d}", 'chapterId': ch['id'], 'front': f"{s['h']}——一句话说清它是什么？",
                          'back': re.split(r'[。；]', s['p'])[0] + '。', 'tags': [ch['id']]})
    m = {
        'slug': bk['slug'], 'title': bk['title'], 'subtitle': bk.get('subtitle', ''),
        'book': {'title': bk['title'], 'author': bk['author'], 'source': [bk.get('source', '第一推动丛书·综合系列（2022年版）')]},
        'audience': '零基础', 'goal': bk.get('goal', '系统掌握本书的核心论证与概念'),
        'learningPath': [{'step': f"{i:02d}", 'title': clean_t(ch['t']), 'chapterIds': [ch['id']],
                          'checkpoint': f"完成第 {i} 章自测题，答对 2 题以上"} for i, ch in enumerate(bk['chapters'], 1)],
        'chapters': chs,
        'concepts': [{'id': c['id'], 'title': c['t'], 'file': [f for f in concept_pages(bk) if f.startswith('concepts/'+c['id'])][0],
                      'chapterIds': c['ch']} for c in bk.get('concepts', [])],
        'glossary': [{'term': t[0], 'def': t[1], 'chapterId': t[2]} for t in bk.get('glossary', [])],
        'patterns': {'file': 'patterns.md'}, 'cheatsheet': {'file': 'cheatsheet.md'},
        'quizzes': qs, 'flashcards': cards,
        'companion': f"{bk['slug']}学习伴侣.html",
    }
    return m

def compile_book(slug):
    bk = json.load(open(os.path.join(CONTENT, slug + '.json'), encoding='utf-8'))
    d = os.path.join(ROOT, f"{bk['num']}-{bk['title']}")
    os.makedirs(os.path.join(d, 'chapters'), exist_ok=True)
    os.makedirs(os.path.join(d, 'concepts'), exist_ok=True)
    for i, ch in enumerate(bk['chapters'], 1):
        open(os.path.join(d, chapter_file(bk, ch, i)), 'w', encoding='utf-8').write(chapter_md(bk, ch, i))
    for path, txt in concept_pages(bk).items():
        open(os.path.join(d, path), 'w', encoding='utf-8').write(txt)
    open(os.path.join(d, 'SKILL.md'), 'w', encoding='utf-8').write(skill_md(bk))
    open(os.path.join(d, 'glossary.md'), 'w', encoding='utf-8').write(glossary_md(bk))
    open(os.path.join(d, 'patterns.md'), 'w', encoding='utf-8').write(patterns_md(bk))
    open(os.path.join(d, 'cheatsheet.md'), 'w', encoding='utf-8').write(cheat_md(bk))
    open(os.path.join(d, 'quiz.md'), 'w', encoding='utf-8').write(quiz_md(bk))
    open(os.path.join(d, 'flashcards.md'), 'w', encoding='utf-8').write(flashcards_md(bk))
    json.dump(manifest(bk), open(os.path.join(d, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(slug, 'ok', len(bk['chapters']), '章')

if __name__ == '__main__':
    for s in sys.argv[1:]:
        compile_book(s)
