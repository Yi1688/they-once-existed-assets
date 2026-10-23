"""English strings for the shared interaction script and CSS hints."""
import json
import re

SCRIPT_TEXT = {
    'they-once-existed-new-gift-v1': 'they-once-existed-new-gift-en-v1',
    '音乐已关闭，点击开启': 'Music is off · Click to turn it on',
    '点击开启音乐': 'Click to turn on the music',
    '音乐暂时没加载好，点击重试': 'Music could not load · Click to retry',
    '音乐已开启': 'Music is on',
    '正在加载音乐…': 'Loading music…',
    '声音：关': 'Sound: off', '声音：开': 'Sound: on',
    '打开声音': 'Turn sound on', '关闭声音': 'Turn sound off',
    '声音已关闭': 'Sound is off',
    '第五次撞击之后，机械显出了野猪神明的轮廓': 'After the fifth strike, the machine takes the shape of a boar god',
    '猫_牢笼': 'Cat-Cage', '听听牢笼里的猫叫': 'Listen to the cat in the cage',
    '已完成 / DISCOVERED': 'DISCOVERED', '尚未完成 / UNDISCOVERED': 'UNDISCOVERED',
    '走完这条路线后，这里会记下结局。': 'Finish this route to record its ending here.',
    '獠牙撞击 · ': 'Tusk strikes · ',
    '撞了五下。你抬起头，灯光后面好像有一对獠牙。': 'Five strikes. You look up. Are those tusks behind the lights?',
    '咔嚓。奇怪的味道在嘴里散开。': 'Crunch. A strange taste fills your mouth.',
    '它挡住了你。换一个方向，再试一次。': 'It blocks your way. Try the other side.',
    '对手已退下': 'It has moved aside', '还需 ': 'Pushes left: ', ' 次': '',
    '它让开了。你又抢到一粒粮。': 'It moves aside. You snatch another grain.',
    '抢到一粒。换个方向，再挤过去。': 'One grain. Switch sides and push again.',
    '前面的鸭子退开了。你护住刚抢到的六粒粮。': 'The ducks give way. You guard your six grains.',
    '再注视一会儿。巨神身旁的白雾还没有散尽。': 'Keep watching. Mist still hangs around the great god.',
    '巨神正在喷出白雾 · ': 'The great god vents white mist · ',
    '巨神喷出的白雾散开了。林间仍回荡着轰鸣。': 'The mist clears. The roar still echoes through the trees.',
    '切换资料': 'Choose a fact card', '切换角色手记': 'Choose a character journal',
    '继续故事': 'Continue the story',
    '图片暂时没加载出来': 'This image could not load',
    '请检查网络连接。你也可以用下方按钮继续。': 'Check your connection, or use the button below to continue.',
}


def localize_script(script):
    def replace(match):
        token = match.group()
        # The shared Chinese UI literals contain no escaped quote characters.
        value = token[1:-1]
        if value not in SCRIPT_TEXT:
            return token
        return json.dumps(SCRIPT_TEXT[value], ensure_ascii=False)
    script = re.sub(r"'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"", replace, script)
    script = script.replace("'use strict';", "'use strict';\n  document.documentElement.lang='en';", 1)
    script = script.replace(r'/[^。！？；\n]+[。！？；]?|[。！？；\n]/g',
                            r'/[^.!?;\n]+[.!?;]?|[.!?;\n]/g')
    return script


def localize_styles(css):
    return css.replace('点击画面继续 ↗', 'Click the image to continue ↗').replace(
        '点击画面 · 听听它的声音 ♫', 'Click the image to hear its call ♫').replace(
        '[data-card-label="猫"]', '[data-card-label="Cat"]')
