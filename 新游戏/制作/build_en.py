"""Build the English edition with Python and Pillow: python build_en.py."""
from pathlib import Path
import html
import json
import re
from functools import lru_cache
from urllib.parse import quote
from PIL import Image, ImageOps
from english_ui import localize_script, localize_styles
from story_expansion import extend_story

PROJECT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
TITLE = 'They Once Existed · A Gift from the Gods'
IFID = 'E56E5DA0-D65C-4D6B-A694-3B425A69C42A'
ASSET_BASE = 'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/'
css = localize_styles((HERE / 'game.css').read_text(encoding='utf-8')) + '\n' + (HERE / 'game-en.css').read_text(encoding='utf-8')
script = localize_script((HERE / 'game.js').read_text(encoding='utf-8'))
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
    return '<div class="memory"><span>You remember</span>' + text + '</div>'


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
    return '<span class="cycle-word word-slot" title="Click to change the wording"><span class="word-measure" aria-hidden="true">' + max(versions, key=len) + '</span><span class="word-value">(cycling-link: ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in versions) + ')</span></span>'


def reveal_word(label, answer):
    return '<span class="reveal-word word-slot" title="Click to look closer"><span class="word-measure" aria-hidden="true">' + max((label, answer), key=len) + '</span><span class="word-value">(link: ' + json.dumps(label, ensure_ascii=False) + ')[(transition: "dissolve")+(transition-time: .55s)[' + answer + ']]</span></span>'


def changing_word(hook, *versions):
    values = ', '.join(json.dumps(value, ensure_ascii=False) for value in versions)
    return '<span class="changing-word word-slot"><span class="word-measure" aria-hidden="true">' + max(versions, key=len) + '</span><span class="word-value">|' + hook + '>[' + versions[0] + ']</span></span>(set: _wordStep to 1)(live: 2.4s)[(set: _wordStep to _wordStep + 1)(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .65s)[(print: (nth: _wordStep, ' + values + '))]](if: _wordStep >= ' + str(len(versions)) + ')[(stop:)]]'


def typed_voice(text):
    plain = text.replace('<br>', '\n')
    count = str(len(plain))
    return '(set: _inkText to ' + json.dumps(plain, ensure_ascii=False) + ')(set: _inkCount to 1)|spokenLine>[<span class="typewriter-line" title="Click to read the whole line"><span class="typewriter-measure" aria-hidden="true">' + text + '</span><span class="typewriter-ink" aria-hidden="true">|typedVoice>[(print: (substring: _inkText, 1, _inkCount))]|typedCursor>[<span class="typewriter-caret">▏</span>](live: 45ms)[(set: _inkCount to (min: _inkCount + 1, ' + count + '))(replace: ?typedVoice)[(print: (substring: _inkText, 1, _inkCount))](if: _inkCount >= ' + count + ')[(replace: ?typedCursor)[](stop:)]]</span><span class="sr-only">' + text + '</span></span>](click: ?spokenLine)[(set: _inkCount to ' + count + ')(replace: ?typedVoice)[(print: _inkText)](replace: ?typedCursor)[]]'


def whisper(hook, label, lines, mode='listen'):
    """Native Harlowe changes stay inside a reserved two-line text slot."""
    text = '<div class="story-whisper" data-whisper="' + hook + '"><span class="whisper-label">' + label + '</span><span class="whisper-copy">|' + hook + '>[' + lines[0] + ']</span>'
    if mode == 'listen':
        text += '<span class="whisper-action">(set: _echo to 1)(link-rerun: "Listen again ↻")[(set: _echo to _echo + 1)(if: _echo > ' + str(len(lines)) + ')[(set: _echo to 1)](replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .4s)[(print: (nth: _echo, ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in lines) + '))]]]</span>'
    elif mode == 'after':
        text += '(after: 1.6s)[(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .8s)[' + lines[-1] + ']]]'
    else:
        text += '(set: _echo to 1)(live: 1.2s)[(set: _echo to _echo + 1)(replace: ?' + hook + ')[(transition: "dissolve")+(transition-time: .6s)[(print: (nth: _echo, ' + ', '.join(json.dumps(value, ensure_ascii=False) for value in lines) + '))]](if: _echo >= ' + str(len(lines)) + ')[(stop:)]]'
    return text + '</div>'


def enrich_scene(name, body):
    replacements = {
        'Boar-Forest': ('Not thunder', cycling('Not thunder', 'Not the wind either', 'Never heard that before')),
        'Boar-Lights': ('blinding yellow light', styled('blinding yellow light')),
        'Boar-God': ('the wild pig god', styled('the wild pig god', 'outline')),
        'Cat-Label': ('Healthy and lively', '|health>[Healthy and lively]'),
        'Cat-Food': ('a little strange', cycling('a little strange', 'a little bitter', "as if something's been mixed in")),
        'Cat-Color': ('the world has turned to color', '(text-colour: "#666666")[' + styled('the world has turned to color') + ']'),
        'Cat-Home': ('your head grows heavier', styled('your head grows heavier', 'blur')),
        'Cat-Priest': ('it won’t hurt anymore', styled('it won’t hurt anymore', 'fade-in-out')),
        'Duck-Pen': ('a ring of light', styled('a ring of light', 'outline')),
        'Duck-Heaven': ('chosen', cycling('chosen', 'weighed', 'taken away')),
        'Duck-Scale': ('your weight', cycling('your weight', 'your selling price', 'how much meat you carry')),
        'Duck-Priest': ('the Creator', styled('the Creator', 'shadow')),
    }
    if name in replacements:
        old, new = replacements[name]
        body = body.replace(old, new, 1)
    clues = {
        'Boar-Machine': ('There is no fur on its dark, hard shell.', changing_word('ironSkin', 'There is no fur on its dark, hard shell.', 'Its shell never rises or falls with a breath.', 'Something inside keeps roaring. It never stops.')),
        'Boar-Lights': ('an odd smell', reveal_word('an odd smell', 'the smell of rust and engine oil')),
        'Boar-Path': ('Hoofprints turn onto a path to the north.', reveal_word('Hoofprints turn onto a path to the north.', 'The path is still clear. It leads back into the woods.')),
        'Boar-Smell': ('Only rust, engine oil, and sap from torn bark.', reveal_word('Only rust, engine oil, and sap from torn bark.', 'Broken branches mingle with the smell of machinery.')),
        'Boar-God': ('Behind the lights are tusks just like yours.', changing_word('godShape', 'Behind the lights are tusks just like yours.', 'Those tusks are taller than you.', "You have mistaken the machine's steel arms for tusks.")),
        'Boar-Leave': ('There is still fruit by the stream', reveal_word('There is still fruit by the stream', 'The fruit tree you remember is still there')),
        'Boar-Stay': ('You follow the great god, taking its chips and stumps for gifts.', changing_word('falseGift', 'You follow the great god, taking its chips and stumps for gifts.', 'Wood chips and stumps are all the great god leaves behind.', 'You try a bite. Your mouth fills with splinters.')),
        'Cat-Cage': ('Several gray cats are packed together.', changing_word('cageNames', 'Several gray cats are packed together.', 'You are wedged in the middle, barely able to turn.', 'Whenever the door opens, every cat looks up.')),
        'Cat-Aisle': ('Rows of identical cages line the aisle.', reveal_word('Rows of identical cages line the aisle.', 'Every cat in every cage is watching the door.')),
        'Cat-Pills': ('a few hard pieces', reveal_word('a few hard pieces', 'pills mixed into the food')),
        'Cat-Bowl': ('The bowl hits the bars with a clink.', reveal_word('The bowl hits the bars with a clink.', 'The sound carries down the aisle. Nobody stops.')),
        'Cat-Color': ('The bars turn pink', changing_word('sweetBars', 'The bars turn pink', 'The floor starts swaying', 'You can barely keep your balance')),
        'Cat-Window': ('“They said you were healthy…”', reveal_word('“They said you were healthy…”', '“We need a vet. Right now.”')),
        'Cat-Recover': ('At home, you walk out of the carrier and climb slowly onto the sofa.', reveal_word('At home, you walk out of the carrier and climb slowly onto the sofa.', "You climb onto the sofa. This time, your back legs don't give way.")),
        'Cat-Depart': ('When your person comes home, the bed by the window is empty.', reveal_word('When your person comes home, the bed by the window is empty.', 'They leave your bed where it was, by the window.')),
        'Duck-Pen': ('It’s a gift from God', reveal_word('It’s a gift from God', "Once you're full, you can leave the mud")),
        'Duck-Help': ('You brace against the crowd and make a little room.', reveal_word('You brace against the crowd and make a little room.', 'You hold the others back until the duck pulls its wing free.')),
        'Duck-Grain': ('You guard your food and count it. Just six grains.', reveal_word('You guard your food and count it. Just six grains.', 'All that shoving, and you only got six grains.')),
        'Duck-Eat': ('The hand reaches toward you.', changing_word('choosingHand', 'The hand reaches toward you.', 'The person who scattered the grain crouches down.', 'They glance at you, then reach for your wings.')),
        'Duck-Share': ('It eats them in seconds', reveal_word('It eats them in seconds', "It hasn't eaten all day")),
    }
    if name in clues:
        old, new = clues[name]
        body = body.replace(old, new, 1)
    extras = {
        'Boar-Forest': ('forestEcho', 'Listen a little longer', ['The ground shakes again. Birds scatter from the trees.', 'The noise gets closer. Branches snap beneath it.', 'You take two steps toward the clearing and prick up your ears.'], 'listen'),
        'Boar-Smell': ('ironBreath', 'Up close', ['Hot air hits your nose. You sneeze.', "Something this big, and not a trace of an animal's scent.", 'The earth is churned up wherever it passes.'], 'listen'),
        'Boar-Mist': ('godReply', 'Through the mist', ['White mist from the great god drifts over your head.', 'You stand still, waiting for it to do something else.', 'The mist clears. The great god lurches forward again.'], 'live'),
        'Cat-Cage': ('cageEcho', 'At the door', ['Footsteps sound at the end of the aisle.', 'Keys jangle. You lift your head at once.'], 'after'),
        'Cat-Visitor': ('homePromise', 'A home you have never seen', ['Is a sofa somewhere you can stretch out and sleep?', 'It must be warm in there with the lamp on.', "If the bed is soft, I'd like to sleep until tomorrow."], 'listen'),
        'Cat-Farewell': ('lastVoice', 'By the bed', ['Someone is still holding your front paw.', 'You want to nuzzle their hand. You have no strength left.', '“I’m here. Don’t be scared.”'], 'live'),
        'Duck-Crowd': ('crowdEcho', 'Behind you', ['“Move up! There’s nothing left back here.”', 'A foot lands on your tail feathers. You hurry aside.', 'The crowd surges again. Nobody will step back.'], 'listen'),
        'Duck-Scale': ('scaleReply', 'On the scale', ['You shift your feet. The needle wobbles.', 'A hand holds you still. Someone checks the dial again.', '“This one’s about right.”'], 'live'),
        'Duck-Priest': ('outsideScreen', 'It looks at you', ['The priest turns toward the person beyond the screen.', 'It waits. You have to choose an answer.'], 'after'),
    }
    if name in extras:
        addition = whisper(*extras[name])
        index = body.find('<div class="actions')
        body = body[:index] + addition + body[index:] if index >= 0 else body + addition
    if name == 'Cat-Label':
        body += '(after: .9s)[(enchant: ?health, (text-style: "strike")+(text-colour: "#777777"))]'
    if name == 'Cat-Window':
        body += '<p class="thought macro-line">(seq-link: "Your carrier is still by the door.", "The paper marked ‘Healthy’ lies beside it.", "They photograph the label and pick up the phone.")</p>'
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


def scene(name, role, number, chapter, path, alt, body, next_to=None, next_label='Continue →', sound='', extra='', ending='', classes='', progress=0, advance=True):
    body = enrich_scene(name, body)
    role_label = {'pig': 'WILD PIG / FOREST', 'cat': 'CAT / HOME', 'duck': 'DUCK / ALTAR'}[role]
    inner = '<div class="chapter"><span class="number">' + number + '</span><span>' + chapter + '</span><span class="track"></span><small>' + role_label + '</small></div>'
    inner += image(path, alt, bool(next_to and advance))
    inner += '<div class="scene-panel"><div class="scene-copy">' + body + (actions((next_label, next_to)) if next_to else '') + '</div>' + extra + '</div>'
    inner += '<div class="chapter-meter" aria-hidden="true"><span style="width:' + str(progress) + '%"></span></div>'
    effects = {'Boar-Forest': 'forest', 'Boar-Machine': 'machine', 'Boar-Approach': 'machine', 'Boar-Lights': 'light', 'Boar-God': 'revelation', 'Boar-Mist': 'steam', 'Cat-Color': 'colour', 'Cat-Visitor': 'warmth', 'Cat-Home': 'warmth', 'Cat-Wake': 'warmth', 'Cat-Farewell': 'farewell', 'Duck-Pen': 'halo', 'Duck-Heaven': 'halo', 'Duck-Scale': 'scales', 'Duck-Priest': 'altar'}
    attrs = ' data-sound="' + ('themeEnd' if ending else sound) + '"' + (' data-ending="' + ending + '"' if ending else '') + (' data-fx="' + effects[name] + '"' if name in effects else '')
    reset = {'Boar-Forest': '(set: $pigTrail to false)(set: $pigOil to false)', 'Cat-Cage': '(set: $catTag to false)', 'Duck-Pen': '(set: $duckHelp to false)(set: $duckShare to false)'}.get(name, '')
    add(name, reset + '<section data-scene="' + name + '" class="page scene-stage role-' + role + ' ' + classes + '"' + attrs + '>' + inner + '</section>')


def task(kind, action_label, status, next_label, target, goal=1, hint=''):
    return '<div class="interaction" data-task="' + kind + '" data-goal="' + str(goal) + '"><p class="instructions">' + hint + '</p><button type="button" class="' + ('hold-button' if kind == 'hold' else 'action-button') + '" data-task-action>' + action_label + '</button><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">' + status + '</p><div class="actions is-locked" data-task-next>' + link(next_label, target) + '</div></div>'


def ending_tail():
    return actions(('Play again ↻', {'pig': 'Boar-Forest', 'cat': 'Cat-Cage', 'duck': 'Duck-Pen'}[ending_role]), ('Choose another ↗', 'Choose a Character'), ('View the journal', 'Journal'))


add('Initialize', '(set: $pigTrail to false)(set: $pigOil to false)(set: $catTag to false)(set: $duckHelp to false)(set: $duckShare to false)', 'startup')
add('Navigation', '<header class="mast"><span class="brand"><em>✧</em><span>THEY ONCE EXISTED</span><span class="series-label"> / A Gift from the Gods</span></span><nav aria-label="Game navigation"><button type="button" class="audio-toggle" data-audio-toggle aria-pressed="true">Sound: on</button>' + link('Home', 'Start') + link('Cast', 'Choose a Character') + link('Journal <span class="journal-number" data-journal-total>0/6</span>', 'Journal') + '</nav></header>', 'header')

title_portals = ''
for key, number, label, animal, path, line in [
    ('pig', 'I', 'FOREST', 'Wild Pig', '素材/选角/野猪.jpg', '“How can it bite right through a tree?”'),
    ('cat', 'II', 'HOME', 'Cat', '素材/选角/猫.jpg', '“Is this really my home now?”'),
    ('duck', 'III', 'ALTAR', 'Duck', '素材/选角/鸭子.jpg', '“Do the chosen ones really go to heaven?”'),
]:
    title_portals += '<button type="button" class="title-portal portal-' + key + '" data-animal="' + key + '" data-title-line="' + line + '" aria-label="Play the ' + animal + ' call"><span class="portal-number">' + number + '</span><span class="portal-halo" aria-hidden="true"></span><img src="' + asset_url(silhouette(path)) + '" alt="' + animal + ' silhouette" width="240" height="200"><span class="portal-caption"><strong>' + animal + '</strong><small>' + label + '</small></span></button>'
title_art = '<div class="title-visual"><div class="title-orbit" aria-hidden="true"><div class="orbit-ring ring-outer"></div><div class="orbit-ring ring-inner"></div><div class="orbit-cross"></div><span class="orbit-star star-north">✦</span><span class="orbit-star star-south">✧</span></div><div class="title-portals">' + title_portals + '</div><p class="title-scene-caption" data-title-caption>“Is that really a god?”</p></div>'
title_copy = '<div class="title-copy"><div class="title-heading"><p class="title-overline">AN INTERACTIVE FABLE</p><h1 class="title-wordmark"><span>They Once</span><span>Existed<span class="title-mark" aria-hidden="true">✦</span></span></h1><p class="title-english">THREE LIVES. SIX ENDINGS.</p><h2 class="title-subtitle">A Gift from the Gods</h2><p class="title-invitation">A forest. A cage. A fence.<br>See what happens through their eyes.</p></div><div class="title-controls">' + actions(('Begin <span aria-hidden="true">↗</span>', 'Choose a Character'), ('Journal', 'Journal')) + '<button type="button" class="title-listen" data-start-listening><span class="title-equalizer" aria-hidden="true"><i></i><i></i><i></i><i></i></span><span data-title-audio-status>Click to turn on the music</span></button></div></div>'
add('Start', '<section data-scene="Start" class="page title-screen" data-sound="themeOpen"><canvas class="title-dust" aria-hidden="true"></canvas><div class="title-light" aria-hidden="true"></div><div class="title-main">' + title_copy + title_art + '</div><footer class="title-footer"><span>Three stories · Six endings</span><span>Click an animal to hear its call</span><span class="title-edition">A GIFT FROM THE GODS / CHAPTER II</span></footer></section>')

roles = [
    ('pig', '01 / THE FOREST', 'Wild Pig', 'Something huge has come to the forest.<br>You have never seen an animal like it.', '素材/选角/野猪.jpg', 'Boar-Forest'),
    ('cat', '02 / THE HOME', 'Cat', 'Someone says they will take you home.<br>You have waited in this cage for so long.', '素材/选角/猫.jpg', 'Cat-Cage'),
    ('duck', '03 / THE ALTAR', 'Duck', 'The ducks fight for grain from a god.<br>They say a full belly leads to heaven.', '素材/选角/鸭子.jpg', 'Duck-Pen'),
]
cards = ''
for key, label, animal, desc, path, target in roles:
    cards += '<article class="role-card"><span class="role-count" data-role-count="' + key + '">0/2</span><button type="button" class="animal-preview" data-animal="' + key + '" aria-label="Play the ' + animal + ' call"><img src="' + asset_url(path) + '" alt="' + animal + ' silhouette"><span class="sound-hint">Click to hear its call ♫</span></button><div class="role-copy"><div class="role-no">' + label + '</div><h2>' + animal + '</h2><p>' + desc + '</p><div class="role-enter">' + link('Begin this story <span>↗</span>', target) + '</div></div></article>'
add('Choose a Character', '<section data-scene="Choose a Character" class="page selection" data-sound="themeOpen"><div class="eyebrow">PROLOGUE</div><div class="selection-head"><h1>Through Their Eyes</h1><p>Choose a character and see what happens next.</p></div><img class="selection-art" src="' + asset_url(silhouette('素材/选角/它们.jpg')) + '" alt="Silhouettes of a wild pig, a cat, and a duck"><div class="role-grid">' + cards + '</div><footer class="selection-foot"><span>Three stories · Two endings each · Underlined words are interactive</span><span class="series">They Once Existed / A Gift from the Gods</span></footer></section>')

# 野猪：保留观察支线，结尾只保留离开与留下。
scene('Boar-Forest', 'pig', '01', 'A noise beyond the trees', '新/1在森林.jpg', "A blue forest seen from a wild pig's point of view",
      '<h1>What is that noise?</h1>' + para('“Not thunder. Why is the ground shaking?”', 'voice') + para('You stop and turn toward the sound.', 'thought'), 'Boar-Machine', 'Go to the clearing →', 'pigOpen', progress=8)
scene('Boar-Machine', 'pig', '01', 'A noise beyond the trees', '新/2看见伐木机.jpg', 'A dark logging machine appears beyond the trees',
      para('Something enormous moves slowly across the clearing.<br>There is no fur on its dark, hard shell.') + para('“It’s huge… What does it eat?”', 'voice') + choices(('Move closer', 'Get a better look at this creature.', 'Boar-Approach'), ('Follow the forest edge', 'See if there is a way around.', 'Boar-Path')), sound='pigOpen', progress=16)
scene('Boar-Path', 'pig', '01', 'The path at the edge', '新/1在森林.jpg', 'A path through the forest that the machine has not flattened',
      '(set: $pigTrail to true)' + para('You skirt the clearing.<br>Hoofprints turn onto a path to the north.') + para('“I can still get through here. I’ll remember it for the way back.”', 'voice') + memory('A northern path begins beside an old tree.'), 'Boar-Approach', 'Go back to the huge creature →', 'pigOpen', progress=22)
scene('Boar-Approach', 'pig', '02', 'The roar inside the shell', '新/3伐木机靠近.jpg', 'The wheels and steel body of the logging machine draw closer',
      para('It touches a tree. The trunk shakes, then snaps.<br>Branches vanish inside. Wood chips rain down.') + para('“It bit right through that tree…”', 'voice'), 'Boar-Lights', 'A little closer →', 'pigOpen', progress=25)
scene('Boar-Lights', 'pig', '02', 'Blinding lights', '新/4机器发光.jpg', 'The machine shines bright yellow lights from the forest edge',
      para('The creature stops. Two beams of blinding yellow light hit your face.<br>The wind carries an odd smell. You have never smelled it before.') + para('“What are you staring at? This is my forest.”', 'voice') + choices(('Bare your tusks', 'It cannot be allowed any farther.', 'Boar-Charge'), ('Sniff the air first', 'Something about its smell is wrong.', 'Boar-Smell')), sound='pigOpen', progress=34)
scene('Boar-Smell', 'pig', '02', 'An unfamiliar smell', '新/3伐木机靠近.jpg', "Dark gaps between the machine's wheels",
      '(set: $pigOil to true)' + para('You sniff again. No fur. No blood.<br>Only rust, engine oil, and sap from torn bark.') + para('“It keeps roaring. Doesn’t it need to breathe?”', 'voice') + memory('It has no animal scent. Its shell never moves with a breath.'), 'Boar-Charge', 'Try your tusks →', 'pigOpen', progress=40)
scene('Boar-Charge', 'pig', '03', 'Charge', '新/5野猪靠近.jpg', 'A wild pig raises its tusks toward the glowing machine',
      para('“Get out! Leave these trees alone!”', 'voice') + para('You lower your head and drive your tusks into its shell.', 'thought'), sound='pigInteract',
      extra=task('ram', 'Ram the machine', 'Tusk strikes · 0 / 5', 'Look up →', 'Boar-God', 5, 'Strike five times. Try to drive it out of the forest.'), progress=45)
scene('Boar-God', 'pig', '04', 'The god you recognize', '新/6机器变野猪.jpg', 'In the eyes of the wild pig, the machine becomes a god with enormous tusks',
      para('On the fifth strike, your tusks ring with pain. You look up.<br>Behind the lights are tusks just like yours.') + para('“So it’s the wild pig god… No wonder I couldn’t move it.”', 'voice'), 'Boar-Mist', 'Gaze up at it →', 'pigWorship', progress=57)
scene('Boar-Mist', 'pig', '04', 'The great god breathes', '新/7野猪喷气.jpg', 'The mechanical god vents white mist above the small blue wild pig',
      para('White mist bursts from the great god.<br>You duck, then find yourself looking up again.', 'voice'), sound='pigWorship',
      extra=task('hold', 'Hold · Watch the great god vent', 'Hold the button to watch the mist from the great god.', 'Wait for the mist to clear →', 'Boar-Choice', hint='Hold for about two seconds to watch the great god vent.'), progress=70)
scene('Boar-Choice', 'pig', '05', 'Leave or stay', '新/野猪说话.jpg', 'A wild pig stands before the silent steel god',
      '<h1>Will you stay here?</h1>' + para('“It’s so powerful. Surely I won’t go hungry if I follow it?”', 'voice') + para('Another tree falls behind you. You look back at the woods.') + '(if: $pigOil)[' + memory('But it never breathes. You still cannot explain that.') + '](if: $pigTrail)[' + memory('The northern path is still there, beside the old tree.') + ']' + choices(('Leave · Return to the forest', 'Find the stream and fruit you know.', 'Boar-Leave'), ('Stay · Follow the great god', 'A god this powerful will look after you. Surely.', 'Boar-Stay')), sound='pigWorship', progress=84)
ending_role = 'pig'
scene('Boar-Leave', 'pig', '06', 'Ending A · Leave', '新/1在森林.jpg', 'The wild pig turns back into the deep blue forest',
      '<div class="ending-label">ENDING 01 / LEAVE</div><h1>Back to the Woods</h1>' + para('You take one last look at the great god, then slip into the trees.<br>Even far away, you can still hear its roar.') + '(if: $pigTrail)[' + para('You follow the northern path around the clearing and stop by the stream.') + '](else:)[' + para('You follow familiar scents until you find the stream.') + ']' + para('There is still fruit by the stream. You drink and eat until the hunger eases.') + para('You can sleep here tonight.', 'closing') + ending_tail(), sound='pigLive', ending='pig-live', classes='ending', progress=100)
scene('Boar-Stay', 'pig', '06', 'Ending B · Stay', '新/2看见伐木机.jpg', 'The forest loses its color while the logging machine keeps working',
      '<div class="ending-label">ENDING 02 / STAY</div><h1>It Never Looked Back</h1>' + para('You follow the great god, taking its chips and stumps for gifts.<br>You cannot eat them. You keep waiting.') + para('Days later, the machine leaves. The shade is gone. Mud blocks the stream.<br>Too hungry to stand, you stare after it.') + para('It never comes back.', 'closing') + ending_tail(), sound='pigFall', ending='pig-fall', classes='ending ending-pig-fall', progress=100)

# 猫：保留笼外观察、食物与窗边支线；前往为康复，放弃为告别。
scene('Cat-Cage', 'cat', '01', 'Days in a cage', '猫/1.jpg', 'Gray cats crowded behind cold iron bars',
      '<h1>Will someone come today?</h1>' + para('The iron bars are cold.<br>Several gray cats are packed together.') + para('“Is it warmer outside?”', 'voice') + choices(('Look toward the door', 'Someone is coming this way.', 'Cat-Visitor'), ('Peer through the bars', 'Try to see what lies outside the cage.', 'Cat-Aisle')), sound='catOpen', progress=8)
scene('Cat-Aisle', 'cat', '01', 'Beyond the bars', '猫/1.jpg', 'A cat looks out at the aisle through iron bars',
      para('You press close. Rows of identical cages line the aisle.<br>The windows are high. Only the top cages catch the sun.') + para('“If I grew a little taller, could I reach the sunshine?”', 'voice'), 'Cat-Visitor', 'Someone is at the door →', 'catOpen', progress=14)
scene('Cat-Visitor', 'cat', '02', 'Someone wants to take you home', '猫/2.jpg', 'A warm room with a sofa, a floor lamp, and a cat bed, imagined by the cat',
      para('“What a sweet cat. Come home with me. Your bed’s all ready.”', 'voice') + para('You do not understand every word, but the voice is gentle.<br>You squeeze forward and press your cheek to the bars.') + choices(('Nuzzle the hand', 'It has been so long since anyone stroked you.', 'Cat-Food'), ('Look at the cage label', 'Someone beside you is changing the paper.', 'Cat-Label')), sound='catOpen', progress=18)
scene('Cat-Label', 'cat', '02', 'A fresh label', '猫/1.jpg', 'Iron bars separate a cat from the people outside',
      '(set: $catTag to true)' + para('The old label is torn off. The new one reads “Healthy and lively.”<br>The old paper is crumpled and tossed into a box.') + para('“Nothing wrong with this one. Such a good appetite.”', 'voice') + memory('You could not eat last night. Today, they call you healthy.'), 'Cat-Food', 'A bowl slides into the cage →', 'catOpen', progress=24)
scene('Cat-Food', 'cat', '03', 'Dinner arrives', '猫/3.jpg', 'A pale purple food bowl against a white background',
      para('“Food at last. But it smells a little strange.”', 'voice') + para('Your stomach growls. You have been hungry for so long.', 'thought') + choices(('Have a little', 'Fill your stomach first.', 'Cat-Chew'), ('Sniff it closely', 'There is something bitter in the food.', 'Cat-Pills')), sound='catInteract', progress=28)
scene('Cat-Pills', 'cat', '03', 'Something in the food', '猫/4.jpg', 'Capsules in the bowl stand out from the food around them',
      para('You paw the food aside and find a few hard pieces.<br>Up close, the bitter smell is stronger.') + para('“Am I meant to eat these?”', 'voice') + choices(('Eat a little anyway', 'You are far too hungry.', 'Cat-Chew'), ('Push the bowl away', 'You do not like the smell.', 'Cat-Bowl')), sound='catInteract', progress=33)
scene('Cat-Bowl', 'cat', '03', 'Pushing it away', '猫/4.jpg', 'A cat pushes a bowl of food and pills toward the cage door',
      para('You push the bowl to the door. The bowl hits the bars with a clink.<br>The person outside glances down and pushes it back.') + para('“Go on, eat. Then we’ll take you home.”', 'voice') + choices(('Lower your head and eat', 'You keep thinking about the bed they promised.', 'Cat-Chew')), sound='catInteract', progress=37)
scene('Cat-Chew', 'cat', '03', 'Bitter', '猫/4.jpg', 'A capsule marked Stimulant lies among the food',
      para('“Just one bite.”', 'voice'), sound='catInteract', extra=task('chew', 'Try to chew', 'Bite down, then swallow.', 'Swallow →', 'Cat-Color', hint='Something hard in the food catches against your teeth.'), progress=38)
scene('Cat-Color', 'cat', '04', 'A cage full of color', '猫/5.jpg', 'The gray cage becomes patches of soft pink, blue, and green',
      para('“Oh, the world has turned to color.”', 'voice') + para('The bars turn pink. Your body feels light.<br>You try to stand and almost bump into the cage door.', 'thought'), 'Cat-Home', 'Someone lifts you up →', 'catDream', classes='is-colour-scene', progress=48)
scene('Cat-Home', 'cat', '05', 'Home at last', '猫/6.jpg', 'A softly lit room with a rug, plants, a sofa, and a picture of a cat',
      '<h1>Is this home?</h1>' + para('“The sofa’s so soft. Can I really sleep here?”', 'voice') + '<p class="thought">(link: "Try the sofa")[You knead twice. Your paws sink into the cushions.] · (link: "Look at the picture")[There is a cat in it too. You watch it for a while.]</p>' + '(if: $catTag)[' + memory('The label said “Healthy and lively.” Now you can barely lift your tail.') + ']' + para('Before long, your head grows heavier, and your whole body feels too hot.', 'thought') + choices(('Lie down and rest', 'Maybe the journey has just worn you out.', 'Cat-Priest'), ('Go to the window', 'It looks cooler over there.', 'Cat-Window')), sound='catDream', progress=61)
scene('Cat-Window', 'cat', '05', 'The jump you cannot make', '猫/6.jpg', 'Hazy light falls through the window of a warm room',
      para('You try to jump onto the sill. Your back legs buckle.<br>You fall to the rug. Your person scoops you up.') + para('“They said you were healthy…”', 'voice') + para('A palm rests on your forehead. Someone starts looking for a phone.', 'thought'), 'Cat-Priest', 'The room blurs →', 'catDream', progress=70)
scene('Cat-Priest', 'cat', '06', 'Half asleep', '猫/7祭司说话猫.jpg', 'A cat priest wearing bone ornaments and carrying a cross stands before you',
      para('You lie dazed and heavy. A tall shadow appears before you.') + para('“Come with me. Over there, it won’t hurt anymore.”', 'voice') + para('There is a door behind the shadow. But someone beside you keeps calling:<br>“Wake up. We’re at the vet now.”', 'thought') + choices(('Go back · Follow the voices', 'You still want to go home.', 'Cat-Wake'), ('Let go · I’m too tired', 'The voices beside you are fading.', 'Cat-Farewell')), sound='catPriest', progress=78)
scene('Cat-Wake', 'cat', '07', 'Choice A · Go back', '猫/2.jpg', 'Warm yellow light reveals the shape of the room',
      '<h1>You move a paw</h1>' + para('“A movement! Doctor, did you see that?”', 'voice') + para('You struggle to open your eyes. The air smells of disinfectant.<br>Your person is still there, still wearing their coat.') + para('You spend the next few days at the hospital, getting treatment.', 'thought'), 'Cat-Recover', 'A few days later →', 'catDream', progress=90)
scene('Cat-Farewell', 'cat', '07', 'Choice B · Let go', '猫/7祭司说话猫.jpg', 'The cat closes its eyes as the priest fades into the dark',
      para('“I want to sleep a little longer.”', 'voice') + para('You walk toward the shadow. It slowly opens the door.<br>Your person calls again. You no longer hear them.') + para('The vet keeps trying. The monitor beeps more slowly.', 'thought'), 'Cat-Depart', 'Afterward →', 'catEnd', classes='ending ending-cat-dark', progress=90)
ending_role = 'cat'
scene('Cat-Recover', 'cat', '08', 'Ending A · Go back', '猫/6.jpg', 'After treatment, the cat returns to its home with a sofa and a bed',
      '<div class="ending-label">ENDING 03 / GO BACK</div><h1>Your Bed Is Still There</h1>' + para('Once you are stable, your person comes to take you home.<br>At home, you walk out of the carrier and climb slowly onto the sofa.') + para('The food bowl has moved. Fresh water sits beside it.<br>You eat a little and curl up in the bed by the window.') + para('Later in the story: they keep the vet records and receipt, and report the seller.', 'ending-note') + para('This time, you can sleep soundly.', 'closing') + ending_tail(), sound='catDream', ending='cat-light', classes='ending', progress=100)
scene('Cat-Depart', 'cat', '08', 'Ending B · Let go', '猫/8.jpg', 'A news screen within the story shows an investigation into a cat-selling scam',
      '<div class="ending-label">ENDING 04 / LET GO</div><h1>Not Long Enough at Home</h1>' + para('The vet cannot save you. You spent less than a day in your new home.<br>When your person comes home, the bed by the window is empty.') + para('Later in the story: they report the seller, keeping the vet records as evidence.<br>An investigation begins into the drugs used to sell sick cats as healthy ones.', 'ending-note') + para('A few of your hairs still cling to the sofa.', 'closing') + ending_tail(), sound='catEnd', ending='cat-sleep', classes='ending', progress=100)

# 鸭子：保留让路、分粮的中间分支，最后只回答是或否。
scene('Duck-Pen', 'duck', '01', 'Inside the fence', '鸭/鸭1.jpg', 'A duck with a halo stands in a vividly colored muddy pen',
      '<h1>Is this all there is?</h1>' + para('You have lived in this mud all your life. The fence is high. The water is dirty.<br>Every duck has a ring of light above its head.') + para('“It’s a gift from God.” That’s what everyone says.', 'voice'), 'Duck-Crowd', 'The crowd suddenly surges →', 'duckOpen', progress=10)
scene('Duck-Crowd', 'duck', '02', 'Feeding time', '鸭/鸭2.jpg', 'A crowd of colorful ducks pushes forward',
      para('“Why is everyone pushing? What’s happening?”', 'voice') + para('“God’s here! More food today!”'), 'Duck-Heaven', 'Follow the crowd →', 'duckOpen', progress=23)
scene('Duck-Heaven', 'duck', '02', 'The heaven they talk about', '鸭/鸭3.jpg', 'Ducks gather around a towering human figure as if worshipping a god',
      para('“Eat up. Only the strong get chosen.”', 'voice') + para('They say the chosen ducks leave for a heaven without mud.<br>Not one of them has ever come back.', 'thought') + choices(('Push forward for food', 'Wait any longer and there will be none left.', 'Duck-Scramble'), ('Help the fallen duck first', 'It is down, one wing stuck in the mud.', 'Duck-Help')), sound='duckWorship', progress=36)
scene('Duck-Help', 'duck', '02', 'A trapped wing', '鸭/鸭2.jpg', 'One duck has fallen behind the pushing crowd',
      '(set: $duckHelp to true)' + para('You brace against the crowd and make a little room.<br>The duck pulls its wing free and struggles to its feet.') + para('“Thanks. Hurry, the food’s almost gone.”', 'voice'), 'Duck-Scramble', 'Turn back toward the food →', 'duckWorship', progress=43)
duel = '<div class="interaction" data-task="duel" data-goal="6"><p class="instructions">Click the two ducks in turn to push through for food.</p><div class="duel">'
for index, (path, alt) in enumerate([('鸭/4.jpg', 'A pink duck with wings spread'), ('鸭/4 1.jpg', 'A purple duck with wings spread')]):
    duel += '<button type="button" class="duel-target" data-task-action data-duck-target="' + str(index) + '" aria-label="Push past the ' + ('left' if index == 0 else 'right') + ' duck"><img src="' + asset_url(path) + '" alt="' + alt + '"><span class="target-label" data-target-life>3 pushes left</span></button>'
duel += '</div><div class="duel-status"><span>Grains <strong data-grains>0</strong> / 6</span><span>Make your way forward</span></div><div class="task-track" aria-hidden="true"><span></span></div><p class="task-status" data-task-status role="status" aria-live="polite">If the left side is blocked, try the right.</p><div class="actions is-locked" data-task-next>' + link('See what you got →', 'Duck-Grain') + '</div></div>'
scene('Duck-Scramble', 'duck', '03', 'Pushing through', '鸭/4.jpg', 'Ducks compete for the grain scattered by their god',
      '<h1>No food unless you fight</h1>' + para('You spread your wings and push. Something tugs at your feathers.<br>You step on something soft. There is so little grain. Nobody gives way.', 'voice'), sound='duckInteract', extra=duel, classes='task-duck', progress=50)
scene('Duck-Grain', 'duck', '03', 'Your handful of grain', '鸭/鸭2.jpg', 'The ducks settle after the scramble for food',
      '<h1>Is this really all?</h1>' + para('You guard your food and count it. Just six grains.') + '(if: $duckHelp)[' + para('The duck you helped stands beside you, empty-beaked and trembling.', 'thought') + '](else:)[' + para('A duck beside you pecks at the mud, looking for stray grains.', 'thought') + ']' + choices(('Eat it all', 'You have been hungry all day too.', 'Duck-Eat'), ('Share half', 'Let the duck beside you have some.', 'Duck-Share')), sound='duckWorship', progress=58)
scene('Duck-Eat', 'duck', '03', 'Your turn', '鸭/鸭3.jpg', 'A duck looks up at the person who scattered the grain',
      para('You gulp down the food. The hand reaches toward you.') + para('“Me? Is it really my turn?”', 'voice') + para('It grips your wings and lifts you off the ground.', 'thought'), 'Duck-Scale', 'Onto the scale →', 'duckWorship', progress=63)
scene('Duck-Share', 'duck', '03', 'Three grains', '鸭/鸭2.jpg', 'Ducks huddle together in the mud',
      '(set: $duckShare to true)' + para('You push three grains toward the other duck. It eats them in seconds.') + para('“Any more?”', 'voice') + para('You look down at your three remaining grains.<br>Before you can eat, a hand closes around your wings.'), 'Duck-Scale', 'Onto the scale →', 'duckWorship', progress=63)
scene('Duck-Scale', 'duck', '04', 'Weighing', '鸭/鸭5.jpg', 'A sacred scale holds a blue duck on one side and a heavy red offering on the other',
      '<h1>They are weighing you</h1>' + para('“What are they checking? Am I faithful enough?”', 'voice') + para('The scale rocks. The person watches the dial, interested only in your weight.') + '(if: $duckShare)[' + para('Sharing those three grains barely seems to change the needle.', 'thought') + '](else:)[' + para('The grain you fought for makes you heavier. It may get you taken away sooner.', 'thought') + ']', 'Duck-Priest', 'Lift your head →', 'duckScales', progress=72)
scene('Duck-Priest', 'duck', '05', 'The priest turns', '鸭/鸭6.jpg', 'The duck priest looks beyond the screen toward the player',
      '<h1>It is asking you</h1>' + para('“Human, do you think you are the Creator?”', 'voice') + choices(('Yes', 'Humans decide how other animals live.', 'Duck-Yes'), ('No', 'Humans are animals too, part of nature.', 'Duck-No')), sound='duckEnd', progress=83)


def fact(value, title, text, source, url):
    return '<article class="fact"><strong>' + value + '</strong><h2>' + title + '</h2><p>' + text + '</p><a href="' + url + '" target="_blank" rel="noopener noreferrer">' + source + ' ↗</a></article>'


ending_role = 'duck'
yes_facts = '<div class="facts">' + fact('$44 trillion', 'in economic value depends on nature', 'In 2020, the World Economic Forum estimated that over half of global GDP was moderately or highly dependent on nature and its services.', 'WEF · Nature Risk Rising · 2020', 'https://www.weforum.org/publications/nature-risk-rising-why-the-crisis-engulfing-nature-matters-for-business-and-the-economy/') + fact('73%', 'average decline in monitored wildlife populations', 'WWF’s Living Planet Report 2024 records a 73% average decline in monitored vertebrate population sizes between 1970 and 2020.', 'WWF · Living Planet Report · 2024', 'https://livingplanet.panda.org/') + fact('~1 million', 'animal and plant species face extinction', 'The 2019 IPBES Global Assessment estimated that around one million animal and plant species face extinction, many within decades.', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + '</div>'
no_facts = '<div class="facts">' + fact('Plastic', 'Where does it go after we throw it away?', 'Plastic entering aquatic environments harms wildlife through ingestion, entanglement, and damage to habitats.', 'UNEP · Plastic pollution', 'https://www.unep.org/plastic-pollution') + fact('Habitat', 'Animals need somewhere to live', 'Changes in land and sea use, direct exploitation, climate change, pollution, and invasive alien species are the main direct drivers of biodiversity loss.', 'IPBES · Global Assessment · 2019', 'https://www.ipbes.net/global-assessment') + fact('Every day', 'What can we do in ordinary life?', 'Use fewer disposable plastics. Avoid wildlife from unknown sources. Find out where pets come from. Keep evidence of illegal trade and report it.', 'UNEP · Act for Nature', 'https://www.unep.org/') + '</div>'
scene('Duck-Yes', 'duck', '06', 'Ending A · Yes', '鸭/鸭6.jpg', 'The duck priest silently watches the human beyond the screen',
      '<div class="ending-label">ENDING 05 / YES</div><h1>You Have a Say. Now What?</h1>' + para('“Then what will you do when these things happen?”', 'voice'), sound='duckEnd', extra=yes_facts + '<p class="facts-note">The 73% figure is an average change in monitored population sizes, not a loss of 73% of all individual animals. Dates and sources appear on the cards.</p>' + ending_tail(), ending='duck-yes', classes='ending data-ending', progress=100)
scene('Duck-No', 'duck', '06', 'Ending B · No', '鸭/鸭6.jpg', 'The duck priest asks the player one final question',
      '<div class="ending-label">ENDING 06 / NO</div><h1>They Need Somewhere to Live</h1>' + para('“But where they live, what they eat, when they are taken away—<br>aren’t humans still the ones deciding?”', 'voice'), sound='duckEnd', extra=no_facts + ending_tail(), ending='duck-no', classes='ending data-ending', progress=100)

entries = {
    'pig': [('pig-live', 'Back to the Woods', 'You leave the machine, find water and fruit, and survive in the forest.'), ('pig-fall', 'It Never Looked Back', 'You keep following the machine. Once the trees are gone, it leaves you with nothing to eat.')],
    'cat': [('cat-light', 'Your Bed Is Still There', 'You wake at the vet’s and receive treatment. When you recover, someone takes you home.'), ('cat-sleep', 'Not Long Enough at Home', 'The vet cannot save you. Your person keeps the records and reports the seller.')],
    'duck': [('duck-yes', 'You Have a Say. Now What?', 'You answer yes. The priest asks what you intend to do for these animals.'), ('duck-no', 'They Need Somewhere to Live', 'You answer no. The priest reminds you that people still decide how animals live.')],
}
journal = ''
for key, label, animal, desc, path, target in roles:
    journal += '<article class="journal-role" data-card-label="' + animal + '"><img src="' + asset_url(silhouette(path)) + '" alt="' + animal + ' silhouette"><div class="role-no">' + label + '</div><h2>' + animal + '</h2>'
    for entry_id, title, description in entries[key]:
        journal += '<div class="journal-entry" data-entry="' + entry_id + '" data-description="' + description + '"><span class="entry-state">UNDISCOVERED</span><h3>' + title + '</h3><p class="entry-copy">Finish this route to record its ending here.</p></div>'
    journal += '<div class="role-enter">' + link('Play again ↗', target) + '</div></article>'
add('Journal', '<section data-scene="Journal" class="page journal" data-sound="themeEnd"><div class="journal-head"><div class="eyebrow">ENDING RECORDS</div><h1>Journey Journal</h1><p><span data-journal-total>0/6</span> endings found · Saved in this browser</p></div><div class="journal-grid">' + journal + '</div>' + actions(('Back to the cast →', 'Choose a Character'), ('Back to the title', 'Start')) + '</section>')


extend_story(globals(), 'en')

add('Styles', css, 'stylesheet')
add('Interactions and Audio', script, 'script')
data = {'ifid': IFID, 'format': 'Harlowe', 'format-version': '3.3.9', 'start': 'Start', 'zoom': 0.7}
twee = ':: StoryTitle\n' + TITLE + '\n\n:: StoryData\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n\n'
for i, (name, body, tags) in enumerate(passages):
    twee += ':: ' + name + (' [' + tags + ']' if tags else '') + ' ' + json.dumps({'position': f'{i % 7 * 240},{i // 7 * 180}', 'size': '180,100'}) + '\n' + body + '\n\n'
(PROJECT / '新游戏-English.twee').write_text(twee.rstrip() + '\n', encoding='utf-8')
raw = []
for i, (name, body, tags) in enumerate(passages):
    if tags in ('stylesheet', 'script'):
        continue
    raw.append(f'<tw-passagedata pid="{i + 1}" name="{html.escape(name, quote=True)}" tags="{tags}" position="{i % 7 * 240},{i // 7 * 180}" size="180,100">{html.escape(body)}</tw-passagedata>')
start = next(i + 1 for i, p in enumerate(passages) if p[0] == 'Start')
story = f'<tw-storydata name="{TITLE}" startnode="{start}" creator="Twine" creator-version="2.10.0" ifid="{IFID}" format="Harlowe" format-version="3.3.9" options="" hidden><style role="stylesheet" id="twine-user-stylesheet" type="text/twine-css">{css}</style><script role="script" id="twine-user-script" type="text/twine-javascript">{script}</script>{"".join(raw)}</tw-storydata>'
template = json.loads((HERE / 'harlowe-3.3.9.json').read_text(encoding='utf-8'))['source']
output = template.replace('{{STORY_NAME}}', TITLE).replace('{{STORY_DATA}}', story)
output = re.sub(r'<html(?:\s[^>]*)?>', '<html lang="en">', output, count=1)
if 'name="viewport"' not in output:
    output = output.replace('</head>', '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"></head>')
(PROJECT / '新游戏-English.html').write_text(output, encoding='utf-8')
(PROJECT / 'They Once Existed A Gift from the Gods.html').write_text(output, encoding='utf-8')
print('Built', len(raw), 'passages;', len(output.encode('utf-8')), 'bytes; Twine/Harlowe 3.3.9')
