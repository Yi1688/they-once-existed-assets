(function(){
  'use strict';
  const storageKey='they-once-existed-new-gift-v1';
  const validEndings=['pig-live','pig-fall','cat-light','cat-sleep','duck-yes','duck-no'];
  let saved={endings:[],muted:false};
  try{const value=JSON.parse(localStorage.getItem(storageKey)||'{}');if(value&&typeof value==='object')saved={endings:Array.isArray(value.endings)?[...new Set(value.endings.filter(x=>validEndings.includes(x)))]:[],muted:value.muted===true};}catch(_){}
  const persist=()=>{try{localStorage.setItem(storageKey,JSON.stringify(saved));}catch(_){}};
  persist();
  // 三条路线按章节播放 GitHub 原始文件直链。同一音频跨页面继续播放，切换章节时停止上一段。
  const sceneAudio={
    themeOpen:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/audio/Hollow%20Knight.mp3?v=b1da8ecb9484',
    themeEnd:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/audio/%E3%81%8B%E3%81%9F%E3%82%8F%E3%82%8C%E6%99%82.m4a?v=76da2363fc9c',
    pigOpen:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AA%E9%9F%B3%E9%A2%91/%E7%8C%AA%E5%BC%80%E5%9C%BA.m4a',pigInteract:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AA%E9%9F%B3%E9%A2%91/%E7%8C%AA%E4%BA%A4%E4%BA%92.m4a',pigWorship:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AA%E9%9F%B3%E9%A2%91/%E7%8C%AA%E5%B4%87%E6%8B%9C.m4a',pigLive:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AA%E9%9F%B3%E9%A2%91/%E7%8C%AA%E5%AD%98%E6%B4%BB.m4a',pigFall:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AA%E9%9F%B3%E9%A2%91/%E7%8C%AA%E7%81%AD%E7%BB%9D.m4a',
    catOpen:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AB%E5%BC%80%E5%9C%BA.m4a',
    catInteract:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AB%E5%90%83%E8%8D%AF.m4a',
    catDream:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AB%E5%B9%BB%E6%83%B3.m4a',
    catPriest:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AB%E7%A5%AD%E5%8F%B8.m4a',
    catEnd:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%8C%AB%E6%AD%BB%E4%BA%A1.m4a',
    duckOpen:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E9%B8%AD%E5%BC%80%E5%9C%BA.m4a',
    duckWorship:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E9%B8%AD%E5%B4%87%E6%8B%9C.m4a',
    duckInteract:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E9%B8%AD%E4%BA%A4%E4%BA%92.m4a',
    duckScales:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E9%B8%AD%E5%A4%A9%E6%9E%B0.m4a',
    duckEnd:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E9%B8%AD%E7%A5%AD%E5%8F%B8.m4a'
  };
  const calls={pig:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%B4%A0%E6%9D%90/%E5%8F%AB%E5%A3%B0/%E9%87%8E%E7%8C%AA%E5%8F%AB.mp3',cat:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%B4%A0%E6%9D%90/%E5%8F%AB%E5%A3%B0/%E7%8C%AB%E5%8F%AB.mp3',duck:'https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E7%B4%A0%E6%9D%90/%E5%8F%AB%E5%A3%B0/%E9%B8%AD%E5%AD%90%E5%8F%AB.mp3'};
  const ambient=new Audio();ambient.loop=true;ambient.preload='none';ambient.volume=.52;
  const preview=new Audio();preview.preload='none';preview.volume=.7;
  let wanted='',active='',unlocked=false,lastPage=null,previewButton=null,previewTimer=0,toastTimer=0,audioContext=null;
  let sceneSoundTimers=[];
  const safeURL=path=>new URL(path,document.baseURI).href;
  const normalVolume=()=>wanted.startsWith('theme')?.26:.52;
  function syncTitleSound(){
    const title=document.querySelector('.title-screen');if(!title)return;
    const playing=!saved.muted&&!ambient.paused&&!ambient.error;
    title.classList.toggle('is-sounding',playing);
    const label=title.querySelector('[data-title-audio-status]'),message=saved.muted?'音乐已关闭，点击开启':!unlocked?'点击开启音乐':ambient.error?'音乐暂时没加载好，点击重试':playing?'音乐已开启':'正在加载音乐…';
    if(label&&label.textContent!==message)label.textContent=message;
  }
  function resetPreview(){preview.pause();if(previewButton)previewButton.classList.remove('is-playing');previewButton=null;clearTimeout(previewTimer);}
  function syncAudio(){
    document.querySelectorAll('[data-audio-toggle]').forEach(b=>{b.textContent=saved.muted?'声音：关':'声音：开';b.classList.toggle('is-off',saved.muted);b.setAttribute('aria-pressed',String(!saved.muted));b.setAttribute('aria-label',saved.muted?'打开声音':'关闭声音');});
    ambient.muted=saved.muted;preview.muted=saved.muted;
    if(saved.muted||!unlocked){ambient.pause();syncTitleSound();return;}
    const source=sceneAudio[wanted]||'';
    if(!source){ambient.pause();active='';ambient.removeAttribute('src');ambient.load();syncTitleSound();return;}
    if(active!==source){ambient.pause();ambient.src=safeURL(source);active=source;}
    ambient.volume=previewButton?.12:normalVolume();
    if(ambient.paused)ambient.play().catch(()=>{});
    syncTitleSound();
  }
  function toast(message){document.querySelector('.sound-toast')?.remove();clearTimeout(toastTimer);const el=document.createElement('div');el.className='sound-toast';el.setAttribute('role','status');el.textContent=message;document.body.append(el);toastTimer=setTimeout(()=>el.remove(),1900);}
  function playCall(animal,button){if(saved.muted){toast('声音已关闭');return;}const source=calls[animal];if(!source)return;resetPreview();previewButton=button;button.classList.add('is-playing');preview.src=safeURL(source);ambient.volume=.12;preview.play().then(()=>{previewTimer=setTimeout(resetPreview,4500);}).catch(()=>resetPreview());}
  preview.addEventListener('ended',()=>{resetPreview();ambient.volume=normalVolume();});preview.addEventListener('pause',()=>{ambient.volume=normalVolume();});preview.addEventListener('error',()=>{resetPreview();ambient.volume=normalVolume();});
  for(const event of ['playing','pause','error','emptied'])ambient.addEventListener(event,syncTitleSound);
  function sound(kind){
    if(saved.muted||!unlocked)return;
    try{
      audioContext=audioContext||new (window.AudioContext||window.webkitAudioContext)();
      if(audioContext.state==='suspended')audioContext.resume().catch(()=>{});
      const time=audioContext.currentTime,gain=audioContext.createGain();gain.connect(audioContext.destination);
      if(kind==='heartbeat'||kind==='monitor'){
        const tone=(offset,frequency,duration,volume)=>{const oscillator=audioContext.createOscillator(),envelope=audioContext.createGain();oscillator.type='sine';oscillator.frequency.setValueAtTime(frequency,time+offset);envelope.gain.setValueAtTime(.001,time+offset);envelope.gain.exponentialRampToValueAtTime(volume,time+offset+.015);envelope.gain.exponentialRampToValueAtTime(.001,time+offset+duration);oscillator.connect(envelope);envelope.connect(audioContext.destination);oscillator.start(time+offset);oscillator.stop(time+offset+duration+.02);};
        if(kind==='heartbeat'){tone(0,58,.13,.13);tone(.19,48,.15,.09);}else tone(0,880,.65,.035);
        return;
      }
      const duration=kind==='ram'?.15:kind==='chew'?.095:.06;
      const osc=audioContext.createOscillator();osc.type=kind==='ram'?'triangle':'sine';osc.frequency.setValueAtTime(kind==='ram'?105:kind==='chew'?680:340,time);osc.frequency.exponentialRampToValueAtTime(kind==='ram'?32:kind==='chew'?180:210,time+duration);gain.gain.setValueAtTime(0,time);gain.gain.linearRampToValueAtTime(kind==='ram'?.12:.045,time+.008);gain.gain.exponentialRampToValueAtTime(.001,time+duration);osc.connect(gain);osc.start(time);osc.stop(time+duration+.02);
    }catch(_){}
  }
  function stopSceneSounds(){sceneSoundTimers.forEach(clearTimeout);sceneSoundTimers=[];}
  function startSceneSounds(page){
    stopSceneSounds();if(page.dataset.fx!=='farewell')return;
    for(const delay of [100,1000,1900,2800,3700])sceneSoundTimers.push(setTimeout(()=>{if(page===lastPage&&!document.hidden)sound('heartbeat');},delay));
    sceneSoundTimers.push(setTimeout(()=>{if(page===lastPage&&!document.hidden)sound('monitor');},4700));
  }
  function artworkImpact(page){
    if(matchMedia('(prefers-reduced-motion: reduce)').matches)return;
    const art=page.querySelector('.artwork'),img=art?.querySelector('img');
    // Only an explicit hit moves the illustration; entering a page never does.
    img?.animate([{transform:'translate(0,0)'},{transform:'translate(-2px,1px)'},{transform:'translate(2px,-1px)'},{transform:'translate(0,0)'}],{duration:210,easing:'ease-out'});
    art?.querySelector('.impact-flash')?.animate([{opacity:0},{opacity:.55,offset:.2},{opacity:0}],{duration:300});
  }
  function revealGod(page){
    const art=page.querySelector('.artwork'),img=art?.querySelector('img');if(!img)return;
    const preload=new Image();preload.src=safeURL('https://raw.githubusercontent.com/Yi1688/they-once-existed-assets/main/%E6%96%B0%E6%B8%B8%E6%88%8F/%E6%96%B0/6%E6%9C%BA%E5%99%A8%E5%8F%98%E9%87%8E%E7%8C%AA.jpg');
    preload.decode().then(()=>{if(page!==lastPage)return;img.src=preload.src;img.alt='第五次撞击之后，机械显出了野猪神明的轮廓';art.dataset.transformed='yes';if(!matchMedia('(prefers-reduced-motion: reduce)').matches)img.animate([{opacity:.25,filter:'brightness(1.8)'},{opacity:1,filter:'brightness(1)'}],{duration:900,easing:'ease-out'});}).catch(()=>{});
  }
  function setupSceneEffects(page){
    const art=page.querySelector('.artwork');
    if(art){
      const veil=document.createElement('div');veil.className='scene-atmosphere';veil.setAttribute('aria-hidden','true');
      if(page.dataset.fx==='steam')for(let i=0;i<3;i++){const cloud=document.createElement('span');cloud.className='atmosphere-cloud';cloud.style.setProperty('--cloud',String(i));veil.append(cloud);}
      art.append(veil);
      if(page.querySelector('[data-task="ram"],[data-task="chew"]')){const flash=document.createElement('span');flash.className='impact-flash';flash.setAttribute('aria-hidden','true');art.append(flash);}
      if(page.dataset.scene==='猫_牢笼'){
        art.classList.add('is-clickable','is-listening');art.tabIndex=0;art.setAttribute('role','button');art.setAttribute('aria-label','听听牢笼里的猫叫');
        const listen=()=>playCall('cat',art);art.addEventListener('click',listen);art.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();listen();}});
      }
    }
    startSceneSounds(page);
  }
  function setupTextEffects(page){
    page.querySelectorAll('.scene-copy h1,.selection-head h1,.journal-head h1').forEach(title=>title.classList.add('ink-title'));
    let order=0;
    page.querySelectorAll('.scene-copy p').forEach(paragraph=>{
      if(paragraph.closest('.story-whisper')||paragraph.querySelector('.typewriter-line'))return;
      const walker=document.createTreeWalker(paragraph,NodeFilter.SHOW_TEXT),nodes=[];
      while(walker.nextNode()){
        const node=walker.currentNode;
        if(node.textContent.trim()&&!node.parentElement.closest('.word-slot,tw-link,tw-hook,tw-expression,tw-enchantment,.sr-only'))nodes.push(node);
      }
      nodes.forEach(node=>{
        const fragment=document.createDocumentFragment();
        for(const sentence of node.textContent.match(/[^。！？；\n]+[。！？；]?|[。！？；\n]/g)||[]){
          const span=document.createElement('span');span.className='prose-fragment';span.style.setProperty('--ink-delay',Math.min(order++*110,660)+'ms');span.textContent=sentence;fragment.append(span);
        }
        node.replaceWith(fragment);
      });
    });
  }
  function setupTitle(page){
    if(!page.classList.contains('title-screen'))return;
    const caption=page.querySelector('[data-title-caption]'),defaultLine=caption.textContent;
    const show=button=>{caption.textContent=button?.dataset.titleLine||defaultLine;page.dataset.focus=button?.dataset.animal||'';};
    page.querySelectorAll('.title-portal').forEach(button=>{
      button.addEventListener('pointerenter',()=>show(button));button.addEventListener('focus',()=>show(button));
      button.addEventListener('pointerleave',()=>{if(document.activeElement!==button)show(null);});button.addEventListener('blur',()=>show(null));
    });
    const canvas=page.querySelector('.title-dust'),context=canvas.getContext('2d');if(!context)return;
    const motion=matchMedia('(prefers-reduced-motion: reduce)');let frame=0,width=1,height=1,last=0,clock=0,destroyed=false;
    const dots=Array.from({length:54},()=>({x:Math.random(),y:Math.random(),size:.4+Math.random()*1.1,speed:2+Math.random()*6,phase:Math.random()*Math.PI*2}));
    function draw(now){
      frame=0;if(destroyed)return;
      const delta=last?Math.min((now-last)/1000,.05):0;last=now;clock+=delta;context.clearRect(0,0,width,height);
      for(const dot of dots){if(!motion.matches)dot.y=(dot.y-dot.speed*delta/height+1)%1;const alpha=.16+(Math.sin(clock*.7+dot.phase)+1)*.16;context.fillStyle='rgba(255,255,255,'+alpha+')';context.beginPath();context.arc(dot.x*width,dot.y*height,dot.size,0,Math.PI*2);context.fill();}
      if(!motion.matches&&!document.hidden)frame=requestAnimationFrame(draw);
    }
    const pause=()=>{cancelAnimationFrame(frame);frame=0;last=0;};
    const resume=()=>{if(!destroyed&&!frame){last=0;frame=requestAnimationFrame(draw);}};
    const size=()=>{const rect=canvas.getBoundingClientRect(),ratio=Math.min(devicePixelRatio||1,2);width=Math.max(1,rect.width);height=Math.max(1,rect.height);canvas.width=Math.round(width*ratio);canvas.height=Math.round(height*ratio);context.setTransform(ratio,0,0,ratio,0,0);pause();resume();};
    const observer=new ResizeObserver(size);observer.observe(canvas);motion.addEventListener('change',size);size();
    page._pauseTitle=pause;page._resumeTitle=resume;page._stopTitle=()=>{destroyed=true;pause();observer.disconnect();motion.removeEventListener('change',size);};
  }
  function syncProgress(){
    document.querySelectorAll('[data-journal-total]').forEach(el=>el.textContent=saved.endings.length+'/'+validEndings.length);
    document.querySelectorAll('[data-role-count]').forEach(el=>{const count=saved.endings.filter(id=>id.startsWith(el.dataset.roleCount+'-')).length;el.textContent=count+'/2';el.classList.toggle('has-ending',count>0);});
    document.querySelectorAll('[data-entry]').forEach(el=>{const found=saved.endings.includes(el.dataset.entry);el.classList.toggle('is-discovered',found);el.querySelector('.entry-state').textContent=found?'已完成 / DISCOVERED':'尚未完成 / UNDISCOVERED';el.querySelector('.entry-copy').textContent=found?el.dataset.description:'走完这条路线后，这里会记下结局。';});
  }
  function complete(task,text){if(task.dataset.complete==='yes')return;task.dataset.complete='yes';task.classList.add('task-complete');const status=task.querySelector('[data-task-status]');if(status)status.textContent=text;task.querySelectorAll('[data-task-action]').forEach(b=>b.disabled=true);task.querySelectorAll('[data-task-next]').forEach(el=>{el.classList.remove('is-locked');el.removeAttribute('inert');el.removeAttribute('aria-hidden');});const meter=task.querySelector('.task-track span');if(meter)meter.style.width='100%';}
  function setupTask(task,page){
    const kind=task.dataset.task;let count=0;const goal=Number(task.dataset.goal||1);const status=task.querySelector('[data-task-status]'),track=task.querySelector('.task-track span');
    task.querySelectorAll('[data-task-next].is-locked').forEach(el=>{el.setAttribute('inert','');el.setAttribute('aria-hidden','true');});
    if(kind==='ram')task.querySelector('[data-task-action]').addEventListener('click',()=>{if(count>=goal)return;count++;task.dataset.value=String(count);status.textContent='獠牙撞击 · '+count+' / '+goal;if(track)track.style.width=count/goal*100+'%';sound('ram');artworkImpact(page);if(count===goal){complete(task,'撞了五下。你抬起头，灯光后面好像有一对獠牙。');revealGod(page);}});
    if(kind==='chew')task.querySelector('[data-task-action]').addEventListener('click',()=>{sound('chew');artworkImpact(page);complete(task,'咔嚓。奇怪的味道在嘴里散开。');});
    if(kind==='duel'){
      const targets=[...task.querySelectorAll('[data-duck-target]')];let previous=-1,hits=[0,0];
      targets.forEach((button,index)=>button.addEventListener('click',event=>{
        if(task.dataset.complete==='yes'||button.disabled)return;
        if(index===previous){status.textContent='它挡住了你。换一个方向，再试一次。';return;}
        previous=index;hits[index]++;count++;task.dataset.value=String(count);sound('grain');button.classList.add('is-hit');setTimeout(()=>button.classList.remove('is-hit'),160);
        const remaining=Math.max(0,3-hits[index]);button.querySelector('[data-target-life]').textContent=remaining===0?'对手已退下':'还需 '+remaining+' 次';
        const grain=task.querySelector('[data-grains]');grain.textContent=String(count);if(track)track.style.width=count/goal*100+'%';status.textContent=remaining===0?'它让开了。你又抢到一粒粮。':'抢到一粒。换个方向，再挤过去。';
        const rect=button.getBoundingClientRect();for(let i=0;i<5;i++){const dot=document.createElement('i');dot.className='crumb';dot.style.left=(event.clientX?event.clientX-rect.left:rect.width/2)+'px';dot.style.top=(event.clientY?event.clientY-rect.top:rect.height/2)+'px';dot.style.setProperty('--dx',(Math.random()*70-35)+'px');dot.style.setProperty('--dy',(-20-Math.random()*65)+'px');button.append(dot);setTimeout(()=>dot.remove(),800);}
        if(remaining===0)button.disabled=true;if(count>=goal)complete(task,'前面的鸭子退开了。你护住刚抢到的六粒粮。');
      }));
    }
    if(kind==='hold'){
      const button=task.querySelector('[data-task-action]'),duration=1800;let elapsed=0,started=0,frame=0,holding=false;
      const stop=()=>{if(!holding)return;elapsed=Math.min(duration,elapsed+performance.now()-started);holding=false;cancelAnimationFrame(frame);button.classList.remove('is-holding');page.querySelector('.artwork')?.classList.remove('is-steaming');if(elapsed<duration)status.textContent='再注视一会儿。巨神身旁的白雾还没有散尽。';};
      const tick=()=>{if(!holding)return;const value=Math.min(duration,elapsed+performance.now()-started);button.style.setProperty('--hold',String(value/duration));if(track)track.style.width=value/duration*100+'%';status.textContent='巨神正在喷出白雾 · '+Math.round(value/duration*100)+'%';if(value>=duration){elapsed=duration;stop();complete(task,'巨神喷出的白雾散开了。林间仍回荡着轰鸣。');return;}frame=requestAnimationFrame(tick);};
      const start=event=>{if(holding||task.dataset.complete==='yes')return;if(event.type==='pointerdown'&&event.button!==0)return;event.preventDefault();event.stopPropagation();started=performance.now();holding=true;button.classList.add('is-holding');page.querySelector('.artwork')?.classList.add('is-steaming');frame=requestAnimationFrame(tick);};
      button.addEventListener('pointerdown',start);button.addEventListener('contextmenu',event=>event.preventDefault());button.addEventListener('keydown',e=>{if([' ','Enter'].includes(e.key)&&!e.repeat)start(e);});page._stopHold=()=>{stop();cancelAnimationFrame(frame);};
    }
  }
  function setupCardTabs(page){
    page.querySelectorAll('.facts,.journal-grid').forEach((group,index)=>{
      const cards=[...group.children];if(cards.length<2)return;
      const tabs=document.createElement('nav');tabs.className='card-tabs';tabs.setAttribute('aria-label',group.classList.contains('facts')?'切换资料':'切换角色手记');
      group.classList.add('has-card-tabs');
      cards.forEach((card,i)=>{
        const button=document.createElement('button');button.type='button';button.textContent=card.dataset.cardLabel||card.querySelector('strong')?.textContent||String(i+1);
        card.id='scene-card-'+index+'-'+i;button.setAttribute('aria-controls',card.id);button.setAttribute('aria-pressed',String(i===0));card.classList.toggle('is-active',i===0);
        button.addEventListener('click',()=>{cards.forEach((item,j)=>item.classList.toggle('is-active',i===j));[...tabs.children].forEach((item,j)=>item.setAttribute('aria-pressed',String(i===j)));});tabs.append(button);
      });
      group.before(tabs);
    });
  }
  function reserveCardHeight(page){
    page.querySelectorAll('.has-card-tabs').forEach(group=>{
      group.style.minHeight='0';
      if(getComputedStyle(group.previousElementSibling).display==='none')return;
      const cards=[...group.children],selected=cards.find(card=>card.classList.contains('is-active'))||cards[0];let height=0;
      cards.forEach(card=>{cards.forEach(item=>item.classList.toggle('is-active',item===card));height=Math.max(height,group.getBoundingClientRect().height/Number(page.style.zoom||1));});
      cards.forEach(card=>card.classList.toggle('is-active',card===selected));group.style.minHeight=Math.ceil(height)+'px';
    });
  }
  function fitPage(page){
    if(!page?.isConnected)return;
    // All measurements and sizing finish synchronously before the next paint.
    const setScale=value=>{page.style.zoom=String(value);page.style.width='100%';};
    setScale(1);page.classList.remove('fit-compact');
    const height=document.documentElement.clientHeight,bottom=parseFloat(getComputedStyle(document.querySelector('tw-story')).paddingBottom)||12;
    const available=Math.max(1,height-page.getBoundingClientRect().top-bottom-1);
    page.style.setProperty('--selection-height',available+'px');
    const wide=matchMedia('(min-width:701px) and (max-height:600px)').matches;
    const artwork=page.querySelector('.artwork'),duel=page.querySelector('.duel');
    const hasArtwork=artwork&&getComputedStyle(artwork).display!=='none';
    const maximum=wide?Math.max(60,available-55):Math.min(height*(page.classList.contains('data-ending')?.3:page.classList.contains('ending')?.4:.52),680);
    const minimum=wide?60:Math.min(110,Math.max(64,height*.12));
    const sizeArt=()=>{
      if(hasArtwork)page.style.setProperty('--art-height',maximum+'px');
      if(duel)page.style.setProperty('--duel-height',Math.min(height*.28,260)+'px');
      reserveCardHeight(page);
      const excess=page.getBoundingClientRect().height-available;
      if(excess>0){
        if(wide&&hasArtwork){page.style.setProperty('--art-height',Math.max(minimum,maximum-excess)+'px');}
        else if(hasArtwork)page.style.setProperty('--art-height',Math.max(minimum,maximum-excess-1)+'px');
        else if(duel){const image=duel.querySelector('img');page.style.setProperty('--duel-height',Math.max(64,image.getBoundingClientRect().height-excess-1)+'px');}
      }
    };
    sizeArt();
    if(page.getBoundingClientRect().height>available){page.classList.add('fit-compact');sizeArt();}
    // Small windows still show the complete content: fit it as a unit instead of clipping it.
    if(page.getBoundingClientRect().height>available){
      let low=.2,high=1,best=.2;
      for(let i=0;i<11;i++){const scale=(low+high)/2;setScale(scale);reserveCardHeight(page);if(page.getBoundingClientRect().height<=available){best=scale;low=scale;}else high=scale;}
      setScale(best);reserveCardHeight(page);
    }
    page.dataset.fitScale=page.style.zoom;
  }
  function setup(){
    const pages=[...document.querySelectorAll('tw-passage .page')];const page=pages[pages.length-1];if(!page||page===lastPage)return false;
    lastPage?._stopHold?.();lastPage?._stopTitle?.();lastPage=page;resetPreview();wanted=page.dataset.sound||'';
    document.documentElement.dataset.role=['pig','cat','duck'].find(role=>page.classList.contains('role-'+role))||'selection';
    document.documentElement.dataset.view=page.classList.contains('title-screen')?'title':'story';
    const ending=page.dataset.ending;if(validEndings.includes(ending)&&!saved.endings.includes(ending)){saved.endings.push(ending);persist();}
    syncProgress();syncAudio();
    page.querySelectorAll('[data-task]').forEach(task=>setupTask(task,page));
    setupCardTabs(page);setupSceneEffects(page);setupTextEffects(page);fitPage(page);setupTitle(page);
    page.querySelectorAll('.artwork[data-advance]').forEach(art=>{const next=page.querySelector('.actions tw-link');if(!next)return;art.classList.add('is-clickable');art.tabIndex=0;art.setAttribute('role','button');art.setAttribute('aria-label','继续故事');const advance=()=>{if(page!==lastPage)return;next.click();};art.addEventListener('click',advance);art.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();advance();}});});
    window.scrollTo({top:0,behavior:'instant'});
    const heading=page.querySelector('h1');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}
    return true;
  }
  document.addEventListener('pointerdown',()=>{if(!unlocked){unlocked=true;syncAudio();}},{capture:true});
  document.addEventListener('keydown',event=>{if(!unlocked){unlocked=true;syncAudio();}if(['Tab','Escape'].includes(event.key))lastPage?._stopHold?.();},{capture:true});
  document.addEventListener('keyup',event=>{if([' ','Enter'].includes(event.key))lastPage?._stopHold?.();},{capture:true});
  document.addEventListener('pointerup',()=>lastPage?._stopHold?.(),{capture:true});
  document.addEventListener('pointercancel',()=>lastPage?._stopHold?.(),{capture:true});
  window.addEventListener('blur',()=>lastPage?._stopHold?.());
  document.addEventListener('click',event=>{
    if(event.target.closest('[data-start-listening]')){unlocked=true;saved.muted=false;persist();if(ambient.error)ambient.load();syncAudio();return;}
    const toggle=event.target.closest('[data-audio-toggle]');if(toggle){saved.muted=!saved.muted;persist();if(saved.muted){resetPreview();stopSceneSounds();}else if(lastPage)startSceneSounds(lastPage);syncAudio();return;}
    const call=event.target.closest('[data-animal]');if(call)playCall(call.dataset.animal,call);
  });
  document.addEventListener('error',event=>{const img=event.target;if(img.tagName!=='IMG'||img.dataset.failed)return;img.dataset.failed='yes';const parent=img.closest('.artwork');if(parent){const note=document.createElement('div');note.className='load-error';note.textContent='图片暂时没加载出来';const sub=document.createElement('small');sub.textContent='请检查网络连接。你也可以用下方按钮继续。';note.append(sub);parent.append(note);}},true);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){ambient.pause();resetPreview();stopSceneSounds();lastPage?._stopHold?.();lastPage?._pauseTitle?.();}else{syncAudio();lastPage?._resumeTitle?.();}});
  window.addEventListener('pagehide',()=>{ambient.pause();resetPreview();stopSceneSounds();lastPage?._stopHold?.();lastPage?._pauseTitle?.();});
  window.addEventListener('pageshow',()=>{if(lastPage){syncAudio();lastPage._resumeTitle?.();}});
  new MutationObserver(records=>{
    if(setup())return;
    // Counter updates use reserved space; only expanded story content needs a new fit.
    if(records.some(record=>lastPage?.contains(record.target)&&!record.target.closest?.('[data-task], [data-role-count], [data-journal-total], .card-tabs, .story-whisper, .typewriter-line, .word-slot, .title-scene-caption, .title-listen')))fitPage(lastPage);
  }).observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('resize',()=>fitPage(lastPage));
  setup();
})();
