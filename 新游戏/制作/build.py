"""使用带 Pillow 的 Python：python build.py；本机 bundled Python 已包含依赖。"""
from pathlib import Path
import html
import json
import re
from functools import lru_cache
from PIL import Image, ImageOps

PROJECT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
TITLE = '它们曾存在 · 神明的赠礼'
IFID = '36B3DFCC-35B5-4163-890F-E7E98B423E62'
css = (HERE / 'game.css').read_text(encoding='utf-8')
script = (HERE / 'game.js').read_text(encoding='utf-8')
passages = []


def add(name, body, tags=''):
    passages.append((name, body, tags))


def link(label, target):
    return '(transition-arrive: "instant")(link-goto: ' + json.dumps(label, ensure_ascii=False) + ', ' + json.dumps(target, ensure_ascii=False) + ')'


def actions(*items):
    return '<div class="actions">' + ''.join('<span>' + link(label, target) + '</span>' for label, target in items) + '</div>'


def choices(*items):
    return '<div class="actions story-choices">' + ''.join('<span class="decision-option">' + link('<span class="choice-title">' + label + '</span><span class="choice-detail">' + detail + '</span>', target) + '</span>' for label, detail, target in items) + '</div>'


def memory(text):
    return '<div class="memory"><span>你记得</span>' + text + '</div>'


@lru_cache(maxsize=None)
def image_size(path):
    with Image.open(PROJECT / path) as artwork:
        return artwork.size


def image(path, alt, advance=False):
    width, height = image_size(path)
    return '<figure class="artwork" style="--image-ratio:' + str(round(width / height, 6)) + '"' + (' data-advance="yes"' if advance else '') + '><img src="' + html.escape(path, quote=True) + '" alt="' + html.escape(alt, quote=True) + '" width="' + str(width) + '" height="' + str(height) + '" decoding="async"></figure>'


@lru_cache(maxsize=None)
def silhouette(path):
    source = PROJECT / path
    output = source.with_name(source.stem + '透明.png')
    if not output.exists() or output.stat().st_mtime < source.stat().st_mtime:
        with Image.open(source) as original:
            alpha = ImageOps.invert(original.convert('L')).point(lambda value: min(255, round(value * 1.8)))
            cutout = Image.new('RGBA', original.size, (55, 53, 54, 0))
            cutout.putalpha(alpha)
            cutout.save(output, optimize=True)
    return output.relative_to(PROJECT).as_posix()


def para(text, kind=''):
    return '<p' + (' class="' + kind + '"' if kind else '') + '>' + text + '</p>'


def styled(text, style='shadow'):
    return '(text-style: ' + json.dumps(style) + ')[' + text + ']'


def cycling(*versions):
    return '<span class="cycle-word word-slot" title="点击文字，换一个角度"><span class="word-measure" aria-hidden="true">' + max(versions, key=len) + '</span><span class="word-value">(cycling-link: ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in versions) + ')</span></span>'


def reveal_word(label, answer):
    return '<span class="reveal-word word-slot" title="点击这句话，看看藏着的意思"><span class="word-measure" aria-hidden="true">' + max((label, answer), key=len) + '</span><span class="word-value">(link: ' + json.dumps(label, ensure_ascii=False) + ')[(transition: "dissolve")+(transition-time: .55s)[' + answer + ']]</span></span>'


def changing_word(hook, *versions):
    values = ', '.join(json.dumps(value, ensure_ascii=False) for value in versions)
    return '<span class="changing-word word-slot"><span class="word-measure" aria-hidden="true">' + max(versions, key=len) + '</span><span class="word-value">|' + hook + '>[' + versions[0] + ']</span></span>(set: _wordStep to 1)(live: 2.4s)[(set: _wordStep to _wordStep + 1)(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .65s)[(print: (nth: _wordStep, ' + values + '))]](if: _wordStep >= ' + str(len(versions)) + ')[(stop:)]]'


def typed_voice(text):
    plain = text.replace('<br>', '\n')
    count = str(len(plain))
    return '(set: _inkText to ' + json.dumps(plain, ensure_ascii=False) + ')(set: _inkCount to 1)|spokenLine>[<span class="typewriter-line" title="点击对白，立即读完整句"><span class="typewriter-measure" aria-hidden="true">' + text + '</span><span class="typewriter-ink" aria-hidden="true">|typedVoice>[(print: (substring: _inkText, 1, _inkCount))]|typedCursor>[<span class="typewriter-caret">▏</span>](live: 45ms)[(set: _inkCount to (min: _inkCount + 1, ' + count + '))(replace: ?typedVoice)[(print: (substring: _inkText, 1, _inkCount))](if: _inkCount >= ' + count + ')[(replace: ?typedCursor)[](stop:)]]</span><span class="sr-only">' + text + '</span></span>](click: ?spokenLine)[(set: _inkCount to ' + count + ')(replace: ?typedVoice)[(print: _inkText)](replace: ?typedCursor)[]]'


def whisper(hook, label, lines, mode='listen'):
    """Native Harlowe changes stay inside a reserved two-line text slot."""
    text = '<div class="story-whisper" data-whisper="' + hook + '"><span class="whisper-label">' + label + '</span><span class="whisper-copy">|' + hook + '>[' + lines[0] + ']</span>'
    if mode == 'listen':
        text += '<span class="whisper-action">(set: _echo to 1)(link-rerun: "再听一次 ↻")[(set: _echo to _echo + 1)(if: _echo > ' + str(len(lines)) + ')[(set: _echo to 1)](replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .4s)[(print: (nth: _echo, ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in lines) + '))]]]</span>'
    elif mode == 'after':
        text += '(after: 1.6s)[(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .8s)[' + lines[-1] + ']]]'
    else:
        text += '(set: _echo to 1)(live: 1.2s)[(set: _echo to _echo + 1)(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .6s)[(print: (nth: _echo, ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in lines) + '))]](if: _echo >= ' + str(len(lines)) + ')[(stop:)]]'
    return text + '</div>'


def enrich_scene(name, body):
    replacements = {
        '猪_森林': ('不是雷霆', cycling('不是雷霆', '不是风声', '不是同伴')),
        '猪_巨兽': ('震耳欲聋的嘶吼', styled('震耳欲聋的嘶吼')),
        '猪_光芒': ('刺眼的黄色光芒', styled('刺眼的黄色光芒')),
        '猪_神明': ('野猪之神', styled('野猪之神', 'outline')),
        '猫_标签': ('健康、活泼', '|health>[健康、活泼]'),
        '猫_饭': ('有一点奇怪', cycling('有一点奇怪', '有一丝苦味', '不像食物了')),
        '猫_色彩': ('世界突然有了色彩', '(text-colour: "#985c7c")[' + styled('世界突然有了色彩') + ']'),
        '猫_新家': ('头越来越沉', styled('头越来越沉', 'blur')),
        '猫_祭司': ('没有痛苦的喵星天堂', styled('没有痛苦的喵星天堂', 'fade-in-out')),
        '鸭_泥沼': ('神圣光晕', styled('神圣光晕', 'outline')),
        '鸭_神迹': ('被挑选', cycling('被挑选', '被称重', '被带走')),
        '鸭_天平': ('脂肪的厚度', cycling('脂肪的厚度', '被出售的重量', '可供挑选的分量')),
        '鸭_祭司': ('造物主', styled('造物主', 'shadow')),
    }
    if name in replacements:
        old, new = replacements[name]
        body = body.replace(old, new, 1)
    clues = {
        '猪_巨兽': ('钢铁鳞甲', changing_word('ironSkin', '钢铁鳞甲', '没有温度的鳞甲', '不会呼吸的钢铁')),
        '猪_光芒': ('陌生的气味', reveal_word('陌生的气味', '铁锈与机油的气味')),
        '猪_足迹': ('浅浅蹄印', reveal_word('浅浅蹄印', '通向生路的蹄印')),
        '猪_机油': ('树木被折断后的汁液', reveal_word('树木被折断后的汁液', '森林受伤后流下的汁液')),
        '猪_神明': ('与你相似的轮廓', changing_word('godShape', '与你相似的轮廓', '你想象中的神明', '沉默无声的机械')),
        '猪_引路': ('还没倒下的树林', reveal_word('还没倒下的树林', '还有呼吸的树林')),
        '猪_存活': ('森林深处，依然能接纳你', reveal_word('森林深处，依然能接纳你', '那里没有神，只有活着的树')),
        '猪_灭绝': ('神明赐予的祭品', changing_word('falseGift', '神明赐予的祭品', '森林留下的伤口', '不再生长的树桩')),
        '猪_同行': ('跟在你身后的脚步', reveal_word('跟在你身后的脚步', '一起逃出生天的脚步')),
        '猫_牢笼': ('灰色的影子', changing_word('cageNames', '灰色的影子', '没有名字的影子', '等待被看见的生命')),
        '猫_同伴': ('一声很轻的呼噜', reveal_word('一声很轻的呼噜', '一句很轻的“等你”')),
        '猫_药味': ('几粒硬硬的东西', reveal_word('几粒硬硬的东西', '藏在食物里的药物')),
        '猫_推碗': ('发出一声轻响', reveal_word('发出一声轻响', '替你说了一声“不”')),
        '猫_求助': ('在笼门前蹲了下来', reveal_word('在笼门前蹲了下来', '终于认真地看向了你')),
        '猫_色彩': ('像糖果一样', changing_word('sweetBars', '像糖果一样', '像梦境一样', '也像一个谎言')),
        '猫_窗边': ('没有说真话', reveal_word('没有说真话', '把疾病藏了起来')),
        '猫_新闻前往': ('没有就此结束', reveal_word('没有就此结束', '成为揭开骗局的线索')),
        '猫_新闻放弃': ('多住一些日子', reveal_word('多住一些日子', '等到下一次日出')),
        '猫_救助': ('真正的家还没有到来', changing_word('realHome', '真正的家还没有到来', '有人愿意先等你康复', '这次的承诺不用着急')),
        '鸭_泥沼': ('泥泞是恩赐', reveal_word('泥泞是恩赐', '泥泞只是圈养')),
        '鸭_同伴': ('拥挤的空隙', reveal_word('拥挤的空隙', '能让同伴站稳的空隙')),
        '鸭_粮食': ('用力挤出来的全部', reveal_word('用力挤出来的全部', '踩过同伴换来的全部')),
        '鸭_独食': ('神明的手', changing_word('choosingHand', '神明的手', '挑选的手', '称量的手')),
        '鸭_分食': ('终于不再空着的嘴', reveal_word('终于不再空着的嘴', '不必再相互争抢的嘴')),
        '鸭_反问': ('轻轻碰了碰你的翅膀', reveal_word('轻轻碰了碰你的翅膀', '提醒你：我们还可以走')),
        '鸭_同行': ('没有人替你们加上光晕', changing_word('ownHalo', '没有人替你们加上光晕', '没有人再替你们做决定', '脚下这条路属于你们')),
    }
    if name in clues:
        old, new = clues[name]
        body = body.replace(old, new, 1)
    extras = {
        '猪_森林': ('forestEcho', '林中的回声', ['轰鸣钻过树根，泥土里再没有鸟鸣。', '你向前一步，落叶下面传来陌生的震动。', '身后是熟悉的林子。声音，却从林外来。'], 'listen'),
        '猪_机油': ('ironBreath', '空气里的答案', ['不是血，也不是雨。是灼热的铁和机油。', '你第一次听见，一种没有呼吸的吼声。', '树木的汁液里，还混着被翻开的泥土。'], 'listen'),
        '猪_喷气': ('godReply', '等一个回答', ['你吐出一口白雾，等它回应。', '白雾散开了。巨神的胸膛里，只有引擎。', '它没有回答。你却仍然仰着头。'], 'live'),
        '猫_牢笼': ('cageEcho', '笼子另一端', ['你听见，角落里有一个很轻的声音。', '那不是睡熟的呼噜。它也在等门打开。'], 'after'),
        '猫_光': ('homePromise', '家的样子', ['你在心里，把那个房间排练了一遍。', '先趴在沙发上，再把尾巴绕过自己的脚。', '最后，给角落里的同伴也留一个位置。'], 'listen'),
        '猫_告别': ('lastVoice', '越来越远的声音', ['你还想再听一遍，那个关于家的承诺。', '脚步远了。灯光也慢慢远了。', '睡吧。那些没有说出口的话，有人会记得。'], 'live'),
        '鸭_拥挤': ('crowdEcho', '队伍里的低语', ['每一只抬起的头，都朝向同一只手。', '后面的鸭子说，再往前一点就好了。', '可前面，已经没有可以站稳的泥地。'], 'listen'),
        '鸭_天平': ('scaleReply', '指针摇动的时候', ['你盯着天平，像在等待一个名字。', '指针动了。没有人问你，从哪里来。', '落在秤盘上的，从来不是名字。'], 'live'),
        '鸭_祭司': ('outsideScreen', '屏幕另一边', ['祭司停下了，目光越过鸭群。', '它在等你的回答。这一次，问题属于你。'], 'after'),
    }
    if name in extras:
        addition = whisper(*extras[name])
        index = body.find('<div class="actions')
        body = body[:index] + addition + body[index:] if index >= 0 else body + addition
    if name == '猫_标签':
        body += '(after: .9s)[(enchant: ?health, (text-style: "strike")+(text-colour: "#945468"))]'
    if name == '猫_窗边':
        body += '<p class="thought macro-line">(seq-link: "那个承诺，还在耳边。", "他说，会有一个温暖的家。", "可他没有说，健康也能被伪装。")</p>'
    # The first plain voice on every page is written with native Harlowe macros.
    # Dialogues containing interactive words retain those words and unfold by sentence.
    typed = False
    def write_voice(match):
        nonlocal typed
        if typed or re.search(r'\([a-z-]+\s*:|<span|\|[A-Za-z]+>', match[2]):
            return match[0]
        typed = True
        return match[1] + typed_voice(match[2]) + match[3]
    body = re.sub(r'(<p class="voice">)(.*?)(</p>)', write_voice, body)
    if not typed:
        def write_closing(match):
            return match[1] + typed_voice(match[2]) + match[3]
        body = re.sub(r'(<p class="closing">)(.*?)(</p>)', write_closing, body, count=1)
    return body


def scene(name, role, number, chapter, path, alt, body, next_to=None, next_label='继续 →', sound='', extra='', ending='', classes='', progress=0, advance=True):
    body = enrich_scene(name, body)
    role_label = {'pig': '野猪 / FOREST', 'cat': '猫 / HOME', 'duck': '鸭子 / ALTAR'}[role]
    inner = '<div class="chapter"><span class="number">' + number + '</span><span>' + chapter + '</span><span class="track"></span><small>' + role_label + '</small></div>'
    inner += image(path, alt, bool(next_to and advance))
    inner += '<div class="scene-panel"><div class="scene-copy">' + body + (actions((next_label, next_to)) if next_to else '') + '</div>' + extra + '</div>'
    inner += '<div class="chapter-meter" aria-hidden="true"><span style="width:' + str(progress) + '%"></span></div>'
    effects = {'猪_森林': 'forest', '猪_巨兽': 'machine', '猪_靠近': 'machine', '猪_光芒': 'light', '猪_神明': 'revelation', '猪_喷气': 'steam', '猫_色彩': 'colour', '猫_光': 'warmth', '猫_新家': 'warmth', '猫_天堂': 'warmth', '猫_告别': 'farewell', '鸭_泥沼': 'halo', '鸭_神迹': 'halo', '鸭_天平': 'scales', '鸭_祭司': 'altar'}
    attrs = ' data-sound="' + sound + '"' + (' data-ending="' + ending + '"' if ending else '') + (' data-fx="' + effects[name] + '"' if name in effects else '')
    reset = {'猪_森林': '(set: $pigTrail to false)(set: $pigOil to false)', '猫_牢笼': '(set: $catCompanion to false)(set: $catTag to false)(set: $catMedicine to false)', '鸭_泥沼': '(set: $duckHelp to false)(set: $duckShare to false)'}.get(name, '')
    add(name, reset + '<section data-scene="' + name + '" class="page scene-stage role-' + role + ' ' + classes + '"' + attrs + '>' + inner + '</section>')


def task(kind, action_label, status, next_label, target, goal=1, hint=''):
    return '<div class="interaction" data-task="' + kind + '" data-goal="' + str(goal) + '"><p class="instructions">' + hint + '</p><button type="button" class="' + ('hold-button' if kind == 'hold' else 'action-button') + '" data-task-action>' + action_label + '</button><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">' + status + '</p><div class="actions is-locked" data-task-next>' + link(next_label, target) + '</div></div>'


def ending_tail():
    return actions(('重走这条路 ↻', {'pig': '猪_森林', 'cat': '猫_牢笼', 'duck': '鸭_泥沼'}[ending_role]), ('换一双眼睛 ↗', '选择角色'), ('翻开旅程手记', '旅程手记'))


add('初始化', '(set: $pigTrail to false)(set: $pigOil to false)(set: $catCompanion to false)(set: $catTag to false)(set: $catMedicine to false)(set: $duckHelp to false)(set: $duckShare to false)', 'startup')
add('页眉', '<header class="mast"><span class="brand"><em>✧</em><span>THEY ONCE EXISTED</span><span class="series-label"> / 神明的赠礼</span></span><nav aria-label="游戏导航"><button type="button" class="audio-toggle" data-audio-toggle aria-pressed="true">声音：开</button>' + link('选角', '选择角色') + link('手记 <span class="journal-number" data-journal-total>0/9</span>', '旅程手记') + '</nav></header>', 'header')

roles = [
    ('pig', '01 / THE FOREST', '野猪', '它披着钢铁的鳞甲。<br>你以为，那是森林的神。', '素材/选角/野猪.jpg', '猪_森林'),
    ('cat', '02 / THE HOME', '猫', '有人答应给你一个家。<br>你记住了，那盏温暖的灯。', '素材/选角/猫.jpg', '猫_牢笼'),
    ('duck', '03 / THE ALTAR', '鸭子', '神明撒下水和粮。<br>你们争抢，被挑选的资格。', '素材/选角/鸭子.jpg', '鸭_泥沼'),
]
cards = ''
for key, label, animal, desc, path, target in roles:
    cards += '<article class="role-card"><span class="role-count" data-role-count="' + key + '">0/3</span><button type="button" class="animal-preview" data-animal="' + key + '" aria-label="试听' + animal + '叫声"><img src="' + path + '" alt="' + animal + '的剪影"><span class="sound-hint">点击动物 · 听见它的声音 ♫</span></button><div class="role-copy"><div class="role-no">' + label + '</div><h2>' + animal + '</h2><p>' + desc + '</p><div class="role-enter">' + link('以它的目光出发 <span>↗</span>', target) + '</div></div></article>'
add('选择角色', '<section data-scene="选择角色" class="page selection"><div class="eyebrow">PROLOGUE / 序章</div><div class="selection-head"><h1>借一双眼睛</h1><p>点击动物试听叫声，再选择以它的目光出发。</p></div><img class="selection-art" src="' + silhouette('素材/选角/它们.jpg') + '" alt="野猪、猫与鸭子的剪影"><div class="role-grid">' + cards + '</div><footer class="selection-foot"><span>三个故事 · 九个结局 · 你记住的细节，也会改变去向</span><span class="series">它们曾存在 / 神明的赠礼</span></footer></section>')

# 野猪：八幅插画，五次撞击，长按喷气，两个结局。
scene('猪_森林', 'pig', '01', '森林的边界', '新/1在森林.jpg', '从野猪的视角看向幽蓝色的树林',
      '<h1>森林的边界</h1>' + para('“那是……什么声音？不是雷霆，却让大地颤抖。”', 'voice') + para('你停下脚步，望向森林之外。', 'thought'), '猪_巨兽', '循着声音望去 →', 'pigOpen', progress=8)
scene('猪_巨兽', 'pig', '01', '森林的边界', '新/2看见伐木机.jpg', '灰黑色的伐木机出现在树林之外',
      para('从平原的尽头，一个奇异的“生物”出现了。它没有皮毛，却披着灰黑色的钢铁鳞甲。') + para('它没有血肉，却发出震耳欲聋的嘶吼。', 'voice') + choices(('迎着声音靠近', '你想看清它的面孔。', '猪_靠近'), ('沿林缘绕一圈', '泥地里，有一些熟悉的足迹。', '猪_足迹')), sound='pigOpen', progress=16)
scene('猪_足迹', 'pig', '01', '被遮住的来路', '新/1在森林.jpg', '森林深处留下了一条尚未被机器推平的小径',
      '(set: $pigTrail to true)' + para('泥地里有幼崽留下的浅浅蹄印。它们绕开空地，朝北边的小径延伸。') + para('小径尽头，还有潮湿的泥土和野果的气味。<br>你把这条路，记在了心里。', 'voice') + memory('北边有一条，还能回到森林的小径。'), '猪_靠近', '再去看看那头巨兽 →', 'pigOpen', progress=22)
scene('猪_靠近', 'pig', '02', '没有血肉的巨兽', '新/3伐木机靠近.jpg', '伐木机的轮盘和钢铁躯体逐渐逼近',
      para('它一路啃食着树木，留下光秃秃的泥地。') + para('“它好庞大……甚至比森林里最老的熊还要强壮。<br>挡路的树木，都被它轻易咬碎。”', 'voice'), '猪_光芒', '继续 →', 'pigOpen', progress=25)
scene('猪_光芒', 'pig', '02', '灼热的光芒', '新/4机器发光.jpg', '停在森林边缘的机器散发刺眼的黄色光芒',
      para('巨兽停在森林边缘。刺眼的黄色光芒直刺过来。<br>空气中没有血腥味，只有一种陌生的气味。') + para('“它看着我不动了。它是在向我宣战？”', 'voice') + choices(('亮出獠牙', '用森林里的规矩，回应它。', '猪_撞击'), ('先闻一闻风', '它身上，没有活物的气味。', '猪_机油')), sound='pigOpen', progress=34)
scene('猪_机油', 'pig', '02', '不像活物的呼吸', '新/3伐木机靠近.jpg', '机器轮盘之间的黑暗缝隙',
      '(set: $pigOil to true)' + para('你没有闻到皮毛、血液，或雨后动物的潮湿气息。<br>只有铁锈、机油，还有树木被折断后的汁液。') + para('“它的叫声里……没有呼吸。”', 'voice') + memory('巨兽没有呼吸。它吞掉树木，却从来不需要进食。'), '猪_撞击', '试探着，碰一碰它 →', 'pigOpen', progress=40)
scene('猪_撞击', 'pig', '03', '獠牙与钢铁', '新/5野猪靠近.jpg', '野猪举起獠牙迎向发光的机器',
      para('你低下头，亮出獠牙。<br>即使它比你庞大，你也不愿退后。', 'voice'), sound='pigInteract',
      extra=task('ram', '用獠牙撞击机械', '獠牙撞击 · 0 / 5', '抬起头，看向它 →', '猪_神明', 5, '点击五次，撞向挡在森林前的巨兽。'), progress=45)
scene('猪_神明', 'pig', '04', '钢铁铸就的神明', '新/6机器变野猪.jpg', '机械在野猪眼中化为长着巨型獠牙的野猪神明',
      para('“天哪……它不是怪物。<br>它是钢铁铸就的——野猪之神！”', 'voice') + para('第五次撞击之后，你看见了一个与你相似的轮廓。', 'thought'), '猪_喷气', '仰望巨神 →', 'pigWorship', progress=57)
scene('猪_喷气', 'pig', '04', '向神明献上呼吸', '新/7野猪喷气.jpg', '渺小的蓝色野猪仰望被白色雾气环绕的机械巨神',
      para('巨大的神明降临凡间。白色的烟雾，如同圣光般环绕。<br>你虔诚地仰起头，试着向它回应。', 'voice'), sound='pigWorship',
      extra=task('hold', '按住 · 向巨神喷气', '按住按钮，也可以按住空格或回车。', '等待它的回答 →', '猪_抉择', hint='长按约两秒，吐出白雾；松开后可继续。'), progress=70)
scene('猪_抉择', 'pig', '05', '命运的抉择', '新/野猪说话.jpg', '野猪站在沉默的钢铁巨神面前',
      '<h1>你会留下吗？</h1>' + para('神明似乎停在了这里。<br>是永远追随这位无所不能的庇护者，还是回到那片拥挤、潮湿，却熟悉的森林？', 'voice') + '(if: $pigOil)[' + memory('这尊神明的身上，没有活物的气息。') + ']' + choices(('离开 · 回到森林', '你仍能听见树影中的风。', '猪_存活'), ('留下 · 追随巨神', '你还在等它回答那口白雾。', '猪_灭绝')) + '(if: $pigTrail and $pigOil)[' + choices(('沿着小径，去找同伴', '你认得来路，也认出了巨神。', '猪_引路')) + ']', sound='pigWorship', progress=84)
scene('猪_引路', 'pig', '05', '把来路留给后来者', '新/1在森林.jpg', '森林的入口仍然敞开，深处有同伴的足迹',
      para('你没有独自离开。你沿着记住的蹄印，回到那片还没倒下的树林。') + para('远处，有同伴仍在向着轰鸣的方向张望。<br>你站在小径入口，把头转向它们。', 'voice'), sound='pigOpen', extra=task('signal', '向林中呼唤', '让它们听见你 · 0 / 3', '带着它们走向森林深处 →', '猪_同行', 3, '呼唤三次，把同伴带离正在逼近的轰鸣。'), progress=93)
ending_role = 'pig'
scene('猪_存活', 'pig', '06', '结局 A · 离开', '新/1在森林.jpg', '野猪转身回到深蓝色的森林',
      '<div class="ending-label">ENDING 01 / 离开</div><h1>森林仍然接纳你</h1>' + para('你最后看了一眼钢铁巨神，转身没入深蓝色的森林。') + para('你以为自己失去了神明庇佑，却不知道自己躲过了怎样的结局。') + para('伐木机继续轰鸣。虽然你失去了部分领地，但森林深处，依然能接纳你。') + para('你活了下来。', 'closing') + ending_tail(), sound='pigLive', ending='pig-live', classes='ending', progress=100)
scene('猪_灭绝', 'pig', '06', '结局 B · 留下', '新/2看见伐木机.jpg', '森林的颜色褪去，只留下继续工作的伐木机',
      '<div class="ending-label">ENDING 02 / 留下</div><h1>沉默的庇护者</h1>' + para('你依偎在巨兽身旁，把被砍伐的树桩，当作神明赐予的祭品。<br>你以为自己获得了最强大的庇护。') + para('几天后，伐木机完成了工作。茂密的森林变成荒原。<br>你倒下了，却始终等不到神明赐予的草地。') + para('你的生命，随着这片森林的覆灭走向终结。', 'closing') + ending_tail(), sound='pigFall', ending='pig-fall', classes='ending ending-pig-fall', progress=100)
scene('猪_同行', 'pig', '06', '隐藏结局 · 引路', '新/1在森林.jpg', '野猪与同伴一起走向未被推平的森林深处',
      '<div class="ending-label">HIDDEN ENDING / 引路</div><h1>把来路留给后来者</h1>' + para('你没有让机器停下。你只是记住了一条小径，认出了一种不属于生命的气味。') + para('但那一天，跟在你身后的脚步，不止一个。<br>幼崽踩过你的蹄印，走向林中尚未消失的水源。') + para('你们一起，活到了第二天。', 'closing') + ending_tail(), sound='pigLive', ending='pig-guide', classes='ending', progress=100)

# 猫：咀嚼—吞咽—色彩，短暂的家，两个选择各自进入新闻结尾。
scene('猫_牢笼', 'cat', '01', '冰凉的铁栏杆', '猫/1.jpg', '灰色的猫挤在冰冷的铁栏杆之后',
      '<h1>外面会暖和一些吗？</h1>' + para('这里的铁栏杆总是冰凉。我们像灰色的影子一样挤在一起，分不清彼此。') + para('“我常常在想，外面的世界，是不是会暖和一些？”', 'voice') + choices(('朝光的方向看去', '门外的脚步，越来越近。', '猫_光'), ('挨近角落的小猫', '它已经很久没有动了。', '猫_同伴')), sound='catOpen', progress=8)
scene('猫_同伴', 'cat', '01', '另一个微弱的呼吸', '猫/1.jpg', '牢笼里的灰猫彼此依偎',
      '(set: $catCompanion to true)' + para('你挤过去，轻轻碰了碰它的额头。它抬起眼睛，朝你发出一声很轻的呼噜。') + para('“等我找到了暖和的地方……<br>我也想带你去。”', 'voice') + memory('角落里，还有一个在等门打开的同伴。'), '猫_光', '一起望向门外 →', 'catOpen', progress=14)
scene('猫_光', 'cat', '02', '今天，来了一道光', '猫/2.jpg', '猫想象中有沙发、落地灯和猫窝的温暖房间',
      para('“好乖的小猫呀，跟我回家吧。<br>家里有软软的沙发，暖黄的落地灯，还有专门为你准备的猫窝哦……”', 'voice') + para('“沙发……落地灯……家？如果那是真的，该多好。”', 'thought') + choices(('相信那个关于家的承诺', '你已经等了很久，很久。', '猫_饭'), ('留意那只伸进来的手', '它摘下了笼子上的一张标签。', '猫_标签')), sound='catOpen', progress=18)
scene('猫_标签', 'cat', '02', '被撕下的名字', '猫/1.jpg', '铁栏杆隔开了猫与外面的人类',
      '(set: $catTag to true)' + para('那只手没有先抱你。它撕下笼门上的旧标签，换了一张写着“健康、活泼”的纸。') + para('角落的纸箱里，塞着许多一样的标签。<br>你不知道那些字是什么意思，只记得上面的气味。', 'voice') + memory('写着“健康”的标签，可以随时被换掉。'), '猫_饭', '看向送进来的食碗 →', 'catOpen', progress=24)
scene('猫_饭', 'cat', '03', '一碗特别的饭', '猫/3.jpg', '白色背景上的淡紫色食碗',
      para('他们给了我一碗特别的饭，闻起来有一点奇怪。<br>饥饿让我，几乎顾不上那么多。', 'voice') + choices(('靠近食碗', '先吃一点，也许就不冷了。', '猫_咀嚼'), ('把鼻子凑近一点', '有一种，你从未闻过的苦味。', '猫_药味')), sound='catInteract', progress=28)
scene('猫_药味', 'cat', '03', '饭里藏着的东西', '猫/4.jpg', '食碗中的胶囊显露出与食物不同的形状',
      '(set: $catMedicine to true)' + para('你拨开上面的饭，露出了几粒硬硬的东西。<br>它们的味道，让鼻子发酸。') + para('“这真的，是给我吃的吗？”', 'voice') + choices(('还是吃下去吧', '肚子里空空的，比苦味还难受。', '猫_咀嚼'), ('先把食碗推开', '让那只手，听见一点不同的声音。', '猫_推碗')), sound='catInteract', progress=33)
scene('猫_推碗', 'cat', '03', '一只被推开的碗', '猫/4.jpg', '猫用爪子把装有药物的食碗推向笼门',
      para('你把碗推到笼门边。瓷碗碰到铁栏杆，发出一声轻响。<br>门外的人没有回头。') + '(if: $catTag)[' + para('那张被撕下的旧标签，正好落在笼门外。<br>你伸出爪子，把它和碗一起拨到走道上。', 'voice') + '](else:)[' + para('你望着门外的光，不知道还有谁，会朝这里看一眼。', 'voice') + ']' + choices(('等脚步声远去，再吃一点', '你仍想相信那个温暖的家。', '猫_咀嚼')) + '(if: $catTag and $catMedicine)[' + choices(('继续敲响笼门', '你把旧标签，留在了食碗旁。', '猫_求助')) + ']', sound='catInteract', progress=37)
scene('猫_求助', 'cat', '04', '门外的另一个人', '猫/1.jpg', '猫望向牢笼外，等待一双愿意停下来的眼睛',
      para('走道里响起另一串脚步。那个人没有先说“好乖”，而是在笼门前蹲了下来。') + para('“这碗里是什么？为什么标签上的编号对不上？”', 'voice') + '(if: $catCompanion)[' + para('你回过头，望向角落里的小猫。它还在等你。', 'thought') + ']', sound='catOpen', extra=task('signal', '轻轻敲响笼门', '再让那个人，多看一眼 · 0 / 3', '这一次，门向你打开 →', '猫_救助', 3, '敲响三次。把食碗与旧标签，留在它能看见的地方。'), progress=83)
scene('猫_咀嚼', 'cat', '03', '奇怪的味道', '猫/4.jpg', '食碗中出现了写着兴奋的胶囊',
      para('饭里，好像藏着什么。', 'voice'), sound='catInteract',
      extra=task('chew', '尝试咀嚼', '咀嚼，然后吞咽。', '吞咽下去 →', '猫_色彩', hint='你太饿了。牙齿轻轻碰到了碗里的东西。'), progress=38)
scene('猫_色彩', 'cat', '04', '世界突然有了色彩', '猫/5.jpg', '原本灰暗的猫笼变成低饱和的粉、蓝、绿等彩色斑块',
      para('“我好像飘了起来。<br>世界突然有了色彩。”', 'voice') + para('冰冷的栏杆，也变得像糖果一样。', 'thought'), '猫_新家', '去往那个家 →', 'catInteract', classes='is-colour-scene', progress=48)
scene('猫_新家', 'cat', '05', '如约而至的“家”', '猫/6.jpg', '有地毯、绿植、沙发和猫画像的柔和房间',
      '<h1>我有家啦。</h1>' + para('这里有地毯，有植物，墙上还挂着我。<br>一切，都和梦里的样子一样。', 'voice') + '<p class="thought">(link: "看看沙发")[软软的沙发，原来真的存在。]　·　(link: "看看墙上的画")[画里的我，看起来很幸福。]</p>' + '(if: $catCompanion)[' + para('“如果角落里的它，也能住进来就好了。”', 'thought') + ']' + '(if: $catTag)[' + memory('笼门上那张被撕下的标签。它说，我很健康。') + ']' + para('可是……为什么我的头越来越沉，身体好像有点发热……', 'thought') + choices(('闭上眼睛，再睁开', '让这阵眩晕，慢慢过去。', '猫_祭司'), ('走到窗边透一口气', '光的另一边，是什么？', '猫_窗边')), sound='catOpen', progress=61)
scene('猫_窗边', 'cat', '05', '灯光以外', '猫/6.jpg', '温暖房间的窗户透进朦胧的光',
      para('你想跳上窗台，后腿却没有跟上来。<br>有人把你轻轻抱起，摸了摸你滚烫的额头。') + para('“不对……你怎么会病得这么快？”', 'voice') + para('你终于知道，那盏灯是真的。<br>只是承诺你健康的那个人，没有说真话。', 'thought'), '猫_祭司', '在那双手里，慢慢闭上眼睛 →', 'catEnd', progress=70)
scene('猫_祭司', 'cat', '06', '喵星之门', '猫/7祭司说话猫.jpg', '背着十字架、戴着骨饰的猫祭司站在猫面前',
      para('很烫……全身都好痛。面前好像站着一个高大的影子。') + para('“小可怜，你的寿命只有短暂的一周。<br>你的身体已经撑不住了。走吧，前面就是没有痛苦的喵星天堂。”', 'voice') + actions(('前往 · 走向那道光', '猫_天堂'), ('放弃 · 闭上眼睛', '猫_告别')), sound='catEnd', progress=78)
scene('猫_天堂', 'cat', '07', '选择 A · 前往', '猫/6.jpg', '猫再一次望见它梦想中的温暖房间',
      '<div class="ending-label">THE OTHER SIDE / 光的另一边</div><h1>你来到了天堂</h1>' + para('这里不再疼痛。那盏暖黄的灯，终于为你亮着。', 'voice') + para('由于你的勇敢选择，这场骗局的一角，开始被揭开。', 'thought'), '猫_新闻前往', '看看它后来留下的痕迹 →', 'catEnd', classes='ending', progress=90)
scene('猫_告别', 'cat', '07', '选择 B · 放弃', '猫/7祭司说话猫.jpg', '猫闭上双眼，祭司的身影逐渐隐入黑暗',
      para('“我好累。终于来到了我梦想中的家，<br>但我好像撑不住了。”', 'voice') + para('“睡吧，孩子。下辈子，不要再遇到无良的猫贩子了。”', 'thought') + para('祭司的声音，渐渐远去。', 'thought'), '猫_新闻放弃', '在故事之外，仍有人记得你 →', 'catEnd', classes='ending ending-cat-dark', progress=90)
ending_role = 'cat'
scene('猫_新闻前往', 'cat', '08', '结局 A · 前往', '猫/8.jpg', '屏幕上的新闻记录了猫贩骗局被揭露的消息',
      '<div class="ending-label">ENDING 03 / 前往</div><h1>那道光之后</h1>' + para('你走向了没有痛苦的地方。你的故事，却没有就此结束。') + para('【故事中的新闻】非法宠物交易骗局被揭露。<br>短暂的“健康”背后，是被药物掩盖的疾病与反复出售的生命。', 'ending-note') + para('这一次，有人看见了它们。', 'closing') + ending_tail(), sound='catEnd', ending='cat-light', classes='ending', progress=100)
scene('猫_新闻放弃', 'cat', '08', '结局 B · 放弃', '猫/8.jpg', '屏幕上的新闻记录了猫的遭遇和猫贩团伙的骗局',
      '<div class="ending-label">ENDING 04 / 放弃</div><h1>短暂地，被爱过</h1>' + para('你被作为无法救治的宠物，进行了安乐死。<br>你终究没能在那个家，多住一些日子。') + para('【故事中的新闻】你的遭遇成为揭开骗局的线索。<br>被药物伪装成“健康”的猫，和背后的非法交易团伙，终于被看见。', 'ending-note') + para('你的遭遇，化作斩断罪恶链条的利刃。', 'closing') + ending_tail(), sound='catEnd', ending='cat-sleep', classes='ending', progress=100)
scene('猫_救助', 'cat', '08', '隐藏结局 · 门开之前', '猫/2.jpg', '一盏暖黄的灯，为被及时救助的猫亮起',
      '<div class="ending-label">HIDDEN ENDING / 门开之前</div><h1>这一次，先听见了你</h1>' + para('那个人留下了食碗，也留下了旧标签。<br>这一次，没有人再把那几粒药当成“活泼”的秘密。') + para('你被带出了笼子，接受检查与照料。真正的家还没有到来，<br>但你不用急着，在今天就变成别人喜欢的模样。') + '(if: $catCompanion)[' + para('另一只小小的笼子，放在你的旁边。角落里的同伴，也一起出来了。', 'ending-note') + '](else:)[' + para('有人回头，开始检查那些还没有打开的笼门。', 'ending-note') + ']' + para('你还有时间，慢慢等那盏灯。', 'closing') + ending_tail(), sound='catEnd', ending='cat-rescue', classes='ending', progress=100)

# 鸭子：两只可点击的对手，交替争夺六次，再进入天平与审判。
scene('鸭_泥沼', 'duck', '01', '神圣的泥沼', '鸭/鸭1.jpg', '头顶光晕的鸭子站在色彩浓烈的泥沼中',
      '<h1>泥泞，也是恩赐吗？</h1>' + para('在第几纪元的泥沼里，鸭子的头顶，长出了不属于自己的神圣光晕。') + para('它们以为泥泞是恩赐，以为被圈养是神迹。', 'voice'), '鸭_拥挤', '走向鸭群 →', 'duckOpen', progress=10)
scene('鸭_拥挤', 'duck', '02', '神明撒下水和粮', '鸭/鸭2.jpg', '一群彩色的鸭子向前挤去',
      para('“大家都在往前挤什么？”', 'voice') + para('“看啊，神明撒下了水和粮。”'), '鸭_神迹', '跟着它们挤上前 →', 'duckOpen', progress=23)
scene('鸭_神迹', 'duck', '02', '没有泥沼的天堂', '鸭/鸭3.jpg', '鸭群在高高的人类形象周围聚集，像在朝拜神明',
      para('“吃了它，我们就能去往没有泥沼的天堂。”', 'voice') + para('只有吃下神明投下的粮食，你才拥有“被挑选”的资格。', 'thought') + choices(('争夺被选中的资格', '只要再向前一点，就能拿到粮食。', '鸭_争夺'), ('扶起身旁倒下的鸭子', '它的翅膀，已经陷进泥里。', '鸭_同伴')), sound='duckOpen', progress=36)
scene('鸭_同伴', 'duck', '02', '泥里的那只翅膀', '鸭/鸭2.jpg', '拥挤的鸭群里，有一只鸭子落在后方',
      '(set: $duckHelp to true)' + para('你停了下来，用身体顶开一点拥挤的空隙。那只鸭子终于把翅膀，从泥里拔了出来。') + para('“谢谢。你也要去争那一粒粮吗？”', 'voice') + para('前面又有人撒下食物。它和你，一起望了过去。', 'thought'), '鸭_争夺', '一起，走进队伍 →', 'duckOpen', progress=43)
duel = '<div class="interaction" data-task="duel" data-goal="6"><p class="instructions">交替点击左右两只鸭子，冲撞对手，争得粮食。</p><div class="duel">'
for index, (path, alt) in enumerate([('鸭/4.jpg', '张开翅膀的粉色鸭子'), ('鸭/4 1.jpg', '张开翅膀的紫色鸭子')]):
    duel += '<button type="button" class="duel-target" data-task-action data-duck-target="' + str(index) + '" aria-label="冲撞' + ('左' if index == 0 else '右') + '侧鸭子"><img src="' + path + '" alt="' + alt + '"><span class="target-label" data-target-life>还需 3 次</span></button>'
duel += '</div><div class="duel-status"><span>圣餐 <strong data-grains>0</strong> / 6</span><span>争夺被挑选的资格</span></div><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">向左，或向右。你挤进了争抢的队伍。</p><div class="actions is-locked" data-task-next>' + link('看向你抢到的食物 →', '鸭_粮食') + '</div></div>'
scene('鸭_争夺', 'duck', '03', '被选中的资格', '鸭/4.jpg', '鸭子争抢神明撒下的粮食',
      '<h1>争夺圣餐</h1>' + para('撕咬、冲撞、踩踏。<br>你和同类，争抢着神明投下的那一粒粮食。', 'voice'), sound='duckInteract', extra=duel, classes='task-duck', progress=50)
scene('鸭_粮食', 'duck', '03', '六粒粮食', '鸭/鸭2.jpg', '争抢之后的鸭群渐渐安静下来',
      '<h1>终于，拿到了。</h1>' + para('你把粮食护在身下。它们很少，却是你用力挤出来的全部。') + '(if: $duckHelp)[' + para('刚才扶起的同伴，安静地站在你身旁。它一粒也没有抢到。', 'thought') + '](else:)[' + para('身旁还有一些鸭子，空着嘴，望着撒粮的地方。', 'thought') + ']' + choices(('全部吃下', '你不想失去被挑选的资格。', '鸭_独食'), ('分出一半', '不够去天堂，至少也能度过今天。', '鸭_分食')), sound='duckOpen', progress=58)
scene('鸭_独食', 'duck', '03', '被挑选的重量', '鸭/鸭3.jpg', '鸭子向着投粮者的方向仰望',
      para('你低下头，飞快地吃完了粮食。<br>神明的手，果然朝你伸了过来。') + para('“看，我就要被选中了。”', 'voice') + para('身旁的脚步，轻轻退开了一点。', 'thought'), '鸭_天平', '站上天平 →', 'duckOpen', progress=63)
scene('鸭_分食', 'duck', '03', '不去天堂的半份食物', '鸭/鸭2.jpg', '鸭群在泥沼中彼此靠近',
      '(set: $duckShare to true)' + para('你把一半粮食推了过去。没有光晕，也没有神迹。<br>只有几张终于不再空着的嘴。') + para('“如果今天不被选中，<br>我们可以一起去看看泥沼的边缘吗？”', 'voice') + memory('有同伴，正在等你一起离开队伍。'), '鸭_天平', '抬起头，看向那座天平 →', 'duckOpen', progress=63)
scene('鸭_天平', 'duck', '04', '残酷的砝码', '鸭/鸭5.jpg', '神圣的天平一边是蓝色的鸭子，一边是沉重的红色祭品',
      '<h1>天平衡量的是什么？</h1>' + para('神明的天平，从不衡量灵魂的重量。<br>它只衡量，脂肪的厚度。', 'voice') + '(if: $duckShare)[' + para('你的分量，不如身旁那些独自吃完粮食的鸭子。<br>第一次，没有被选中，好像也没有那么可怕。') + '](else:)[' + para('你拼命吃下的一切，是为了让自己成为更丰厚的祭品。<br>越肥美，越“光荣”，越容易被选中。') + ']', '鸭_祭司', '迎向挑选你的目光 →', 'duckOpen', progress=72)
scene('鸭_祭司', 'duck', '05', '祭司的提问', '鸭/鸭6.jpg', '鸭祭司转身望向屏幕之外的玩家',
      '<h1>这一次，它在问你。</h1>' + para('“告诉我，人类，<br>是主宰生物链的造物主吗？”', 'voice') + choices(('是', '力量，是否也意味着责任？', '鸭_是'), ('否', '那是谁，替它们决定结局？', '鸭_否')) + '(if: $duckHelp and $duckShare)[' + choices(('先问问，谁替我们决定', '你想起那只被扶起的翅膀，和分出去的半份粮食。', '鸭_反问')) + ']', sound='duckEnd', progress=83)
scene('鸭_反问', 'duck', '05', '祭司没有说过的话', '鸭/鸭6.jpg', '祭司的目光与鸭群相对',
      para('你没有望向屏幕之外的人类。你先转向祭司。') + para('“如果粮食是恩赐，为什么我们必须踩着同伴，才能得到它？<br>如果被选中是荣耀，为什么天平只看我们的重量？”', 'voice') + para('祭司没有回答。身旁那只鸭子，轻轻碰了碰你的翅膀。', 'thought') + choices(('和它一起，走向队伍之外', '没有人保证那边是天堂。', '鸭_同行'), ('仍想听听人类的回答', '你把最后的问题，留给屏幕之外。', '鸭_祭司')), sound='duckEnd', progress=94)


def fact(value, title, text, source, url):
    return '<article class="fact"><strong>' + value + '</strong><h2>' + title + '</h2><p>' + text + '</p><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + source + ' ↗</a></article>'


ending_role = 'duck'
yes_facts = '<div class="facts">' + fact('44 万亿', '美元的经济价值，依赖自然', '世界经济论坛在 2020 年估计，超过一半的全球 GDP，中度或高度依赖自然及其提供的服务。', 'WEF · Nature Risk Rising · 2020', 'https://www.weforum.org/publications/nature-risk-rising-why-the-crisis-engulfing-nature-matters-for-business-and-the-economy/') + fact('73%', '监测到的野生动物种群规模平均下降', 'WWF《地球生命力报告 2024》记录：1970—2020 年，受监测的脊椎动物种群规模平均下降 73%。', 'WWF · Living Planet Report · 2024', 'https://livingplanet.panda.org/') + fact('约 100 万', '动植物物种面临灭绝威胁', 'IPBES 在 2019 年全球评估中指出，约一百万种动植物面临灭绝威胁，其中许多可能在数十年内消失。', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + '</div>'
no_facts = '<div class="facts">' + fact('塑料', '便利之后，留下了什么？', '流入水生环境的塑料，会通过误食、缠绕和生境污染，影响水生生物的生存。', 'UNEP · Plastic pollution', 'https://www.unep.org/plastic-pollution') + fact('生境', '一片森林，无法被替代', '土地与海洋利用变化、直接利用生物、气候变化、污染和外来入侵物种，是生物多样性丧失的主要直接驱动因素。', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + fact('共存', '答案也藏在下一次选择里', '拒绝非法野生动物交易，减少一次性塑料，关注动物来源。保护它们的生存空间，也是在保护共同生活的世界。', 'UNEP · 为自然而行动', 'https://www.unep.org/') + '</div>'
scene('鸭_是', 'duck', '06', '结局 A · 是', '鸭/鸭6.jpg', '鸭祭司静静凝视着屏幕外的人类',
      '<div class="ending-label">ENDING 05 / 是</div><h1>如果你拥有力量</h1>' + para('“那么，你愿意为它们的世界负责吗？”', 'voice'), sound='duckEnd', extra=yes_facts + '<p class="facts-note">数据保留各报告的年份与统计口径。73% 指受监测种群规模指数的平均变化，并非所有动物个体减少了 73%。</p>' + ending_tail(), ending='duck-yes', classes='ending data-ending', progress=100)
scene('鸭_否', 'duck', '06', '结局 B · 否', '鸭/鸭6.jpg', '鸭祭司向屏幕外的人类提出最后一个问题',
      '<div class="ending-label">ENDING 06 / 否</div><h1>那就，留一点世界给它们</h1>' + para('“如果我们都不是造物主，<br>为什么有些生命，可以替另一些生命决定结局？”', 'voice'), sound='duckEnd', extra=no_facts + ending_tail(), ending='duck-no', classes='ending data-ending', progress=100)
scene('鸭_同行', 'duck', '06', '隐藏结局 · 队伍之外', '鸭/鸭2.jpg', '几只鸭子不再向前拥挤，转而朝着泥沼边缘走去',
      '<div class="ending-label">HIDDEN ENDING / 队伍之外</div><h1>不被选中的我们</h1>' + para('你们没有再向前挤。被扶起的同伴、吃过你半份粮食的鸭子，和你一起，慢慢走向队伍之外。') + para('那边仍然是泥沼。没有人许诺你们永恒，也没有人替你们加上光晕。<br>但今天，你们终于可以自己决定，往哪里走。') + para('至少这一次，没有谁踩着谁的翅膀。', 'closing') + ending_tail(), sound='duckEnd', ending='duck-together', classes='ending', progress=100)

entries = {
    'pig': [('pig-live', '森林仍然接纳你', '你离开了巨神，回到森林深处，活了下来。'), ('pig-fall', '沉默的庇护者', '你留下追随巨神，最终随失去的森林一同倒下。'), ('pig-guide', '把来路留给后来者', '你观察了来路与机器的气味，最后带着同伴走向森林深处。')],
    'cat': [('cat-light', '那道光之后', '你走向没有痛苦的地方。骗局的一角，开始被揭开。'), ('cat-sleep', '短暂地，被爱过', '你闭上眼睛。你的遭遇，成为揭开骗局的线索。'), ('cat-rescue', '这一次，先听见了你', '你留下了被换掉的标签与食碗，让门外的人看见骗局。')],
    'duck': [('duck-yes', '如果你拥有力量', '你回答“是”。祭司问，你是否愿意为世界负责。'), ('duck-no', '留一点世界给它们', '你回答“否”。祭司请你，为共同生活的生命留下一点世界。'), ('duck-together', '不被选中的我们', '你扶起同伴、分享粮食，最后一起走出被挑选的队伍。')],
}
journal = ''
for key, label, animal, desc, path, target in roles:
    journal += '<article class="journal-role" data-card-label="' + animal + '"><img src="' + silhouette(path) + '" alt="' + animal + '剪影"><div class="role-no">' + label + '</div><h2>' + animal + '</h2>'
    for entry_id, title, description in entries[key]:
        journal += '<div class="journal-entry" data-entry="' + entry_id + '" data-description="' + description + '"><span class="entry-state">尚未抵达 / UNDISCOVERED</span><h3>' + title + '</h3><p class="entry-copy">选择另一条路，听见另一个答案。</p></div>'
    journal += '<div class="role-enter">' + link('重走它的故事 ↗', target) + '</div></article>'
add('旅程手记', '<section data-scene="旅程手记" class="page journal"><div class="journal-head"><div class="eyebrow">TRACES / 留下的痕迹</div><h1>旅程手记</h1><p>已抵达 <span data-journal-total>0/9</span> 个结局 · 记录保存在当前浏览器</p></div><div class="journal-grid">' + journal + '</div>' + actions(('借另一双眼睛 →', '选择角色')) + '</section>')

add('样式', css, 'stylesheet')
add('游戏交互与声音', script, 'script')
data = {'ifid': IFID, 'format': 'Harlowe', 'format-version': '3.3.9', 'start': '选择角色', 'zoom': 0.7}
twee = ':: StoryTitle\n' + TITLE + '\n\n:: StoryData\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n\n'
for i, (name, body, tags) in enumerate(passages):
    twee += ':: ' + name + (' [' + tags + ']' if tags else '') + ' ' + json.dumps({'position': f'{i % 7 * 240},{i // 7 * 180}', 'size': '180,100'}) + '\n' + body + '\n\n'
(PROJECT / '新游戏.twee').write_text(twee, encoding='utf-8')
raw = []
for i, (name, body, tags) in enumerate(passages):
    if tags in ('stylesheet', 'script'):
        continue
    raw.append(f'<tw-passagedata pid="{i + 1}" name="{html.escape(name, quote=True)}" tags="{tags}" position="{i % 7 * 240},{i // 7 * 180}" size="180,100">{html.escape(body)}</tw-passagedata>')
start = next(i + 1 for i, p in enumerate(passages) if p[0] == '选择角色')
story = f'<tw-storydata name="{TITLE}" startnode="{start}" creator="Twine" creator-version="2.10.0" ifid="{IFID}" format="Harlowe" format-version="3.3.9" options="" hidden><style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css">{css}</style><script role="script" id="twine-user-script" type="text/twine-javascript">{script}</script>{"".join(raw)}</tw-storydata>'
template = json.loads((HERE / 'harlowe-3.3.9.json').read_text(encoding='utf-8'))['source']
output = template.replace('{{STORY_NAME}}', TITLE).replace('{{STORY_DATA}}', story)
if 'name="viewport"' not in output:
    output = output.replace('</head>', '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head>')
(PROJECT / '新游戏.html').write_text(output, encoding='utf-8')
print('Built', len(raw), 'passages;', len(output.encode('utf-8')), 'bytes; Twine/Harlowe 3.3.9')
