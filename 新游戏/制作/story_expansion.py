"""Shared bilingual story additions. Imported by both Twine edition builders."""
import json


CN_NAMES = {
    'Initialize': '初始化', 'Start': '开始', 'Choose a Character': '选择角色',
    'Journal': '旅程手记',
    'Boar-Forest': '猪_森林', 'Boar-Machine': '猪_巨兽', 'Boar-Path': '猪_足迹',
    'Boar-Approach': '猪_靠近', 'Boar-Lights': '猪_光芒', 'Boar-Smell': '猪_机油',
    'Boar-Charge': '猪_撞击', 'Boar-God': '猪_神明', 'Boar-Mist': '猪_喷气',
    'Boar-Choice': '猪_抉择', 'Boar-Leave': '猪_存活', 'Boar-Stay': '猪_灭绝',
    'Cat-Cage': '猫_牢笼', 'Cat-Aisle': '猫_走道', 'Cat-Visitor': '猫_光',
    'Cat-Label': '猫_标签', 'Cat-Food': '猫_饭', 'Cat-Pills': '猫_药味',
    'Cat-Bowl': '猫_推碗', 'Cat-Chew': '猫_咀嚼', 'Cat-Color': '猫_色彩',
    'Cat-Home': '猫_新家', 'Cat-Window': '猫_窗边', 'Cat-Priest': '猫_祭司',
    'Cat-Wake': '猫_醒来', 'Cat-Farewell': '猫_告别', 'Cat-Recover': '猫_康复',
    'Cat-Depart': '猫_离去',
    'Duck-Pen': '鸭_泥沼', 'Duck-Crowd': '鸭_拥挤', 'Duck-Heaven': '鸭_神迹',
    'Duck-Help': '鸭_同伴', 'Duck-Scramble': '鸭_争夺', 'Duck-Grain': '鸭_粮食',
    'Duck-Eat': '鸭_独食', 'Duck-Share': '鸭_分食', 'Duck-Scale': '鸭_天平',
    'Duck-Priest': '鸭_祭司', 'Duck-Yes': '鸭_是', 'Duck-No': '鸭_否',
    'Boar-Stream': '猪_溪水', 'Boar-Mud': '猪_泥印', 'Boar-Roots': '猪_树根',
    'Boar-Ridge': '猪_土坡', 'Boar-Listen': '猪_停听', 'Boar-Marker': '猪_路标',
    'Boar-Fallen': '猪_倒树', 'Boar-Burrow': '猪_树洞', 'Boar-Trunk': '猪_树心',
    'Boar-Fuel': '猪_铁壳', 'Boar-Question': '猪_试探', 'Boar-Answer': '猪_等回答',
    'Boar-Bow': '猪_低头', 'Boar-Gifts': '猪_赠礼', 'Boar-Taste': '猪_木屑',
    'Boar-Shadow': '猪_树荫', 'Boar-Dusk': '猪_黄昏', 'Boar-Retrace': '猪_来路',
    'Boar-Wait': '猪_再等',
    'Cat-Neighbor': '猫_隔壁', 'Cat-Draft': '猫_夜风', 'Cat-Keys': '猫_钥匙',
    'Cat-Sale': '猫_交谈', 'Cat-Receipt': '猫_凭据', 'Cat-CleanBowl': '猫_换碗',
    'Cat-Witness': '猫_目光', 'Cat-Carrier': '猫_提笼', 'Cat-LookOut': '猫_抬头',
    'Cat-Hide': '猫_藏起', 'Cat-Door': '猫_门槛', 'Cat-Water': '猫_水碗',
    'Cat-Call': '猫_电话', 'Cat-Signal': '猫_叫一声', 'Cat-Sleeve': '猫_袖口',
    'Cat-Ride': '猫_夜路', 'Cat-Visit': '猫_探望', 'Cat-Treatment': '猫_吃饭',
    'Cat-Rest': '猫_等一等', 'Cat-EmptyCarrier': '猫_空提笼',
    'Duck-Water': '鸭_水面', 'Duck-Fence': '鸭_围栏', 'Duck-Halo': '鸭_倒影',
    'Duck-OldDuck': '鸭_老鸭', 'Duck-Return': '鸭_回来', 'Duck-Hunger': '鸭_饿着',
    'Duck-Gate': '鸭_开门', 'Duck-Tracks': '鸭_脚印', 'Duck-Wait': '鸭_远望',
    'Duck-Wing': '鸭_伤翅', 'Duck-After': '鸭_散场', 'Duck-Fallen': '鸭_低处',
    'Duck-Guard': '鸭_护粮', 'Duck-Carried': '鸭_悬空', 'Duck-Crate': '鸭_木箱',
    'Duck-Voices': '鸭_人声', 'Duck-Ink': '鸭_记号', 'Duck-Grains': '鸭_六粒',
    'Duck-Wire': '鸭_铁丝', 'Duck-Screen': '鸭_转身',
    'Duck-YesReply': '鸭_能决定', 'Duck-NoReply': '鸭_也在其中',
}


def extend_story(api, language):
    """Add playable scenes and redirect existing links without changing save IDs."""
    english = language == 'en'
    passages = api['passages']

    def t(cn, en):
        return en if english else cn

    def name(key):
        return key if english else CN_NAMES[key]

    def edit(key, transform):
        for index, (title, body, tags) in enumerate(passages):
            if title == name(key):
                passages[index] = (title, transform(body), tags)
                return
        raise ValueError('Missing passage: ' + name(key))

    def replace(key, old, new):
        def transform(body):
            if old not in body:
                raise ValueError('Missing text in ' + name(key) + ': ' + old[:100])
            return body.replace(old, new, 1)
        edit(key, transform)

    def edge(key, old, new):
        replace(key, json.dumps(name(old), ensure_ascii=False), json.dumps(name(new), ensure_ascii=False))

    def p(cn, en, kind=''):
        return api['para'](t(cn, en), kind)

    def voice(cn, en):
        return p(cn, en, 'voice')

    def flag(variable):
        return '(set: $' + variable + ' to true)'

    def when(variable, yes, no=''):
        return '(if: $' + variable + ')[' + yes + ']' + ('(else:)[' + no + ']' if no else '')

    def choices(*items):
        return api['choices'](*[(t(cn, en), t(detail_cn, detail_en), name(target))
                                for cn, en, detail_cn, detail_en, target in items])

    def s(key, role, number, chapter, path, body, target=None, label=None,
          sound='', progress=0, fx=''):
        alt = {
            '新/1在森林.jpg': ('幽蓝的树林与林间小径', 'Blue woodland and a narrow forest path'),
            '新/2看见伐木机.jpg': ('树林边缘的伐木机', 'A logging machine at the edge of the woods'),
            '新/3伐木机靠近.jpg': ('伐木机靠近，钢铁轮盘露在树间', 'The logging machine draws close, steel wheels showing between the trees'),
            '新/4机器发光.jpg': ('林边亮着灯的机器', 'The machine shines its lights at the forest edge'),
            '新/5野猪靠近.jpg': ('野猪站在机器前面', 'A wild pig stands in front of the machine'),
            '新/6机器变野猪.jpg': ('野猪眼中长着獠牙的钢铁巨神', 'The steel god with tusks as the wild pig sees it'),
            '新/野猪说话.jpg': ('野猪望着林间的巨神', 'The wild pig looks up at the great god among the trees'),
            '猫/1.jpg': ('挤在铁栏杆后的猫', 'Cats crowded behind iron bars'),
            '猫/2.jpg': ('猫所期待的房间和暖灯', 'The room and warm lamp the cat hopes for'),
            '猫/3.jpg': ('放在猫面前的食碗', 'A food bowl set down in front of the cat'),
            '猫/4.jpg': ('猫食碗里混着几粒胶囊', 'Capsules mixed into the food in the cat bowl'),
            '猫/5.jpg': ('猫眼中摇晃的彩色笼子', 'A colorful cage swaying in the cat’s vision'),
            '猫/6.jpg': ('有沙发和窗边猫窝的房间', 'A room with a sofa and a cat bed by the window'),
            '猫/7祭司说话猫.jpg': ('猫梦中的祭司', 'The priest in the cat’s dream'),
            '鸭/鸭1.jpg': ('站在泥水里的鸭子', 'A duck stands in muddy water'),
            '鸭/鸭2.jpg': ('围栏内聚在一起的鸭群', 'Ducks gather inside the fence'),
            '鸭/鸭3.jpg': ('鸭群仰望撒粮的人', 'Ducks look up at the person scattering grain'),
            '鸭/鸭5.jpg': ('站在秤盘上的蓝色鸭子', 'A blue duck stands on the scale'),
            '鸭/鸭6.jpg': ('面向屏幕外的鸭祭司', 'The duck priest faces the person beyond the screen'),
        }[path]
        api['scene'](name(key), role, number, t(*chapter), path, t(*alt), body,
                     name(target) if target else None,
                     t(*(label or ('继续 →', 'Continue →'))), sound=sound,
                     classes='expanded-scene', progress=progress)
        if fx:
            replace(key, ' data-sound=', ' data-fx="' + fx + '" data-sound=')

    variables = {
        'Boar-Forest': ['pigWater', 'pigRoots', 'pigShelter', 'pigRings', 'pigMarked',
                        'pigTasted', 'pigWaited', 'pigRetraced'],
        'Cat-Cage': ['catHeard', 'catCold', 'catProof', 'catTouch', 'catSignal', 'catPatient'],
        'Duck-Pen': ['duckFence', 'duckAsked', 'duckTracks', 'duckFallen', 'duckCrate', 'duckPrice'],
    }
    for beginning, fields in variables.items():
        reset = ''.join('(set: $' + field + ' to false)' for field in fields)
        edit(beginning, lambda body, reset=reset: reset + body)
        edit('Initialize', lambda body, reset=reset: body + reset)

    # Forest: the old water source, damaged homes, a god that does not answer.
    edge('Boar-Forest', 'Boar-Machine', 'Boar-Stream')
    replace('Boar-Forest', t('去林子边看看 →', 'Go to the clearing →'),
            t('沿着溪边过去 →', 'Follow the stream toward the sound →'))
    s('Boar-Stream', 'pig', '01', ('今天的水浅了', 'The water is low today'), '新/1在森林.jpg',
      p('你本来只是来喝水。昨天还能没过蹄子的地方，今天只剩一条细流。水面漂着碎叶，上游还传来咚咚的响声。你用鼻子拱了拱石缝，没找到藏在下面的小虫。',
        'You only came for a drink. Yesterday the water covered your hooves; today it barely threads between the stones. Torn leaves drift past. The thudding comes from upstream. You nose a stone aside, looking for the little creatures usually hiding underneath. Nothing moves.')
      + voice('“昨天还不是这样。上面到底怎么了？”', '“It wasn’t like this yesterday. What happened upstream?”')
      + choices(('看看岸边的泥', 'Check the bank', '泥里有你不认识的印子。', 'Something unfamiliar has marked the mud.', 'Boar-Mud'),
                ('去旧树下面找吃的', 'Look beneath the old tree', '那里常有落下的果子。', 'Fruit usually falls there.', 'Boar-Roots')),
      sound='pigOpen', progress=10, fx='forest')
    s('Boar-Mud', 'pig', '01', ('不是蹄印', 'These are not hoofprints'), '新/1在森林.jpg',
      flag('pigWater') + p('泥岸被压出两道很深的沟，横着穿过溪水。你把一只蹄子放进去，比了比，连沟的一半都填不满。两边的泥被挤进水里，水绕不过去，只能慢慢往石头下面渗。',
        'Two deep grooves cross the bank and the stream. You put a hoof in one. It does not come close to filling it. Mud has been pushed into the channel on both sides, leaving the water to seep under a heap of stones.')
      + voice('“这得多重啊。它也从这里喝水？”', '“How heavy is it? Does it drink here too?”'),
      'Boar-Ridge', ('顺着印子往上走 →', 'Follow the grooves uphill →'), 'pigOpen', 12)
    s('Boar-Roots', 'pig', '01', ('空了的树下', 'Nothing beneath the tree'), '新/1在森林.jpg',
      flag('pigRoots') + p('你记得树根旁有一小堆熟果，昨天还没吃完。现在树枝横在地上，果子埋进了泥。你翻出一颗，咬下去全是沙，赶紧吐了。树皮上还留着很新的一道刮痕。',
        'There was a little pile of ripe fruit beside these roots. You left some yesterday. Now branches cover the ground, and the fruit is pressed into the mud. You dig one out, bite through grit, and spit it away. A fresh scrape runs up the bark.')
      + voice('“我才离开一会儿。谁把这里弄成这样？”', '“I was only gone a little while. Who did this?”'),
      'Boar-Ridge', ('从土坡上看看 →', 'Look from the ridge →'), 'pigOpen', 12)
    s('Boar-Ridge', 'pig', '01', ('树梢在往下沉', 'The treetops sink'), '新/2看见伐木机.jpg',
      p('你爬上土坡，正好看见一片树梢慢慢往下沉。鸟叫突然密起来，几只鸟从枝叶里冲出去。那个声音停了一下，又响起来，比刚才更近。你往后缩了半步。',
        'From the ridge you see a patch of treetops slowly sink. Birds burst out of the leaves, calling all at once. The noise stops, then begins again, closer this time. You shift back half a step. Something down there is moving through the trees.')
      + choices(('先停下来听听', 'Stop and listen', '看看它会不会靠过来。', 'Find out whether it is coming this way.', 'Boar-Listen'),
                ('走到空地边', 'Go to the clearing', '躲在树后面看。', 'Keep a tree between you and the noise.', 'Boar-Machine')),
      sound='pigOpen', progress=14)
    s('Boar-Listen', 'pig', '01', ('它没有停下来', 'It never rests'), '新/2看见伐木机.jpg',
      p('你伏在坡后，数着它的声音。响一阵，停一下，又响一阵。停下的时候，没有喘气声，也听不到啃食的声音。只有树枝折断以后，远处传来一阵沙沙响。',
        'You crouch behind the ridge and listen. A roar, a pause, another roar. In the pauses there is no panting and no chewing. After each crack of a branch comes a long rustle of falling leaves. You wait for an animal call. None comes.')
      + voice('“吃这么多，还不歇一会儿？”', '“After eating that much, doesn’t it need a rest?”'),
      'Boar-Machine', ('再看清楚一点 →', 'Get a clearer look →'), 'pigOpen', 15)
    edge('Boar-Path', 'Boar-Approach', 'Boar-Marker')
    s('Boar-Marker', 'pig', '01', ('把来路记住', 'Remember the way back'), '新/1在森林.jpg',
      flag('pigMarked') + p('小径的入口被倒下的枝叶遮住了。从空地回头看，很容易走过头。你把一截白色枯枝拱到老树旁，又在树根上蹭掉一点泥。离开时，只要找到它们，就能认出路口。',
        'Fallen branches hide the entrance to the path. From the clearing it would be easy to walk straight past. You push a pale dead branch beside the old tree and rub some mud off its root. On the way back, those marks should help you find it.')
      + voice('“从这里回去。别走错了。”', '“Back this way. Remember.”'),
      'Boar-Approach', ('回到空地旁 →', 'Return to the clearing →'), 'pigOpen', 23)
    edge('Boar-Approach', 'Boar-Lights', 'Boar-Fallen')
    s('Boar-Fallen', 'pig', '02', ('倒下的那棵树', 'The tree that fell'), '新/3伐木机靠近.jpg',
      p('断树倒在你常走的地方。树冠压住了灌木，叶子还在抖。你本想从下面钻过去，鼻尖却碰到湿漉漉的木头。平时遮雨的那片阴凉，整个翻到了地上。',
        'The fallen tree blocks the way you usually take. Its crown crushes the bushes; leaves are still trembling. You try to squeeze underneath and touch wet wood with your nose. The shade where you sheltered from rain is lying on its side.')
      + choices(('看看原来的树洞', 'Look for the hollow', '洞口被枝叶挡住了。', 'Branches cover the entrance.', 'Boar-Burrow'),
                ('闻闻断开的树干', 'Sniff the broken trunk', '树心的气味很重。', 'The exposed wood smells strong.', 'Boar-Trunk')),
      sound='pigOpen', progress=28, fx='machine')
    s('Boar-Burrow', 'pig', '02', ('雨天躲过的地方', 'Where you hid from rain'), '新/1在森林.jpg',
      flag('pigShelter') + p('树洞的底翻出来了，里面的干叶子散了一地。你以前在这里挤着睡过，鼻子贴着树皮，外面下大雨也淋不到。你拱了拱那堆叶子，已经没有能钻进去的口子。',
        'The hollow has tipped over, spilling its dry leaves. You slept wedged in there once, your nose against the bark, while rain poured outside. You push at the leaves. There is no longer an opening large enough to crawl into.')
      + voice('“下雨的时候，我还能去哪儿？”', '“Where do I go when it rains now?”'),
      'Boar-Lights', ('身后亮了起来 →', 'Light falls across your back →'), 'pigOpen', 30)
    s('Boar-Trunk', 'pig', '02', ('里面也不是食物', 'It leaves the trunk behind'), '新/3伐木机靠近.jpg',
      flag('pigRings') + p('树干断面一圈套着一圈，湿润得像刚被咬开的果子。可你舔了一下，只有涩味。大家伙扯掉树枝，又把长长的树干拖到一边。它折了这么多树，却没有把树干吃下去。',
        'Rings circle the broken wood. It is wet, like a freshly bitten piece of fruit, but a lick gives you only bitterness. The huge creature strips the branches and drags the long trunk aside. It breaks the trees without swallowing them.')
      + voice('“不吃？那它弄倒树干什么？”', '“It isn’t eating it? Why knock it down?”'),
      'Boar-Lights', ('抬头看看它 →', 'Look up at the creature →'), 'pigOpen', 30)
    edge('Boar-Smell', 'Boar-Charge', 'Boar-Fuel')
    s('Boar-Fuel', 'pig', '02', ('壳下面有人', 'Someone beneath the shell'), '新/3伐木机靠近.jpg',
      p('你绕到侧面，看见硬壳高处有一块透明的东西。后面晃着一个影子。影子动一下，巨大的铁臂就抬起来；影子停住，铁臂也停住了。你踮着蹄子，还是看不清它的脸。',
        'Around the side you notice a clear patch high in the shell. A small figure moves behind it. The figure shifts, and the huge steel arm rises. It stops, and the arm stops too. You stretch up on your hooves but cannot make out its face.')
      + voice('“它肚子里还有个东西？”', '“There’s something living inside it?”'),
      'Boar-Charge', ('回到灯光前 →', 'Move back in front of the lights →'), 'pigOpen', 41)
    edge('Boar-God', 'Boar-Mist', 'Boar-Question')
    s('Boar-Question', 'pig', '04', ('它认得你吗', 'Does it recognize you'), '新/6机器变野猪.jpg',
      p('你慢慢站直，把发麻的獠牙从泥里抬起来。巨神的脸上没有伤口。你刚才用尽了力气，它连头都没低过。也许它早就见过你，也许只是还没发现你站在这里。',
        'You straighten up and lift your aching tusks out of the mud. There is no mark on the god’s face. You struck as hard as you could, and it never even lowered its head. Perhaps it already knows you. Perhaps it has not noticed you at all.')
      + choices(('叫一声，等它回应', 'Call and wait for an answer', '如果它听得懂呢？', 'Perhaps it understands you.', 'Boar-Answer'),
                ('像它一样低下头', 'Lower your head before it', '你不知道该怎么见神。', 'You do not know how to greet a god.', 'Boar-Bow')),
      sound='pigWorship', progress=59)
    s('Boar-Answer', 'pig', '04', ('没有回答', 'No answer'), '新/野猪说话.jpg',
      p('你短短地叫了一声。林子里没有别的野猪回答，巨神也没有。你又叫了一声，这次更响。灯光从你头顶扫过去，一根树枝在它身后断了，像是谁踩碎了一截干骨头。',
        'You give a short call. No wild pig answers from the trees. Neither does the god. You call again, louder. Its light sweeps over your head. Behind it, a branch cracks with a sound like a dry bone breaking underfoot.')
      + voice('“我就在这里。你没听见吗？”', '“I’m right here. Can’t you hear me?”'),
      'Boar-Mist', ('巨神忽然动了 →', 'The great god moves →'), 'pigWorship', 63)
    s('Boar-Bow', 'pig', '04', ('低头等着', 'With your head lowered'), '新/6机器变野猪.jpg',
      p('你压低前腿，学着它刚才的样子低下头。过了好一会儿，泥水渗进蹄子。巨神没有伸出獠牙碰你，也没有靠过来闻。你悄悄抬起一只眼睛，它还望着远处的树。',
        'You bend your front legs and lower your head, copying its posture. Mud creeps around your hooves while you wait. The god does not touch tusks with you or lean close to sniff. You lift one eye. It is still facing the trees beyond you.')
      + voice('“还不行吗？我要再低一点？”', '“Is this wrong? Do I need to bow lower?”'),
      'Boar-Mist', ('听见一声长响 →', 'A long hiss begins →'), 'pigWorship', 63)
    edge('Boar-Mist', 'Boar-Choice', 'Boar-Gifts')
    s('Boar-Gifts', 'pig', '04', ('神明留下的东西', 'What the god leaves behind'), '新/2看见伐木机.jpg',
      p('白雾散了，巨神又往前走。你跟出几步，发现它身后铺着细细的木屑，还有刚切下来的树皮。你已经很久没吃东西，肚子又叫了一声。也许这些就是给你的。',
        'When the mist clears, the god moves on. You follow a few paces. Fine wood chips and freshly stripped bark cover the ground behind it. Your stomach growls. You have not eaten for hours. Perhaps this is what it has left for you.')
      + choices(('尝一点木屑', 'Try a wood chip', '看看是不是能吃的。', 'Find out whether it is food.', 'Boar-Taste'),
                ('先找个凉快的地方', 'Find some shade first', '太阳已经照到背上了。', 'The sun is hot on your back.', 'Boar-Shadow')),
      sound='pigWorship', progress=73)
    s('Boar-Taste', 'pig', '04', ('咽不下去', 'You cannot swallow it'), '新/5野猪靠近.jpg',
      flag('pigTasted') + p('你挑了一小片木屑，嚼了两下。硬刺扎进牙缝，舌头上全是苦味。你吐出来，在泥上蹭了蹭嘴。巨神已经走远，后面还落着同样的东西。没有果子，也没有根茎。',
        'You pick up a small chip and chew twice. A splinter catches between your teeth. Your tongue tastes bitter. You spit it out and rub your snout against the mud. Farther ahead the god leaves the same things: wood and bark, no fruit, no roots.')
      + voice('“也许……这块不够好。”', '“Maybe… I picked the wrong piece.”'),
      'Boar-Dusk', ('天开始暗了 →', 'The light begins to fade →'), 'pigWorship', 76)
    s('Boar-Shadow', 'pig', '04', ('影子不肯停', 'The shade keeps moving'), '新/2看见伐木机.jpg',
      p('树荫少了很多。你挪到巨神身后，它的影子刚好盖住你的背。可没歇多久，影子就移开了。你只好跟着走。它停下的时候，你才能喘口气；它再往前，你也得往前。',
        'There is little shade left. You move behind the god, where its shadow covers your back. Before you can rest, the shadow slides away. You follow. When it stops, you catch your breath. When it moves again, so must you.')
      + voice('“等一下。我还没歇够。”', '“Wait. I haven’t rested yet.”'),
      'Boar-Dusk', ('再跟出去一段 →', 'Follow a little farther →'), 'pigWorship', 76)
    s('Boar-Dusk', 'pig', '05', ('天快黑了', 'It is almost dark'), '新/野猪说话.jpg',
      p('傍晚的风吹过空地。白天还连在一起的树冠，现在裂开了很大一块。你站在光秃秃的地方，突然不知道今晚该在哪儿躺下。巨神仍在叫，好像不需要睡觉。',
        'Evening wind crosses the clearing. A wide gap splits the treetops that joined together this morning. You stand in the open, wondering where to lie down tonight. The god keeps roaring. It seems to have no need for sleep.')
      + when('pigShelter', p('你想起那个翻倒的树洞。里面的干叶子，这会儿大概已经湿了。',
                             'You think of the overturned hollow. Its dry leaves must be wet by now.'))
      + choices(('回头认一认来路', 'Look for the way back', '看看溪水还在什么方向。', 'Work out which way the stream lies.', 'Boar-Retrace'),
                ('再等一会儿', 'Wait a little longer', '它也许会停下来。', 'Perhaps it will finally stop.', 'Boar-Wait')),
      sound='pigWorship', progress=79)
    s('Boar-Retrace', 'pig', '05', ('还能认出来', 'You can still find it'), '新/1在森林.jpg',
      flag('pigRetraced') + when('pigMarked',
        p('老树旁的白色枯枝还在。你把头朝那边转了转，小径藏在两丛叶子后面。只要走过去，就不用再追着巨神的影子跑。',
          'The pale branch is still beside the old tree. You turn toward it. The path is tucked behind two clumps of leaves. If you go that way, you will no longer have to chase the god’s shadow.'),
        p('你顺着风闻了很久，终于分出了溪边湿泥的气味。回去要绕一段路，可方向还没有丢。你往那边走了两步，又回过头看巨神。',
          'You test the wind until you recognize the smell of wet mud beside the stream. The way back will be longer, but you have not lost it. You take two steps in that direction, then look back at the god.'))
      + when('pigWater', p('水沟被堵住的地方也在那边。至少你知道，可以从更上游找水。',
                           'The blocked channel lies that way too. At least you know to look farther upstream for water.')),
      'Boar-Choice', ('回到空地边做决定 →', 'Make your choice at the forest edge →'), 'pigWorship', 82)
    s('Boar-Wait', 'pig', '05', ('又等过一阵', 'Still waiting'), '新/2看见伐木机.jpg',
      flag('pigWaited') + p('你等到地上的影子伸得很长。巨神停了一次，可那只是为了转向另一棵树。你跟着挪过去，空着的肚子疼了一下。它从没说过会喂你；这件事，你以前没有想过。',
        'You wait until the shadows stretch across the ground. The god stops once, but only to turn toward another tree. You shuffle after it. Your empty stomach aches. It has never actually promised to feed you. Until now, that had not occurred to you.')
      + voice('“要是等到明天，它还不停呢？”', '“What if it is still doing this tomorrow?”'),
      'Boar-Choice', ('天黑以前，做个决定 →', 'Decide before it gets dark →'), 'pigWorship', 82)

    # Cage and home: early observations become evidence and familiar comforts.
    edge('Cat-Cage', 'Cat-Visitor', 'Cat-Neighbor')
    edge('Cat-Cage', 'Cat-Aisle', 'Cat-Draft')
    replace('Cat-Cage', t('朝门口看去', 'Look toward the door'), t('听听隔壁的声音', 'Listen to the next cage'))
    replace('Cat-Cage', t('有人朝这边走过来了。', 'Someone is coming this way.'),
            t('有只猫一直没有睡着。', 'One of the cats has been awake all night.'))
    replace('Cat-Cage', t('凑到栏杆边看看', 'Peer through the bars'), t('找个不漏风的角落', 'Find a corner out of the draft'))
    replace('Cat-Cage', t('把头伸出去，看看笼子外面。', 'Try to see what lies outside the cage.'),
            t('笼子底下的布已经凉了。', 'The cloth under you has gone cold.'))
    s('Cat-Neighbor', 'cat', '01', ('隔壁还醒着', 'Your neighbor is awake'), '猫/1.jpg',
      flag('catHeard') + p('隔壁的猫轻轻咳了一下。它说，昨天有人抱它出去，摸了摸，又放回原来的笼子。你问外面有没有窗台，它想了半天，说自己只记得头顶的灯很亮。',
        'The cat next door coughs softly. Yesterday someone carried it out, felt along its sides, and put it back. You ask whether there was a windowsill outside. It thinks for a long time. All it remembers is the bright light overhead.')
      + voice('“你要是出去了，替我看看太阳。”', '“If you get out, have a look at the sun for me.”'),
      'Cat-Keys', ('门锁响了一声 →', 'A key turns in the lock →'), 'catOpen', 10)
    s('Cat-Draft', 'cat', '01', ('挪过去一点', 'A little farther over'), '猫/1.jpg',
      flag('catCold') + p('你用爪子把薄布拢到肚子下面。旁边的猫动了一下，给你让出一点位置。你们挤在一起，总算没有那么冷。可门一开，风又从最下面那道缝钻了进来。',
        'You pull the thin cloth under your belly. Another cat shifts over to make a little space. Pressed together, you are finally less cold. Then the door opens and air slips through the gap beneath it. You tuck your paws under yourself again.')
      + voice('“到外面以后，也会一直这么冷吗？”', '“Will it be cold outside too?”'),
      'Cat-Keys', ('有人走进来了 →', 'Footsteps come into the room →'), 'catOpen', 10)
    s('Cat-Keys', 'cat', '01', ('钥匙碰着笼门', 'Keys against the bars'), '猫/1.jpg',
      p('钥匙一响，几只猫都抬起头。有人把上面的笼子搬到灯下，又把你这只挪到前面。你晃了一下，爪子没抓稳。那个人没有看你，只是拍掉袖子上的毛。',
        'At the rattle of keys, the cats lift their heads. Someone moves an upper cage under the light and pulls yours to the front. You wobble, unable to keep your claws on the floor. The person does not look down, only brushes fur off a sleeve.')
      + voice('“今天能出去吗？”', '“Do I get to go out today?”'),
      'Cat-Sale', ('听见笼门外的交谈 →', 'Listen to the people outside →'), 'catOpen', 12)
    s('Cat-Sale', 'cat', '02', ('门外的人声', 'Voices outside'), '猫/1.jpg',
      p('一个陌生人蹲下来，把手指伸近笼门。“它怎么不太动？”旁边的人笑着说：“刚睡醒，脾气好。”你用力甩了甩尾巴，尾尖却只碰了一下地。陌生人的手还在等着。',
        'A stranger crouches and offers a finger near the door. “Why is this one so still?” The person beside them smiles. “Just woke up. Very gentle.” You try to flick your tail, but its tip only brushes the floor. The stranger keeps the finger there, waiting.')
      + choices(('靠过去闻闻那只手', 'Sniff the offered hand', '它没有急着抓你。', 'It is not trying to grab you.', 'Cat-Visitor'),
                ('先看看走道外面', 'Look down the aisle first', '你还不知道门通到哪里。', 'You still do not know where the door leads.', 'Cat-Aisle')),
      sound='catOpen', progress=16)
    edge('Cat-Label', 'Cat-Food', 'Cat-Receipt')
    s('Cat-Receipt', 'cat', '02', ('那张纸被收起来了', 'The paper goes into a bag'), '猫/1.jpg',
      flag('catProof') + p('陌生人拿手机对着标签拍了一张，又把一张折好的纸装进包里。有人催：“放心吧，都是一样的。”陌生人没有马上走，先低头看你，问你是不是饿了。你舔了舔干燥的鼻子。',
        'The stranger photographs the label and folds another sheet of paper into a bag. Someone says, “Don’t worry. They’re all the same.” The stranger stays beside the cage, looks at you, and asks whether you are hungry. You lick your dry nose.')
      + voice('“你会把我和那张纸一起带走吗？”', '“Will you take me along with that paper?”'),
      'Cat-CleanBowl', ('有人拿来食碗 →', 'Someone brings a bowl →'), 'catOpen', 25)
    edge('Cat-Visitor', 'Cat-Food', 'Cat-CleanBowl')
    s('Cat-CleanBowl', 'cat', '03', ('饭送来之前', 'Before the food arrives'), '猫/3.jpg',
      p('原来的空碗被拿走了。你闻到食物，忍不住往前蹭。外面的人说：“让它吃点，精神就好了。”陌生人把手收回去，站在笼门旁边等，没有跟着别人离开。',
        'The empty bowl is taken away. You smell food and shuffle forward despite yourself. “Let it eat,” someone says. “It’ll perk up.” The stranger withdraws the offered hand but stays beside the cage instead of following the others away.')
      + voice('“吃完就走，是不是？”', '“We leave after I eat, right?”'),
      'Cat-Food', ('把鼻子凑过去 →', 'Lean toward the food →'), 'catInteract', 27)
    edge('Cat-Bowl', 'Cat-Chew', 'Cat-Witness')
    s('Cat-Witness', 'cat', '03', ('有人看见了', 'Someone notices'), '猫/4.jpg',
      flag('catProof') + p('碗被推回来时，里面的一粒硬东西滚到了表面。陌生人伸头看了一眼，拿起了手机。旁边的人说是拌进去的营养品。你听不懂，只知道这一次，那只手没有再把你的头按向碗里。',
        'As the bowl slides back, a hard piece rolls to the surface. The stranger leans closer and reaches for the phone. Someone calls it a supplement. You do not understand the explanation. You only notice that this time nobody pushes your head toward the bowl.')
      + voice('“你也觉得味道不对吗？”', '“Does it smell wrong to you too?”'),
      'Cat-Chew', ('肚子又响了一声 →', 'Your stomach growls again →'), 'catInteract', 38)
    edge('Cat-Color', 'Cat-Home', 'Cat-Carrier')
    s('Cat-Carrier', 'cat', '04', ('第一次离开笼架', 'Off the cage shelf at last'), '猫/5.jpg',
      p('脚下忽然离地。你被放进另一个小笼子，底下垫着干净的布。门合上的时候，你吓得缩了一下，可原来那排笼子正在慢慢往后退。你第一次从它们的另一边经过。',
        'Your paws leave the floor. You are lowered into a smaller carrier lined with clean cloth. You flinch when its door closes. But the old row of cages is moving away now. For the first time, you pass along the other side of those bars.')
      + choices(('抬头看着外面', 'Keep looking out', '那个人的手就在旁边。', 'The stranger’s hand is beside the carrier.', 'Cat-LookOut'),
                ('钻进布下面', 'Get under the cloth', '你有点怕晃动的光。', 'The moving light makes you uneasy.', 'Cat-Hide')),
      sound='catDream', progress=51)
    s('Cat-LookOut', 'cat', '04', ('隔着提笼的手', 'A hand beside the carrier'), '猫/2.jpg',
      flag('catTouch') + p('你把鼻子凑到小孔边。那个人停下来，用指背碰了碰你的脸。“快到了。”你听见这三个字重复了两遍。提笼晃起来时，旁边的手也跟着放慢了。',
        'You put your nose to a little opening. The person stops and brushes your cheek with the back of a finger. “Nearly there.” You hear the words twice. When the carrier starts swaying, the hand beside it slows down too.')
      + when('catHeard', p('你努力往亮的地方看，想记住太阳到底是什么样。',
                           'You try to look toward the brightness, to remember what the sun looks like.')),
      'Cat-Door', ('提笼终于停下了 →', 'The carrier finally stops →'), 'catDream', 54)
    s('Cat-Hide', 'cat', '04', ('布下面的声音', 'Sounds through the cloth'), '猫/2.jpg',
      p('你把头埋起来，只露出一只耳朵。外面的声音变低了，有风声，也有金属碰在一起的响声。那个人隔着提笼叫你，没有伸手把布掀开。你一点一点松开了抓紧布料的爪子。',
        'You bury your head, leaving one ear out. The sounds grow muffled: wind, metal against metal, a low voice. The person calls to you through the carrier but does not pull the cloth away. Little by little, you loosen your claws from the fabric.')
      + voice('“再等一会儿。我就出来。”', '“Give me a moment. I’ll come out.”'),
      'Cat-Door', ('听见一扇门打开 →', 'A door opens →'), 'catDream', 54)
    s('Cat-Door', 'cat', '05', ('门开着', 'The door stays open'), '猫/6.jpg',
      p('提笼被轻轻放在地上。门开了，外面没有另一排笼子。一个碗，一张软垫，还有离地很近的窗。那个人坐在旁边等。你试着伸出一只爪子，没有人把你推回去。',
        'The carrier is set gently on the floor. Its door opens. Outside there is no second row of cages: only a bowl, a cushion, and a low window. The person sits nearby and waits. You put one paw out. Nobody pushes you back.')
      + when('catCold', p('地板不凉，风也没有从肚子下面钻过来。你又往外挪了一点。',
                          'The floor is not cold. No draft slips under your belly. You move a little farther out.')),
      'Cat-Home', ('慢慢走进房间 →', 'Step into the room →'), 'catDream', 57, 'warmth')
    edge('Cat-Home', 'Cat-Priest', 'Cat-Water')
    edge('Cat-Window', 'Cat-Priest', 'Cat-Water')
    replace('Cat-Home', t('趴下来歇一会儿', 'Lie down and rest'), t('靠近旁边的水碗', 'Move toward the water bowl'))
    replace('Cat-Home', t('也许只是一路上太累了。', 'Maybe the journey has just worn you out.'),
            t('嘴里一直发干。', 'Your mouth is still dry.'))
    s('Cat-Water', 'cat', '05', ('水就在旁边', 'The water is right there'), '猫/3.jpg',
      p('水就在鼻子前面，你却低不下头。你想再往前一点，前腿软了，碗边碰出一声轻响。那个人马上蹲下来，没有再让你自己走，把你和垫子一起抱了起来。',
        'The water is just in front of your nose, but you cannot lower your head properly. You try to move closer. Your front legs buckle and the bowl gives a small clink. The person crouches at once and lifts you together with the cushion.')
      + voice('“刚才还会走的。你怎么了？”', '“You were walking a moment ago. What’s wrong?”'),
      'Cat-Call', ('听见电话接通 →', 'The phone connects →'), 'catDream', 71)
    s('Cat-Call', 'cat', '05', ('电话那边', 'The voice on the phone'), '猫/6.jpg',
      p('有人在电话里问了很多话。抱着你的人一边回答，一边找钥匙。窗边那盏灯还亮着，猫窝也没有收走。你想把这些都记住，可眼睛已经睁不开了。',
        'A voice on the phone asks questions. The person holding you answers while searching for keys. The lamp is still on by the window. Your new bed is still there. You try to remember the room, but your eyes will not stay open.')
      + when('catProof', p('手机里还留着刚拍的照片。那个人把照片和那张纸一起找出来，放进包里。',
                           'The photographs are still on the phone. The person finds them and puts the folded paper in the bag.'))
      + choices(('用力叫一声', 'Try to call out', '让那个人知道你还醒着。', 'Let them know you can still hear.', 'Cat-Signal'),
                ('把爪子搭在袖口上', 'Rest a paw on the sleeve', '你现在只抬得动一点。', 'It is as far as you can lift it.', 'Cat-Sleeve')),
      sound='catDream', progress=73)
    s('Cat-Signal', 'cat', '05', ('只叫出很轻一声', 'Only a small sound'), '猫/2.jpg',
      flag('catSignal') + p('你攒了半天力气，只发出很轻的一声。那个人却立刻低下头：“我听见了。”手掌贴住你的背，没有把你放回地上。你听见包的拉链响，接着是急急的脚步。',
        'You gather your strength and make only a tiny sound. The person looks down immediately. “I heard you.” A palm settles against your back. You are not put down. A bag zips shut; quick footsteps carry you toward the door.')
      + voice('“别把我留在这里。”', '“Please don’t leave me here.”'),
      'Cat-Ride', ('跟着脚步声出去 →', 'Go with the footsteps →'), 'catDream', 75)
    s('Cat-Sleeve', 'cat', '05', ('抓住一点布料', 'A little fold of fabric'), '猫/2.jpg',
      p('你勾住了袖口的一点布。那个人停下来，把你的爪子托在手心里。“不松开也行。”你没有力气再抓紧了，可那只手一直没有抽走。门被打开，一阵风吹过你的耳朵。',
        'Your claw catches a fold in the sleeve. The person stops and cups your paw. “You can hold on.” You do not have the strength to grip any harder, but the hand stays underneath. The door opens. Air brushes past your ears.')
      + voice('“那就让我抓一会儿。”', '“Let me hold on a little longer.”'),
      'Cat-Ride', ('那只手一直托着你 →', 'The hand keeps supporting you →'), 'catDream', 75)
    s('Cat-Ride', 'cat', '06', ('窗外的夜路', 'The road outside'), '猫/5.jpg',
      p('灯光一盏一盏从外面滑过去。提笼重新晃起来，里面还是那块布。有人报出你的体温，又重复了一遍你的名字。你不明白那些数字，只认得声音还是刚才那个。',
        'Lights slide past outside, one after another. The carrier is moving again, lined with the same cloth. Someone gives a temperature and repeats your name. The numbers mean nothing to you. The voice is familiar, though. It is still the same person.')
      + when('catTouch', p('你把脸挪到那个小孔边，等着刚才碰过你的手。',
                           'You shift your face toward the little opening, waiting for the hand that touched your cheek.')),
      'Cat-Priest', ('声音忽远忽近 →', 'The voices drift in and out →'), 'catPriest', 77)
    edge('Cat-Wake', 'Cat-Recover', 'Cat-Visit')
    s('Cat-Visit', 'cat', '07', ('第二天的探望', 'A visit the next day'), '猫/2.jpg',
      p('再醒来时，那个人换了一件衣服。你隔着笼门闻到熟悉的味道，慢慢把脸转过去。桌上放着一个小食碗，这回没有人催你吃，也没有人说你应该很有精神。',
        'When you wake again, the person is wearing different clothes. You recognize the smell through the cage door and turn your face toward it. A little bowl waits on the table. This time nobody urges you to eat or insists that you ought to be lively.')
      + choices(('凑近闻闻，再吃一口', 'Sniff it and try a mouthful', '这一次先慢慢来。', 'Take it slowly this time.', 'Cat-Treatment'),
                ('先趴着，等一等', 'Lie still a little longer', '有人会等你。', 'Someone is willing to wait.', 'Cat-Rest')),
      sound='catDream', progress=93, fx='warmth')
    s('Cat-Treatment', 'cat', '07', ('吃下一点', 'A small mouthful'), '猫/3.jpg',
      p('你先闻了闻，再舔下一点。那个人没有把碗往前推，只轻轻摸了摸你的耳朵。“今天吃一点就好。”你吃得很慢，中间歇了好几次。碗一直放在你够得到的地方。',
        'You sniff first, then take a little lick. The person does not push the bowl closer, only strokes an ear. “A little is enough today.” You eat slowly, stopping several times. The bowl stays within reach for as long as you need it.')
      + voice('“这个味道，我想记住。”', '“This is a smell I want to remember.”'),
      'Cat-Recover', ('等身体一点点好起来 →', 'Give yourself time to recover →'), 'catDream', 96)
    s('Cat-Rest', 'cat', '07', ('没有人催你', 'Nobody hurries you'), '猫/2.jpg',
      flag('catPatient') + p('你把头放回前爪上。那个人就在旁边坐下来，包还背在肩上，像是刚赶到。过了一会儿，手掌又伸进来。你用鼻子碰了一下，接着睡，没有因为没吃饭被抱走。',
        'You lower your head onto your paws. The person sits beside you, bag still over one shoulder, as if they have only just arrived. After a while a hand reaches in again. You touch it with your nose and sleep. Nobody carries you away for refusing food.')
      + voice('“醒来以后，你还会在吗？”', '“Will you be here when I wake up?”'),
      'Cat-Recover', ('一天一天地过去 →', 'Let the days pass →'), 'catDream', 96)
    edge('Cat-Farewell', 'Cat-Depart', 'Cat-EmptyCarrier')
    s('Cat-EmptyCarrier', 'cat', '07', ('空下来的提笼', 'The carrier is empty'), '猫/6.jpg',
      p('医院走道安静下来。那个人把垫布叠好，放回提笼底下，手在笼门上停了很久。窗边的猫窝是昨天才买的，袋子还没扔，里面放着没用完的东西。',
        'The hospital corridor grows quiet. The person folds the cloth, puts it back in the carrier, and rests a hand on the door for a long time. The bed by the window was bought only yesterday. Its bag is still at home, holding things never used.')
      + when('catProof', p('手机里的照片没有删。那张写着“健康”的纸，也和医院留下的记录放在了一起。',
                           'The photographs stay on the phone. The paper marked “Healthy” is kept with the hospital records.')),
      'Cat-Depart', ('那个人带着空提笼回了家 →', 'The person takes the empty carrier home →'), 'catEnd', 96)

    # Fence and altar: the player sees who gets food and what selection means.
    edge('Duck-Pen', 'Duck-Crowd', 'Duck-Water')
    replace('Duck-Pen', t('前面突然挤了起来 →', 'The crowd suddenly surges →'),
            t('先到水边看看 →', 'Walk to the water first →'))
    s('Duck-Water', 'duck', '01', ('水里的另一只鸭', 'Another duck in the water'), '鸭/鸭1.jpg',
      p('你低头找水喝，水面上也有一只鸭子。它和你一起晃，头顶的光也跟着晃。脚边漂着几根断羽，远一点的水却被围栏隔开了。你伸长脖子，还是够不到。',
        'You lower your head to drink. Another duck wobbles in the water, its light wobbling with yours. Broken feathers float beside your feet. Farther away the water looks clearer, but the fence cuts across it. You stretch your neck and cannot reach.')
      + choices(('沿着围栏走一段', 'Walk along the fence', '看看有没有能过去的地方。', 'Look for a way to the clearer water.', 'Duck-Fence'),
                ('再看看自己的光圈', 'Look at your ring of light', '大家说这证明你被照顾着。', 'They say it means you are cared for.', 'Duck-Halo')),
      sound='duckOpen', progress=12)
    s('Duck-Fence', 'duck', '01', ('够不到的那一边', 'The side you cannot reach'), '鸭/鸭1.jpg',
      flag('duckFence') + p('你贴着铁丝走，试着把头伸过去。脖子够到了，身体却卡在里面。外面有一小块干地，长着细细的草。你拽了一下，草尖从嘴边滑走，铁丝在羽毛上刮了一道。',
        'You follow the wire and push your head through. Your neck reaches, but your body will not. Outside lies a small dry patch with thin grass. You catch a blade, tug, and lose it. The wire scrapes along your feathers as you pull back.')
      + voice('“那边也有地方。为什么不能过去？”', '“There’s room over there. Why can’t we go?”'),
      'Duck-OldDuck', ('回到鸭群旁边 →', 'Return to the other ducks →'), 'duckOpen', 15)
    s('Duck-Halo', 'duck', '01', ('光照不到泥下面', 'The light does not clear the mud'), '鸭/鸭1.jpg',
      p('你把头压低，想看看光是不是从羽毛里长出来的。水里那圈光碎成几段，又慢慢拼回去。肚子还是饿，踩进泥里的脚也没变干净。旁边的鸭子让你别乱动，说光会被弄散。',
        'You lower your head, trying to see whether the light grows out of your feathers. In the water it breaks apart, then joins again. You are still hungry. Your feet are still sunk in mud. A duck beside you says to keep still before you disturb the light.')
      + voice('“可我动不动，都还是饿啊。”', '“But I’m hungry whether I move or not.”'),
      'Duck-OldDuck', ('有人叫住了你 →', 'An older duck calls you over →'), 'duckOpen', 15)
    s('Duck-OldDuck', 'duck', '01', ('在这里待得最久的鸭', 'The duck that has stayed longest'), '鸭/鸭2.jpg',
      p('有只尾羽稀疏的老鸭站在角落。它知道粮会从哪个方向撒下来，也知道开门之前会响几声。你问它是不是一直住在这里。它说，久到以前挤在身边的那些鸭都不在了。',
        'An older duck with thin tail feathers stands in the corner. It knows which way the grain will fall and what sounds come before the gate opens. You ask whether it has always lived here. Long enough, it says, that none of its old neighbors remain.')
      + choices(('问问被带走的鸭子', 'Ask about the ducks taken away', '它们真的去过天堂吗？', 'Did any of them really see heaven?', 'Duck-Return'),
                ('问问今天的粮', 'Ask about today’s food', '你现在饿得更厉害。', 'Your stomach is getting harder to ignore.', 'Duck-Hunger')),
      sound='duckOpen', progress=18)
    s('Duck-Return', 'duck', '01', ('谁回来讲过', 'Who came back to tell you'), '鸭/鸭2.jpg',
      flag('duckAsked') + p('“你见过回来的吗？”你问。老鸭想了一会儿，说没有。“那是谁告诉你的？”它转头看了看别的鸭子：“大家一直都这么说。”你等着它再说一点，它却只低头理了理翅膀。',
        '“Have you seen one come back?” you ask. The old duck thinks, then says no. “Who told you about heaven, then?” It glances toward the flock. “That’s what everyone has always said.” You wait for more, but it only lowers its head to tidy a wing.')
      + voice('“那第一个这么说的，又是谁呢？”', '“Who was the first one to say it?”'),
      'Duck-Crowd', ('前面突然吵起来 →', 'A commotion starts at the front →'), 'duckOpen', 21)
    s('Duck-Hunger', 'duck', '01', ('先把肚子填上', 'An empty stomach first'), '鸭/鸭2.jpg',
      p('老鸭说，别站在最边上，粮常落不到那里。你问为什么不多撒一点，它说自己也等过。说话的时候，它一直望着门。你本来还有别的问题，肚子却响得让你没法集中精神。',
        'The old duck tells you not to stand at the edge; the grain rarely lands there. You ask why more is not scattered. It says it has waited for that too. All the while it watches the gate. You have other questions, but your stomach is making it difficult to think.')
      + voice('“等吃到东西，我再来问。”', '“I’ll ask again after I’ve eaten.”'),
      'Duck-Crowd', ('跟着它看向门口 →', 'Follow its gaze toward the gate →'), 'duckOpen', 21)
    edge('Duck-Crowd', 'Duck-Heaven', 'Duck-Gate')
    s('Duck-Gate', 'duck', '02', ('门只开了一点', 'The gate opens a little'), '鸭/鸭3.jpg',
      p('门缝打开时，几只鸭子一起伸长脖子。一个空箱子被拖进来，底下留着湿湿的拖痕。撒粮的人站住了，门却没有完全关。你第一次看见那条缝后面的地面。',
        'As the gate opens, several ducks stretch their necks. An empty crate scrapes inside, leaving wet tracks behind it. The person with the grain stops. The gate is not quite shut. For the first time you can see the ground on the other side.')
      + choices(('看看地上的印子', 'Study the tracks', '有些印子只朝一个方向。', 'Some of them lead only one way.', 'Duck-Tracks'),
                ('先看撒粮的手', 'Watch the hand with the grain', '也许粮马上就落下来了。', 'The food may fall any moment.', 'Duck-Wait')),
      sound='duckWorship', progress=26)
    s('Duck-Tracks', 'duck', '02', ('只往外去的脚印', 'Tracks going out'), '鸭/鸭2.jpg',
      flag('duckTracks') + p('你认得鸭子的脚印，三根脚趾分开，深浅也熟悉。门口的几行印子通向箱子，外面还有更大的鞋印。你找了半天，没找出同样一行从外面走回来的鸭脚印。',
        'You recognize duck footprints: three toes spread apart, pressed to a familiar depth. Several lines lead toward the crate. Beyond them are larger shoeprints. You look for a matching line of duck tracks coming back in, but cannot find one.')
      + voice('“回来时，是被抱着的吗？”', '“Are they carried when they come back?”'),
      'Duck-Heaven', ('鸭群把你推向前面 →', 'The flock presses you forward →'), 'duckWorship', 30)
    s('Duck-Wait', 'duck', '02', ('粮还在手里', 'The grain is still in the hand'), '鸭/鸭3.jpg',
      p('你盯着那只手。它抬高一点，鸭群就往前挪一点。你也跟着挪，脚踩进前一只鸭子留下的坑。门缝很快被身体挡住，等你再回头，已经什么都看不见了。',
        'You keep your eyes on the hand. It lifts a little; the ducks move a little closer. You move too, stepping into the hollow left by the duck ahead. Bodies soon block the gap in the gate. When you look back, you can no longer see through it.')
      + voice('“先吃到再说。别又空着肚子。”', '“Food first. Don’t miss it again.”'),
      'Duck-Heaven', ('第一粒粮掉下来了 →', 'The first grain falls →'), 'duckWorship', 30)
    edge('Duck-Help', 'Duck-Scramble', 'Duck-Wing')
    s('Duck-Wing', 'duck', '02', ('能站稳了', 'Back on its feet'), '鸭/鸭2.jpg',
      p('那只鸭子把翅膀收好，试着拍了一下。它告诉你，刚才不是不肯往前走，是脚陷得太深。你替它踩住旁边的泥，让它借力拔出来。再抬头时，前面已经少了好几个空位。',
        'The duck folds its wing and gives it a small flap. It was not refusing to move, it explains; one foot was stuck too deep. You brace the mud beside it so it can pull free. When you look up, several spaces near the food have already closed.')
      + voice('“走吧。再晚就真的没了。”', '“Come on. Any later and there’ll be nothing left.”'),
      'Duck-Scramble', ('一起挤回鸭群里 →', 'Push back into the flock →'), 'duckWorship', 44)
    edge('Duck-Scramble', 'Duck-Grain', 'Duck-After')
    s('Duck-After', 'duck', '03', ('粮撒完以后', 'After the last grain'), '鸭/鸭2.jpg',
      p('最后一点粮落进泥里，撒粮的手收回去了。大家还在低头啄，谁都怕漏了一粒。你护着抢来的东西，听见背后有鸭子叫了一声。那声音很轻，很快被踩水声盖住。',
        'The last grain drops into the mud. The hand withdraws. Heads stay down; nobody wants to miss a single piece. You guard what you caught and hear a duck call behind you. The sound is small and quickly lost under splashing feet.')
      + choices(('回头看看低处', 'Look behind you', '有只鸭子还没站起来。', 'One duck has not got back up.', 'Duck-Fallen'),
                ('先护好自己的粮', 'Guard your grain', '旁边还在有人挤。', 'Others are still pressing close.', 'Duck-Guard')),
      sound='duckWorship', progress=53)
    s('Duck-Fallen', 'duck', '03', ('被挡住的那只', 'The one you could not see'), '鸭/鸭2.jpg',
      flag('duckFallen') + p('你把翅膀让开一点，才看见它趴在脚边。它一直够不到地上的粮，刚伸出脖子，又被后面的身体压回去。你往旁边挪了半步，让它能抬起头。自己的肚子也还空着。',
        'You lift a wing and finally see it beside your feet. It could never reach the grain. Each time it stretched its neck, another body pushed it back. You shift half a step so it can lift its head. Your own stomach is still empty too.')
      + voice('“你刚才也一直在这里？”', '“You were here the whole time?”'),
      'Duck-Grain', ('低头数数护着的粮 →', 'Count what you caught →'), 'duckWorship', 55)
    s('Duck-Guard', 'duck', '03', ('护住这几粒', 'Hold on to these few grains'), '鸭/鸭2.jpg',
      p('你把身体压低，用翅膀挡住旁边的嘴。没有谁真的要抢，你却一直不敢松开。刚才用了那么多力气，脚现在还在发抖。你一点一点把泥推开，想看清自己到底抢到了多少。',
        'You lower your body and shield the grains from the beaks beside you. Nobody actually takes one, but you cannot relax. Your feet still tremble from all the pushing. Slowly you clear the mud away to see how much you managed to catch.')
      + voice('“这些得是我的。至少这些是。”', '“These are mine. At least these are.”'),
      'Duck-Grain', ('终于数清了 →', 'At last you can count them →'), 'duckWorship', 55)
    edge('Duck-Eat', 'Duck-Scale', 'Duck-Carried')
    edge('Duck-Share', 'Duck-Scale', 'Duck-Carried')
    s('Duck-Carried', 'duck', '04', ('脚离开泥地', 'Your feet leave the mud'), '鸭/鸭3.jpg',
      p('脚下忽然空了。你拍了一下翅膀，抓着你的手更紧了一点。地上的鸭子都抬起头，有的往前挤，像是盼着下一次能轮到自己。你想说，从这里看并没有更舒服。',
        'Your feet leave the mud. You flap once and the hand tightens. The ducks below look up; some press forward, hoping to be next. You want to tell them that being up here is no more comfortable. Your wings cannot open properly.')
      + choices(('看看旁边的箱子', 'Look into the crate', '里面传来窸窸窣窣的声音。', 'Something rustles inside.', 'Duck-Crate'),
                ('听听上面的人说话', 'Listen to the people', '他们正在商量什么。', 'They are discussing something.', 'Duck-Voices')),
      sound='duckWorship', progress=65)
    s('Duck-Crate', 'duck', '04', ('箱子里面', 'Inside the crate'), '鸭/鸭2.jpg',
      flag('duckCrate') + p('箱子里挤着几只鸭子。你认出一只昨天还在门口争食的，它脖子上的那撮毛没有长齐。它看了你一眼，想往旁边让，却没让出地方。箱子底下也有泥，并不是传说中干净的草地。',
        'Several ducks crowd the crate. You recognize one that fought for food by the gate yesterday; a patch of neck feathers is still missing. It tries to shift over for you, but there is no room. Mud coats the floor. There is no clean grass here.')
      + voice('“你也没到吗？”', '“You haven’t got there either?”'),
      'Duck-Scale', ('你被放到另一边 →', 'You are set down beside it →'), 'duckWorship', 68)
    s('Duck-Voices', 'duck', '04', ('它们在挑什么', 'What they are choosing'), '鸭/鸭3.jpg',
      flag('duckPrice') + p('一个人把你翻了翻，看了看翅膀下面。另一个人拿着笔，说：“这只先称。”没有谁提天堂，也没有谁夸你的光圈。你听见几句很快的话，里面反复出现一个数字。',
        'One person turns you a little and checks beneath a wing. Another holds a pen. “Weigh this one first.” Nobody mentions heaven. Nobody admires your ring of light. They speak quickly, repeating a number you do not understand.')
      + voice('“不是在看我够不够好？”', '“Aren’t they checking whether I’m good enough?”'),
      'Duck-Scale', ('脚碰到了冰凉的盘子 →', 'Your feet touch a cold plate →'), 'duckWorship', 68)
    edge('Duck-Scale', 'Duck-Priest', 'Duck-Ink')
    s('Duck-Ink', 'duck', '04', ('笔尖落下去', 'The pen moves'), '鸭/鸭5.jpg',
      p('指针停了，那个人低头在纸上写了一笔。你努力站直，想让它再看你一眼。它却已经转向下一只鸭子。原来它等的只是指针停下，连你有没有抬头，都不太在意。',
        'The needle settles. The person writes something on the paper. You stand as straight as you can, hoping for another look. They have already turned toward the next duck. They were waiting for the needle, not for you. It makes no difference whether you lift your head.')
      + choices(('想起刚才抢到的粮', 'Remember the grains', '六粒，费了那么大力气。', 'Six grains, after all that struggle.', 'Duck-Grains'),
                ('想起围栏另一边', 'Remember the fence', '你一直够不到那里。', 'You never could reach the other side.', 'Duck-Wire')),
      sound='duckScales', progress=75, fx='scales')
    s('Duck-Grains', 'duck', '04', ('六粒粮的分量', 'The weight of six grains'), '鸭/鸭5.jpg',
      when('duckShare', p('你想起推过去的三粒粮。旁边那只鸭子至少吃到了东西，可你的去处并没有因此变远。那只手没有问你分过多少，只把你的重量记在纸上。',
                         'You remember the three grains you pushed aside. At least the other duck ate something. Sharing has not changed where you are being taken. The hand never asked how much you gave away. It only recorded your weight.'),
                        p('你把六粒都吃了，肚子却没有饱多久。为了这些粮，你踩过泥，也撞开过别的鸭子。现在它们只变成纸上的一点重量，连多看你一眼都没有换来。',
                          'You ate all six, but the fullness barely lasted. For those grains you pushed through mud and against other ducks. Now they have become a little more weight on the paper. They have not earned you another glance.'))
      + voice('“吃到了，也还是在这里。”', '“I got the food. I’m still here.”'),
      'Duck-Screen', ('听见身后有声音 →', 'A voice comes from behind you →'), 'duckScales', 78)
    s('Duck-Wire', 'duck', '04', ('那道铁丝还在', 'The wire is still there'), '鸭/鸭1.jpg',
      when('duckFence', p('你记得铁丝刮过羽毛的感觉。外面那点草离你那么近，脖子一伸就碰得到。你当时还以为，只要被挑中，就能从另一边绕过去。可现在，脚下变成了秤盘。',
                         'You remember the wire scraping your feathers. The grass was so close that you could touch it with your neck stretched out. You thought being chosen might let you go around to the other side. Instead, your feet are on a scale.'),
                        p('你以前没有走到围栏边。总觉得先吃饱，别的以后再说。现在离泥地远了一点，你才看清围栏把整片地方圈得很紧，连那条浅浅的水沟也出不去。',
                          'You never went to the fence. Food first, you thought; everything else could wait. Lifted above the mud, you can finally see how tightly the wire surrounds the pen. Even the shallow water channel has no way through.'))
      + voice('“原来被抱起来，也不算出去。”', '“Being lifted up isn’t the same as getting out.”'),
      'Duck-Screen', ('有谁转过身来 →', 'Someone turns toward you →'), 'duckScales', 78)
    s('Duck-Screen', 'duck', '05', ('它问的不是鸭子', 'The question is for someone else'), '鸭/鸭6.jpg',
      p('一个高高的影子站在前面。你以为它会让你再站直一点，它却从你身旁望过去。它看的不是秤，不是撒粮的手，也不是门后的箱子。它一直望着屏幕外面。',
        'A tall figure waits ahead. You expect it to tell you to stand straighter. Instead, it looks past you. It is not watching the scale, the hand with the grain, or the crate by the gate. It is looking at someone beyond the screen.')
      + when('duckAsked', p('你想起那个没得到回答的问题：谁回来讲过天堂？现在，好像轮到别人回答了。',
                            'You remember the unanswered question: who came back to describe heaven? Now it seems someone else has to answer.')),
      'Duck-Priest', ('顺着它的目光看去 →', 'Follow its gaze →'), 'duckEnd', 81)
    edge('Duck-Priest', 'Duck-Yes', 'Duck-YesReply')
    edge('Duck-Priest', 'Duck-No', 'Duck-NoReply')
    s('Duck-YesReply', 'duck', '05', ('如果你能决定', 'If you get to decide'), '鸭/鸭6.jpg',
      p('“那就别只看它吃得多不多。”祭司朝秤盘点了点头。“粮是你撒的，围栏是你搭的，去哪里也是你决定的。它想喝一口干净的水，却连走到哪边都选不了。”',
        '“Then look at more than how much it eats.” The priest nods toward the scale. “You scatter the grain, build the fence, decide where it goes. It wants a drink of clean water and cannot even choose which side to walk toward.”')
      + voice('“你说自己能决定。那下一步呢？”', '“You say you get to decide. What will you decide next?”'),
      'Duck-Yes', ('看看这些决定影响着什么 →', 'See what those decisions affect →'), 'duckEnd', 94)
    s('Duck-NoReply', 'duck', '05', ('你也在这段生活里', 'You are part of this life too'), '鸭/鸭6.jpg',
      p('“好。那你和它都需要吃饭，也都需要能休息的地方。”祭司没有替你松开围栏。“可这道门谁来开，谁会被带走，它还是说了不算。你走过的时候，会不会看见它？”',
        '“All right. You both need food and somewhere to rest.” The priest leaves the fence closed. “But it still has no say in who opens the gate or who gets carried away. When you pass a place like this, will you notice it?”')
      + voice('“不用先成为神，才肯替它留一点地方。”', '“You do not have to be a god to leave it a little room.”'),
      'Duck-No', ('从身边的事看起 →', 'Look at the choices close to home →'), 'duckEnd', 94)

    # Choice callbacks add context without adding or deleting any final endings.
    def add_before_choices(key, text):
        replace(key, '<div class="actions story-choices">', text + '<div class="actions story-choices">')

    add_before_choices('Boar-Choice', when('pigTasted',
        p('牙缝里的木刺还没弄出来。你已经尝过，木屑不能当饭吃。',
          'The splinter is still between your teeth. You have tried the wood. It is not food.', 'thought')))
    add_before_choices('Cat-Priest', when('catSignal',
        p('你认得那个人的声音。刚才你只叫出一点，它也听见了。',
          'You recognize that voice. It heard even the tiny sound you made.', 'thought')))
    add_before_choices('Duck-Grain', when('duckFallen',
        p('你刚看见，有的鸭子并不是不肯争，只是连站起来的地方都没有。',
          'You have just seen that some ducks never had room to stand, let alone compete.', 'thought')))

    # Make a first tour of all three stories easy to follow.
    for key in ('Boar-Leave', 'Boar-Stay'):
        replace(key, api['link'](t('换个角色 ↗', 'Choose another ↗'), name('Choose a Character')),
                api['link'](t('下一个故事 · 猫 ↗', 'Next story · Cat ↗'), name('Cat-Cage')))
    for key in ('Cat-Recover', 'Cat-Depart'):
        replace(key, api['link'](t('换个角色 ↗', 'Choose another ↗'), name('Choose a Character')),
                api['link'](t('下一个故事 · 鸭子 ↗', 'Next story · Duck ↗'), name('Duck-Pen')))
    replace('Start', t('三个故事 · 六个结局', 'Three stories · Six endings'),
            t('三个故事 · 约 10–15 分钟', 'Three stories · About 10–15 min'))
    replace('Choose a Character', t('选一个角色，看看接下来会发生什么。', 'Choose a character and see what happens next.'),
            t('选一个角色。读完三条故事约需 10–15 分钟。',
              'Choose a character. Allow about 10–15 minutes for all three stories.'))
