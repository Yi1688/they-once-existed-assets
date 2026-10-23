"""使用带 Pillow 的 Python：python build.py；本机 bundled Python 已包含依赖。"""
from pathlib import Path
import html
import json
import re
from functools import lru_cache
from urllib.parse import quote
from PIL import Image, ImageOps

PROJECT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
TITLE = '它们曾存在 · 神明的赠礼'
IFID = '36B3DFCC-35B5-4163-890F-E7E98B423E62'
ASSET_BASE = 'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/'
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


def asset_url(path):
    return ASSET_BASE + quote('新游戏/' + path, safe='/')


def image(path, alt, advance=False):
    width, height = image_size(path)
    return '<figure class="artwork" style="--image-ratio:' + str(round(width / height, 6)) + '"' + (' data-advance="yes"' if advance else '') + '><img src="' + html.escape(asset_url(path), quote=True) + '" alt="' + html.escape(alt, quote=True) + '" width="' + str(width) + '" height="' + str(height) + '" decoding="async"></figure>'


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
    return '<span class="cycle-word word-slot" title="点击切换文字"><span class="word-measure" aria-hidden="true">' + max(versions, key=len) + '</span><span class="word-value">(cycling-link: ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in versions) + ')</span></span>'


def reveal_word(label, answer):
    return '<span class="reveal-word word-slot" title="点击展开这句话"><span class="word-measure" aria-hidden="true">' + max((label, answer), key=len) + '</span><span class="word-value">(link: ' + json.dumps(label, ensure_ascii=False) + ')[(transition: "dissolve")+(transition-time: .55s)[' + answer + ']]</span></span>'


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
        '猪_森林': ('不像打雷', cycling('不像打雷', '也不像刮风', '从没听过')),
        '猪_光芒': ('刺眼的黄光', styled('刺眼的黄光')),
        '猪_神明': ('野猪之神', styled('野猪之神', 'outline')),
        '猫_标签': ('健康、活泼', '|health>[健康、活泼]'),
        '猫_饭': ('有一点怪', cycling('有一点怪', '有点发苦', '像是混了别的东西')),
        '猫_色彩': ('世界突然有了色彩', '(text-colour: "#666666")[' + styled('世界突然有了色彩') + ']'),
        '猫_新家': ('头越来越沉', styled('头越来越沉', 'blur')),
        '猫_祭司': ('不用再疼了', styled('不用再疼了', 'fade-in-out')),
        '鸭_泥沼': ('一圈光', styled('一圈光', 'outline')),
        '鸭_神迹': ('被挑选', cycling('被挑选', '被称重', '被带走')),
        '鸭_天平': ('你的体重', cycling('你的体重', '能卖出的价钱', '能切下多少肉')),
        '鸭_祭司': ('造物主', styled('造物主', 'shadow')),
    }
    if name in replacements:
        old, new = replacements[name]
        body = body.replace(old, new, 1)
    clues = {
        '猪_巨兽': ('灰黑色的硬壳上看不见皮毛。', changing_word('ironSkin', '灰黑色的硬壳上看不见皮毛。', '硬壳没有随着呼吸起伏。', '里面一直响着，怎么也不停。')),
        '猪_光芒': ('一股怪味', reveal_word('一股怪味', '铁锈混着机油的味道')),
        '猪_足迹': ('几行蹄印拐进了北边的小径。', reveal_word('几行蹄印拐进了北边的小径。', '小径还没被压坏，能从这里绕回密林。')),
        '猪_机油': ('只有铁锈、机油和树皮渗出的汁液。', reveal_word('只有铁锈、机油和树皮渗出的汁液。', '机器的怪味里混着刚折断的树枝味。')),
        '猪_神明': ('灯光后面，竟然长着和你一样的獠牙。', changing_word('godShape', '灯光后面，竟然长着和你一样的獠牙。', '那对獠牙比你高出许多。', '你把机器的铁臂认成了獠牙。')),
        '猪_存活': ('溪边还有野果', reveal_word('溪边还有野果', '你记得的那棵果树还在')),
        '猪_灭绝': ('你跟在巨神身后，把木屑和树桩当成神明留下的东西。', changing_word('falseGift', '你跟在巨神身后，把木屑和树桩当成神明留下的东西。', '巨神经过的地方，只有木屑和树桩。', '你低头咬了一口，嘴里全是木头渣。')),
        '猫_牢笼': ('几只猫挤成灰扑扑的一团。', changing_word('cageNames', '几只猫挤成灰扑扑的一团。', '你被夹在中间，连翻身都难。', '门一开，所有的猫就都抬起头。')),
        '猫_走道': ('走道两边是一排一样的笼子。', reveal_word('走道两边是一排一样的笼子。', '每个笼子里的猫都在盯着门口。')),
        '猫_药味': ('几粒硬东西', reveal_word('几粒硬东西', '掺进饭里的药粒')),
        '猫_推碗': ('瓷碗碰到栏杆，叮的一声。', reveal_word('瓷碗碰到栏杆，叮的一声。', '响声传进走道，没人停下来。')),
        '猫_色彩': ('栏杆变成了粉色', changing_word('sweetBars', '栏杆变成了粉色', '地面也晃了起来', '你已经站不太稳了')),
        '猫_窗边': ('“明明说是健康的……”', reveal_word('“明明说是健康的……”', '“先去医院。现在就去。”')),
        '猫_康复': ('到家时，你自己走出了笼门，慢慢爬回那张沙发。', reveal_word('到家时，你自己走出了笼门，慢慢爬回那张沙发。', '你一步步爬上沙发，这回后腿没再发软。')),
        '猫_离去': ('那个人回到家时，窗边的猫窝还空着。', reveal_word('那个人回到家时，窗边的猫窝还空着。', '他们没收起你的猫窝，还放在原来的位置。')),
        '鸭_泥沼': ('这就是神的恩赐', reveal_word('这就是神的恩赐', '吃饱了就能离开泥地')),
        '鸭_同伴': ('你用身体顶住后面的鸭子，挤出一点空地。', reveal_word('你用身体顶住后面的鸭子，挤出一点空地。', '你挡着挤过来的鸭子，等它把翅膀抽出来。')),
        '鸭_粮食': ('你把粮护在身前，数了数，只有六粒。', reveal_word('你把粮护在身前，数了数，只有六粒。', '挤了这么久，你只抢到六粒粮。')),
        '鸭_独食': ('那只手朝你伸了过来。', changing_word('choosingHand', '那只手朝你伸了过来。', '刚才撒粮的人蹲了下来。', '它看了你一眼，伸手抓向你的翅膀。')),
        '鸭_分食': ('它很快就吃完了', reveal_word('它很快就吃完了', '它一直饿着肚子')),
    }
    if name in clues:
        old, new = clues[name]
        body = body.replace(old, new, 1)
    extras = {
        '猪_森林': ('forestEcho', '再听一会儿', ['地面又震了一下。附近的鸟全飞走了。', '声音越来越近，还夹着树枝断裂的响声。', '你往林外走了两步，竖起耳朵。'], 'listen'),
        '猪_机油': ('ironBreath', '靠近以后', ['热气扑在鼻子上，你打了个喷嚏。', '这么大的东西，居然闻不到一点皮毛味。', '它刚压过的地方，泥土都翻了出来。'], 'listen'),
        '猪_喷气': ('godReply', '白雾里', ['巨神喷出的白雾从你头顶飘过。', '你一动不动，等着它再做点什么。', '雾散了，巨神又朝前挪了一步。'], 'live'),
        '猫_牢笼': ('cageEcho', '门口的动静', ['走道尽头响起了脚步声。', '钥匙碰在一起。你赶紧抬起头。'], 'after'),
        '猫_光': ('homePromise', '你没见过的家', ['沙发是可以趴着睡的地方吗？', '灯开着的时候，屋里一定很暖和吧。', '要是猫窝够软，我想一直睡到明天。'], 'listen'),
        '猫_告别': ('lastVoice', '床边', ['有人一直握着你的前爪。', '你想蹭蹭那只手，已经没有力气了。', '“我在这儿。别怕。”'], 'live'),
        '鸭_拥挤': ('crowdEcho', '身后的声音', ['“往前点，后面的都吃不到了。”', '一只脚踩住了你的尾羽。你赶紧往旁边躲。', '前面又挤了起来。没人肯往后退。'], 'listen'),
        '鸭_天平': ('scaleReply', '秤盘上', ['你动了一下，指针跟着晃。', '有人伸手按住你，又低头看了一眼秤。', '“这只差不多了。”'], 'live'),
        '鸭_祭司': ('outsideScreen', '它看着你', ['祭司转过头，盯着屏幕外。', '它没有接着说。你得自己选一个回答。'], 'after'),
    }
    if name in extras:
        addition = whisper(*extras[name])
        index = body.find('<div class="actions')
        body = body[:index] + addition + body[index:] if index >= 0 else body + addition
    if name == '猫_标签':
        body += '(after: .9s)[(enchant: ?health, (text-style: "strike")+(text-colour: "#777777"))]'
    if name == '猫_窗边':
        body += '<p class="thought macro-line">(seq-link: "来时的笼子还放在门边。", "旁边压着那张写着“健康”的纸。", "他们拍下了标签，又拿起了电话。")</p>'
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
    effects = {'猪_森林': 'forest', '猪_巨兽': 'machine', '猪_靠近': 'machine', '猪_光芒': 'light', '猪_神明': 'revelation', '猪_喷气': 'steam', '猫_色彩': 'colour', '猫_光': 'warmth', '猫_新家': 'warmth', '猫_醒来': 'warmth', '猫_告别': 'farewell', '鸭_泥沼': 'halo', '鸭_神迹': 'halo', '鸭_天平': 'scales', '鸭_祭司': 'altar'}
    attrs = ' data-sound="' + sound + '"' + (' data-ending="' + ending + '"' if ending else '') + (' data-fx="' + effects[name] + '"' if name in effects else '')
    reset = {'猪_森林': '(set: $pigTrail to false)(set: $pigOil to false)', '猫_牢笼': '(set: $catTag to false)', '鸭_泥沼': '(set: $duckHelp to false)(set: $duckShare to false)'}.get(name, '')
    add(name, reset + '<section data-scene="' + name + '" class="page scene-stage role-' + role + ' ' + classes + '"' + attrs + '>' + inner + '</section>')


def task(kind, action_label, status, next_label, target, goal=1, hint=''):
    return '<div class="interaction" data-task="' + kind + '" data-goal="' + str(goal) + '"><p class="instructions">' + hint + '</p><button type="button" class="' + ('hold-button' if kind == 'hold' else 'action-button') + '" data-task-action>' + action_label + '</button><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">' + status + '</p><div class="actions is-locked" data-task-next>' + link(next_label, target) + '</div></div>'


def ending_tail():
    return actions(('再玩一次 ↻', {'pig': '猪_森林', 'cat': '猫_牢笼', 'duck': '鸭_泥沼'}[ending_role]), ('换个角色 ↗', '选择角色'), ('查看结局记录', '旅程手记'))


add('初始化', '(set: $pigTrail to false)(set: $pigOil to false)(set: $catTag to false)(set: $duckHelp to false)(set: $duckShare to false)', 'startup')
add('页眉', '<header class="mast"><span class="brand"><em>✧</em><span>THEY ONCE EXISTED</span><span class="series-label"> / 神明的赠礼</span></span><nav aria-label="游戏导航"><button type="button" class="audio-toggle" data-audio-toggle aria-pressed="true">声音：开</button>' + link('选角', '选择角色') + link('手记 <span class="journal-number" data-journal-total>0/6</span>', '旅程手记') + '</nav></header>', 'header')

roles = [
    ('pig', '01 / THE FOREST', '野猪', '林子外来了个大家伙。<br>你从没见过这样的动物。', '素材/选角/野猪.jpg', '猪_森林'),
    ('cat', '02 / THE HOME', '猫', '有人说，要带你回家。<br>你在笼子里等了很久。', '素材/选角/猫.jpg', '猫_牢笼'),
    ('duck', '03 / THE ALTAR', '鸭子', '鸭群都在抢神明撒下的粮。<br>它们说，吃饱了就能去天堂。', '素材/选角/鸭子.jpg', '鸭_泥沼'),
]
cards = ''
for key, label, animal, desc, path, target in roles:
    cards += '<article class="role-card"><span class="role-count" data-role-count="' + key + '">0/2</span><button type="button" class="animal-preview" data-animal="' + key + '" aria-label="试听' + animal + '叫声"><img src="' + asset_url(path) + '" alt="' + animal + '的剪影"><span class="sound-hint">点击动物 · 试听叫声 ♫</span></button><div class="role-copy"><div class="role-no">' + label + '</div><h2>' + animal + '</h2><p>' + desc + '</p><div class="role-enter">' + link('开始它的故事 <span>↗</span>', target) + '</div></div></article>'
add('选择角色', '<section data-scene="选择角色" class="page selection"><div class="eyebrow">PROLOGUE / 序章</div><div class="selection-head"><h1>从它的眼睛看</h1><p>选一个角色，看看接下来会发生什么。</p></div><img class="selection-art" src="' + asset_url(silhouette('素材/选角/它们.jpg')) + '" alt="野猪、猫与鸭子的剪影"><div class="role-grid">' + cards + '</div><footer class="selection-foot"><span>三个故事 · 每个故事两个结局 · 带下划线的文字可以点击</span><span class="series">它们曾存在 / 神明的赠礼</span></footer></section>')

# 野猪：保留观察支线，结尾只保留离开与留下。
scene('猪_森林', 'pig', '01', '林子外的声音', '新/1在森林.jpg', '从野猪的视角看向幽蓝色的树林',
      '<h1>什么东西在响？</h1>' + para('“不像打雷。怎么地也在动？”', 'voice') + para('你停下来，朝声音传来的方向看去。', 'thought'), '猪_巨兽', '去林子边看看 →', 'pigOpen', progress=8)
scene('猪_巨兽', 'pig', '01', '林子外的声音', '新/2看见伐木机.jpg', '灰黑色的伐木机出现在树林之外',
      para('空地上，一个大家伙正慢慢往前挪。<br>灰黑色的硬壳上看不见皮毛。') + para('“这么大……它吃什么长的？”', 'voice') + choices(('走近一点', '看看它到底长什么样。', '猪_靠近'), ('沿林缘绕一圈', '先看清周围有没有路。', '猪_足迹')), sound='pigOpen', progress=16)
scene('猪_足迹', 'pig', '01', '林边的小径', '新/1在森林.jpg', '森林深处留下了一条尚未被机器推平的小径',
      '(set: $pigTrail to true)' + para('你绕着空地走了一段。<br>几行蹄印拐进了北边的小径。') + para('“这边还能走。先记住，等会儿从这里回去。”', 'voice') + memory('北边有条小径，入口旁长着一棵老树。'), '猪_靠近', '再去看看大家伙 →', 'pigOpen', progress=22)
scene('猪_靠近', 'pig', '02', '硬壳里的轰鸣', '新/3伐木机靠近.jpg', '伐木机的轮盘和钢铁躯体逐渐逼近',
      para('它碰到一棵树。树干晃了几下，突然折断。<br>枝叶被卷进去，碎木屑落了一地。') + para('“连这么粗的树都咬得断……”', 'voice'), '猪_光芒', '再靠近一点 →', 'pigOpen', progress=25)
scene('猪_光芒', 'pig', '02', '刺眼的灯', '新/4机器发光.jpg', '停在森林边缘的机器散发刺眼的黄色光芒',
      para('大家伙停住了。两束刺眼的黄光照在你脸上。<br>风里飘来一股怪味，你以前没有闻过。') + para('“盯着我干什么？这是我的地盘。”', 'voice') + choices(('亮出獠牙', '不能让它再往前走了。', '猪_撞击'), ('先闻一闻风', '这家伙身上的味道不对。', '猪_机油')), sound='pigOpen', progress=34)
scene('猪_机油', 'pig', '02', '奇怪的气味', '新/3伐木机靠近.jpg', '机器轮盘之间的黑暗缝隙',
      '(set: $pigOil to true)' + para('你嗅了又嗅。没有皮毛味，也没有血腥气。<br>只有铁锈、机油和树皮渗出的汁液。') + para('“它一直在叫，怎么不用喘气？”', 'voice') + memory('这个大家伙没有动物的气味，硬壳上也没有呼吸的起伏。'), '猪_撞击', '用獠牙试一试 →', 'pigOpen', progress=40)
scene('猪_撞击', 'pig', '03', '撞上去', '新/5野猪靠近.jpg', '野猪举起獠牙迎向发光的机器',
      para('“走开！不许再碰这里的树！”', 'voice') + para('你压低头，用獠牙撞上它的硬壳。', 'thought'), sound='pigInteract',
      extra=task('ram', '用獠牙撞击机械', '獠牙撞击 · 0 / 5', '抬头看看 →', '猪_神明', 5, '点击五次，试着把它赶出森林。'), progress=45)
scene('猪_神明', 'pig', '04', '你认出的神明', '新/6机器变野猪.jpg', '机械在野猪眼中化为长着巨型獠牙的野猪神明',
      para('第五次撞上去，獠牙震得发麻。你抬起头。<br>灯光后面，竟然长着和你一样的獠牙。') + para('“原来是野猪之神……难怪我撞不动。”', 'voice'), '猪_喷气', '仰头望着它 →', 'pigWorship', progress=57)
scene('猪_喷气', 'pig', '04', '巨神的吐息', '新/7野猪喷气.jpg', '机械巨神向外喷出白雾，渺小的蓝色野猪在下方仰望',
      para('巨神身上突然喷出一团白雾。<br>你缩了缩脖子，又忍不住仰头去看。', 'voice'), sound='pigWorship',
      extra=task('hold', '按住 · 注视巨神喷气', '按住按钮，观察巨神喷出的白雾。', '等白雾散开 →', '猪_抉择', hint='按住约两秒，观察巨神喷气。'), progress=70)
scene('猪_抉择', 'pig', '05', '走，还是留下', '新/野猪说话.jpg', '野猪站在沉默的钢铁巨神面前',
      '<h1>还要留在这里吗？</h1>' + para('“它这么厉害，跟着它应该不会挨饿吧？”', 'voice') + para('身后又倒下一棵树。你回头看了看林子。') + '(if: $pigOil)[' + memory('可它没有呼吸。你始终没想明白。') + '](if: $pigTrail)[' + memory('北边那条小径还在，可以从老树旁边走。') + ']' + choices(('离开 · 回到森林', '去找你熟悉的溪水和野果。', '猪_存活'), ('留下 · 追随巨神', '这么强大的神，总会照顾你吧。', '猪_灭绝')), sound='pigWorship', progress=84)
ending_role = 'pig'
scene('猪_存活', 'pig', '06', '结局 A · 离开', '新/1在森林.jpg', '野猪转身回到深蓝色的森林',
      '<div class="ending-label">ENDING 01 / 离开</div><h1>回到林子里</h1>' + para('你最后看了一眼巨神，转身钻进树林。<br>走出很远，那阵轰鸣还没有停。') + '(if: $pigTrail)[' + para('你沿北边的小径绕过空地，在溪边停了下来。') + '](else:)[' + para('你顺着熟悉的气味往里走，终于找到了溪水。') + ']' + para('溪边还有野果。你低头喝了水，肚子也渐渐填饱了。') + para('今晚就在这里睡吧。', 'closing') + ending_tail(), sound='pigLive', ending='pig-live', classes='ending', progress=100)
scene('猪_灭绝', 'pig', '06', '结局 B · 留下', '新/2看见伐木机.jpg', '森林的颜色褪去，只留下继续工作的伐木机',
      '<div class="ending-label">ENDING 02 / 留下</div><h1>它没有回头</h1>' + para('你跟在巨神身后，把木屑和树桩当成神明留下的东西。<br>可那些东西吃不下去。你只好继续等。') + para('几天后，机器开走了。周围没有树荫，溪水也被泥堵住。<br>你饿得站不起来，还是望着它离开的方向。') + para('它一直没有回来。', 'closing') + ending_tail(), sound='pigFall', ending='pig-fall', classes='ending ending-pig-fall', progress=100)

# 猫：保留笼外观察、食物与窗边支线；前往为康复，放弃为告别。
scene('猫_牢笼', 'cat', '01', '笼子里的日子', '猫/1.jpg', '灰色的猫挤在冰冷的铁栏杆之后',
      '<h1>今天会有人来吗？</h1>' + para('铁栏杆很凉。<br>几只猫挤成灰扑扑的一团。') + para('“外面是不是暖和一点？”', 'voice') + choices(('朝门口看去', '有人朝这边走过来了。', '猫_光'), ('凑到栏杆边看看', '把头伸出去，看看笼子外面。', '猫_走道')), sound='catOpen', progress=8)
scene('猫_走道', 'cat', '01', '栏杆外面', '猫/1.jpg', '猫从铁栏杆之间望向走道',
      para('你贴着栏杆往外看。走道两边是一排一样的笼子。<br>窗户很高，阳光只照得到最上面一层。') + para('“我要是再长高一点，就能晒到了吧。”', 'voice'), '猫_光', '门口有人来了 →', 'catOpen', progress=14)
scene('猫_光', 'cat', '02', '有人要带你走', '猫/2.jpg', '猫想象中有沙发、落地灯和猫窝的温暖房间',
      para('“这只好乖。跟我回家吧，猫窝都买好了。”', 'voice') + para('你听不懂所有的话，只听出声音很轻。<br>你往前挤了挤，把脸贴在栏杆上。') + choices(('伸头蹭蹭那只手', '你已经很久没被摸过了。', '猫_饭'), ('看一眼笼门上的纸', '旁边的人正忙着换标签。', '猫_标签')), sound='catOpen', progress=18)
scene('猫_标签', 'cat', '02', '新换的标签', '猫/1.jpg', '铁栏杆隔开了猫与外面的人类',
      '(set: $catTag to true)' + para('笼门上的纸被撕了下来，新纸上写着“健康、活泼”。<br>旧纸揉成一团，扔进了旁边的箱子。') + para('“这只没问题，吃东西可积极了。”', 'voice') + memory('你昨晚一直没胃口。今天，他们却说你很健康。'), '猫_饭', '一碗饭送了进来 →', 'catOpen', progress=24)
scene('猫_饭', 'cat', '03', '送来的饭', '猫/3.jpg', '白色背景上的淡紫色食碗',
      para('“总算有饭了。可是闻着有一点怪。”', 'voice') + para('肚子咕噜响了一声。你已经饿了很久。', 'thought') + choices(('先吃一点', '填饱肚子再说。', '猫_咀嚼'), ('凑近闻一闻', '饭里混着一股苦味。', '猫_药味')), sound='catInteract', progress=28)
scene('猫_药味', 'cat', '03', '饭里有什么', '猫/4.jpg', '食碗中的胶囊显露出与食物不同的形状',
      para('你用爪子拨开上面的饭，下面有几粒硬东西。<br>鼻子凑过去，苦味更重了。') + para('“这也能吃吗？”', 'voice') + choices(('还是吃一点', '肚子实在太饿了。', '猫_咀嚼'), ('把食碗推开', '你不喜欢这个味道。', '猫_推碗')), sound='catInteract', progress=33)
scene('猫_推碗', 'cat', '03', '推开食碗', '猫/4.jpg', '猫用爪子把装有药物的食碗推向笼门',
      para('你把碗推到门边，瓷碗碰到栏杆，叮的一声。<br>门外的人低头看了看，又把碗推回来。') + para('“吃吧，吃完就带你走。”', 'voice') + choices(('低头吃一点', '你还在惦记刚才说好的猫窝。', '猫_咀嚼')), sound='catInteract', progress=37)
scene('猫_咀嚼', 'cat', '03', '苦味', '猫/4.jpg', '食碗中出现了写着兴奋的胶囊',
      para('“就吃一口。”', 'voice'), sound='catInteract', extra=task('chew', '尝试咀嚼', '咬一咬，再咽下去。', '吞咽下去 →', '猫_色彩', hint='饭里的硬东西硌到了牙。'), progress=38)
scene('猫_色彩', 'cat', '04', '突然亮起来的笼子', '猫/5.jpg', '原本灰暗的猫笼变成低饱和的粉、蓝、绿等彩色斑块',
      para('“咦，世界突然有了色彩。”', 'voice') + para('栏杆变成了粉色。身上也轻飘飘的。<br>你想站起来，却差点撞上笼门。', 'thought'), '猫_新家', '有人把你抱了起来 →', 'catDream', classes='is-colour-scene', progress=48)
scene('猫_新家', 'cat', '05', '到家了', '猫/6.jpg', '有地毯、绿植、沙发和猫画像的柔和房间',
      '<h1>这里就是家吗？</h1>' + para('“沙发好软。我真的可以睡在这里？”', 'voice') + '<p class="thought">(link: "看看沙发")[你踩了两下，爪子陷进软垫里。]　·　(link: "看看墙上的画")[画里也有一只猫。你盯着它看了一会儿。]</p>' + '(if: $catTag)[' + memory('笼门上的纸写着“健康、活泼”。你现在却连尾巴都抬不动。') + ']' + para('才过了一会儿，头越来越沉，身上也热得难受。', 'thought') + choices(('趴下来歇一会儿', '也许只是一路上太累了。', '猫_祭司'), ('走到窗边', '那里好像凉快一点。', '猫_窗边')), sound='catDream', progress=61)
scene('猫_窗边', 'cat', '05', '没能跳上去', '猫/6.jpg', '温暖房间的窗户透进朦胧的光',
      para('你想跳上窗台，后腿一软，摔回了地毯上。<br>带你回来的人赶紧把你抱起来。') + para('“明明说是健康的……”', 'voice') + para('手掌贴在你的额头上。有人开始翻找手机。', 'thought'), '猫_祭司', '眼前渐渐模糊 →', 'catDream', progress=70)
scene('猫_祭司', 'cat', '06', '半梦半醒', '猫/7祭司说话猫.jpg', '背着十字架、戴着骨饰的猫祭司站在猫面前',
      para('你昏昏沉沉地趴着。一个高大的影子出现在面前。') + para('“跟我走吧，过去就不用再疼了。”', 'voice') + para('影子后面有一扇门。身旁却一直有人在叫你：<br>“醒醒，我们到医院了。”', 'thought') + choices(('前往 · 回到人声里', '你还想回那个家。', '猫_醒来'), ('放弃 · 我太累了', '你已经听不清身边的话。', '猫_告别')), sound='catPriest', progress=78)
scene('猫_醒来', 'cat', '07', '选择 A · 前往', '猫/2.jpg', '暖黄的灯光映出房间的轮廓',
      '<h1>你动了一下爪子</h1>' + para('“它动了。医生，它刚才动了！”', 'voice') + para('你费力睁开眼睛，闻到一股消毒水的气味。<br>刚才那个人还在旁边，外套都没来得及脱。') + para('接下来的几天，你留在医院接受治疗。', 'thought'), '猫_康复', '几天以后 →', 'catDream', progress=90)
scene('猫_告别', 'cat', '07', '选择 B · 放弃', '猫/7祭司说话猫.jpg', '猫闭上双眼，祭司的身影逐渐隐入黑暗',
      para('“我想再睡一会儿。”', 'voice') + para('你朝那个影子走去。它慢慢推开了门。<br>床边的人又叫了你几声，你没有听见。') + para('医生继续抢救。监护仪的声音却慢了下来。', 'thought'), '猫_离去', '后来 →', 'catEnd', classes='ending ending-cat-dark', progress=90)
ending_role = 'cat'
scene('猫_康复', 'cat', '08', '结局 A · 前往', '猫/6.jpg', '治疗后的猫回到了有沙发和猫窝的家',
      '<div class="ending-label">ENDING 03 / 前往</div><h1>猫窝还给你留着</h1>' + para('病情稳定后，那个人来接你出院。<br>到家时，你自己走出了笼门，慢慢爬回那张沙发。') + para('饭碗换了位置，水就在旁边。<br>你吃了几口，蜷进窗边的猫窝里。') + para('【故事后续】他们留下检查记录和购猫凭据，举报了卖猫的人。', 'ending-note') + para('这次可以好好睡一觉了。', 'closing') + ending_tail(), sound='catDream', ending='cat-light', classes='ending', progress=100)
scene('猫_离去', 'cat', '08', '结局 B · 放弃', '猫/8.jpg', '屏幕上的新闻记录了猫贩骗局被调查的消息',
      '<div class="ending-label">ENDING 04 / 放弃</div><h1>没住够的家</h1>' + para('抢救没能留住你。你只在新家待了不到一天。<br>那个人回到家时，窗边的猫窝还空着。') + para('【故事后续】他们拿着检查记录报了案。<br>卖家用药物掩盖病情、把病猫当健康猫出售的事，开始接受调查。', 'ending-note') + para('沙发上还留着几根你的毛。', 'closing') + ending_tail(), sound='catEnd', ending='cat-sleep', classes='ending', progress=100)

# 鸭子：保留让路、分粮的中间分支，最后只回答是或否。
scene('鸭_泥沼', 'duck', '01', '围栏里面', '鸭/鸭1.jpg', '头顶光晕的鸭子站在色彩浓烈的泥沼中',
      '<h1>这里就是全部吗？</h1>' + para('你从小就住在这片泥地里。围栏很高，水一直很浑。<br>每只鸭子头顶都有一圈光。') + para('“这就是神的恩赐。”大家都这么说。', 'voice'), '鸭_拥挤', '前面突然挤了起来 →', 'duckOpen', progress=10)
scene('鸭_拥挤', 'duck', '02', '开饭了', '鸭/鸭2.jpg', '一群彩色的鸭子向前挤去',
      para('“往哪儿挤？出了什么事？”', 'voice') + para('“神明来了！今天又有粮！”'), '鸭_神迹', '跟上去看看 →', 'duckOpen', progress=23)
scene('鸭_神迹', 'duck', '02', '它们说的天堂', '鸭/鸭3.jpg', '鸭群在高高的人类形象周围聚集，像在朝拜神明',
      para('“多吃点。吃得壮，才会被挑选。”', 'voice') + para('听说被选中的鸭子会离开这里，去没有泥水的天堂。<br>去过的鸭子，一只也没回来过。', 'thought') + choices(('挤到前面抢粮', '再等下去就吃不到了。', '鸭_争夺'), ('先扶起旁边的鸭子', '它被挤倒了，翅膀还陷在泥里。', '鸭_同伴')), sound='duckWorship', progress=36)
scene('鸭_同伴', 'duck', '02', '被踩住的翅膀', '鸭/鸭2.jpg', '拥挤的鸭群里，有一只鸭子落在后方',
      '(set: $duckHelp to true)' + para('你用身体顶住后面的鸭子，挤出一点空地。<br>它收回翅膀，晃了几下才站稳。') + para('“谢谢。快去吧，要撒完了。”', 'voice'), '鸭_争夺', '转身去抢粮 →', 'duckWorship', progress=43)
duel = '<div class="interaction" data-task="duel" data-goal="6"><p class="instructions">交替点击左右两只鸭子，挤过去抢粮。</p><div class="duel">'
for index, (path, alt) in enumerate([('鸭/4.jpg', '张开翅膀的粉色鸭子'), ('鸭/4 1.jpg', '张开翅膀的紫色鸭子')]):
    duel += '<button type="button" class="duel-target" data-task-action data-duck-target="' + str(index) + '" aria-label="冲撞' + ('左' if index == 0 else '右') + '侧鸭子"><img src="' + asset_url(path) + '" alt="' + alt + '"><span class="target-label" data-target-life>还需 3 次</span></button>'
duel += '</div><div class="duel-status"><span>粮食 <strong data-grains>0</strong> / 6</span><span>先挤到前面去</span></div><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">左边挤不动，就试试右边。</p><div class="actions is-locked" data-task-next>' + link('看看抢到了多少 →', '鸭_粮食') + '</div></div>'
scene('鸭_争夺', 'duck', '03', '挤进去', '鸭/4.jpg', '鸭子争抢神明撒下的粮食',
      '<h1>抢不到就没得吃</h1>' + para('你张开翅膀往前挤。羽毛被扯住，脚下也踩到了什么。<br>可粮就那么一点，谁都不肯让。', 'voice'), sound='duckInteract', extra=duel, classes='task-duck', progress=50)
scene('鸭_粮食', 'duck', '03', '抢到的粮', '鸭/鸭2.jpg', '争抢之后的鸭群渐渐安静下来',
      '<h1>只有这么一点</h1>' + para('你把粮护在身前，数了数，只有六粒。') + '(if: $duckHelp)[' + para('刚才那只鸭子站在旁边。它没抢到，翅膀还在抖。', 'thought') + '](else:)[' + para('旁边有只鸭子低头啄着泥，像是在找漏下的粮。', 'thought') + ']' + choices(('自己吃完', '你也饿了一整天。', '鸭_独食'), ('分出一半', '让旁边那只也吃一点。', '鸭_分食')), sound='duckWorship', progress=58)
scene('鸭_独食', 'duck', '03', '轮到你了', '鸭/鸭3.jpg', '鸭子向着投粮者的方向仰望',
      para('你赶紧把粮吃下去。那只手朝你伸了过来。') + para('“是我吗？这次真的轮到我了？”', 'voice') + para('它抓住你的翅膀，把你提了起来。', 'thought'), '鸭_天平', '被放上秤盘 →', 'duckWorship', progress=63)
scene('鸭_分食', 'duck', '03', '三粒粮', '鸭/鸭2.jpg', '鸭群在泥沼中彼此靠近',
      '(set: $duckShare to true)' + para('你把三粒粮推到旁边。它很快就吃完了。') + para('“还有吗？”', 'voice') + para('你低头看看自己剩下的三粒，还没来得及吃，<br>一只手就抓住了你的翅膀。'), '鸭_天平', '被放上秤盘 →', 'duckWorship', progress=63)
scene('鸭_天平', 'duck', '04', '称重', '鸭/鸭5.jpg', '神圣的天平一边是蓝色的鸭子，一边是沉重的红色祭品',
      '<h1>原来是在称重</h1>' + para('“它在看什么？我够不够虔诚吗？”', 'voice') + para('秤盘晃了几下。那个人盯着刻度，只关心你的体重。') + '(if: $duckShare)[' + para('刚才分出去的三粒粮，似乎也没让指针少动多少。', 'thought') + '](else:)[' + para('你拼命抢来的粮，会让你再重一点，也更早被带走。', 'thought') + ']', '鸭_祭司', '抬起头 →', 'duckScales', progress=72)
scene('鸭_祭司', 'duck', '05', '祭司转过身', '鸭/鸭6.jpg', '鸭祭司转身望向屏幕之外的玩家',
      '<h1>它在问屏幕外的你</h1>' + para('“人类，你觉得自己是造物主吗？”', 'voice') + choices(('是', '人能决定别的动物怎样生活。', '鸭_是'), ('否', '人也是自然中的一种动物。', '鸭_否')), sound='duckEnd', progress=83)


def fact(value, title, text, source, url):
    return '<article class="fact"><strong>' + value + '</strong><h2>' + title + '</h2><p>' + text + '</p><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + source + ' ↗</a></article>'


ending_role = 'duck'
yes_facts = '<div class="facts">' + fact('44 万亿', '美元的经济价值，依赖自然', '世界经济论坛在 2020 年估计，超过一半的全球 GDP 中度或高度依赖自然及其提供的服务。', 'WEF · Nature Risk Rising · 2020', 'https://www.weforum.org/publications/nature-risk-rising-why-the-crisis-engulfing-nature-matters-for-business-and-the-economy/') + fact('73%', '监测到的野生动物种群规模平均下降', 'WWF《地球生命力报告 2024》记录：1970—2020 年，受监测的脊椎动物种群规模平均下降 73%。', 'WWF · Living Planet Report · 2024', 'https://livingplanet.panda.org/') + fact('约 100 万', '动植物物种面临灭绝威胁', 'IPBES 在 2019 年全球评估中指出，约一百万种动植物面临灭绝威胁，其中许多可能在数十年内消失。', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + '</div>'
no_facts = '<div class="facts">' + fact('塑料', '丢掉以后，它去了哪里？', '流入水生环境的塑料会通过误食、缠绕和生境污染，影响水生生物的生存。', 'UNEP · Plastic pollution', 'https://www.unep.org/plastic-pollution') + fact('生境', '动物需要能生活的地方', '土地与海洋利用变化、直接利用生物、气候变化、污染和外来入侵物种，是生物多样性丧失的主要直接驱动因素。', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + fact('日常', '能从哪些小事做起？', '少用一次性塑料，不买来源不明的野生动物，了解宠物的来源。看见非法交易，可以保留证据并举报。', 'UNEP · 为自然而行动', 'https://www.unep.org/') + '</div>'
scene('鸭_是', 'duck', '06', '结局 A · 是', '鸭/鸭6.jpg', '鸭祭司静静凝视着屏幕外的人类',
      '<div class="ending-label">ENDING 05 / 是</div><h1>能决定，然后呢？</h1>' + para('“那这些事发生的时候，你打算怎么办？”', 'voice'), sound='duckEnd', extra=yes_facts + '<p class="facts-note">73% 是受监测种群规模指数的平均变化，不代表所有动物个体减少了 73%。各项数据的年份和来源见卡片。</p>' + ending_tail(), ending='duck-yes', classes='ending data-ending', progress=100)
scene('鸭_否', 'duck', '06', '结局 B · 否', '鸭/鸭6.jpg', '鸭祭司向屏幕外的人类提出最后一个问题',
      '<div class="ending-label">ENDING 06 / 否</div><h1>它们也得有地方活</h1>' + para('“可它们住哪里、吃什么、什么时候被带走，<br>不还是人说了算吗？”', 'voice'), sound='duckEnd', extra=no_facts + ending_tail(), ending='duck-no', classes='ending data-ending', progress=100)

entries = {
    'pig': [('pig-live', '回到林子里', '你离开机器，找到溪水和野果，在森林里活了下来。'), ('pig-fall', '它没有回头', '你一直跟着机器。树被砍完后，它走了，没给你留下吃的。')],
    'cat': [('cat-light', '猫窝还给你留着', '你在医院醒来，接受治疗。病情稳定后，有人接你回家。'), ('cat-sleep', '没住够的家', '抢救没能留住你。带你回家的人留下病历，举报了卖家。')],
    'duck': [('duck-yes', '能决定，然后呢？', '你回答“是”。祭司问，你打算怎样对待这些动物。'), ('duck-no', '它们也得有地方活', '你回答“否”。祭司提醒你，动物的生活仍在被人决定。')],
}
journal = ''
for key, label, animal, desc, path, target in roles:
    journal += '<article class="journal-role" data-card-label="' + animal + '"><img src="' + asset_url(silhouette(path)) + '" alt="' + animal + '剪影"><div class="role-no">' + label + '</div><h2>' + animal + '</h2>'
    for entry_id, title, description in entries[key]:
        journal += '<div class="journal-entry" data-entry="' + entry_id + '" data-description="' + description + '"><span class="entry-state">尚未完成 / UNDISCOVERED</span><h3>' + title + '</h3><p class="entry-copy">走完这条路线后，这里会记下结局。</p></div>'
    journal += '<div class="role-enter">' + link('再玩一次 ↗', target) + '</div></article>'
add('旅程手记', '<section data-scene="旅程手记" class="page journal"><div class="journal-head"><div class="eyebrow">JOURNAL / 结局记录</div><h1>旅程手记</h1><p>已完成 <span data-journal-total>0/6</span> 个结局 · 记录保存在当前浏览器</p></div><div class="journal-grid">' + journal + '</div>' + actions(('返回选角 →', '选择角色')) + '</section>')


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
