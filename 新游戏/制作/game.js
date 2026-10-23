(function(){
  'use strict';
  const storageKey='they-once-existed-new-gift-v1';
  let saved={endings:[],muted:false};
  try{const value=JSON.parse(localStorage.getItem(storageKey)||'{}');if(value&&typeof value==='object')saved={endings:Array.isArray(value.endings)?value.endings.filter(x=>typeof x==='string'):[],muted:value.muted===true};}catch(_){}
  const persist=()=>{try{localStorage.setItem(storageKey,JSON.stringify(saved));}catch(_){}};
  // 三条路线按章节播放 GitHub 原始文件直链。同一音频跨页面继续播放，切换章节时停止上一段。
  const sceneAudio={
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
  function resetPreview(){preview.pause();if(previewButton)previewButton.classList.remove('is-playing');previewButton=null;clearTimeout(previewTimer);}
  function syncAudio(){
    document.querySelectorAll('[data-audio-toggle]').forEach(b=>{b.textContent=saved.muted?'声音：关':'声音：开';b.classList.toggle('is-off',saved.muted);b.setAttribute('aria-pressed',String(!saved.muted));b.setAttribute('aria-label',saved.muted?'打开声音':'关闭声音');});
    ambient.muted=saved.muted;preview.muted=saved.muted;
    if(saved.muted||!unlocked){ambient.pause();return;}
    const source=sceneAudio[wanted]||'';
    if(!source){ambient.pause();active='';ambient.removeAttribute('src');ambient.load();return;}
    if(active!==source){ambient.pause();ambient.src=safeURL(source);active=source;}
    if(ambient.paused)ambient.play().catch(()=>{});
  }
  function toast(message){document.querySelector('.sound-toast')?.remove();clearTimeout(toastTimer);const el=document.createElement('div');el.className='sound-toast';el.setAttribute('role','status');el.textContent=message;document.body.append(el);toastTimer=setTimeout(()=>el.remove(),1900);}
  function playCall(animal,button){if(saved.muted){toast('声音已关闭');return;}const source=calls[animal];if(!source)return;resetPreview();previewButton=button;button.classList.add('is-playing');preview.src=safeURL(source);ambient.volume=.2;preview.play().then(()=>{previewTimer=setTimeout(resetPreview,4500);}).catch(()=>resetPreview());}
  preview.addEventListener('ended',()=>{resetPreview();ambient.volume=.52;});preview.addEventListener('pause',()=>{ambient.volume=.52;});preview.addEventListener('error',resetPreview);
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
  function syncProgress(){
    document.querySelectorAll('[data-journal-total]').forEach(el=>el.textContent=saved.endings.length+'/9');
    document.querySelectorAll('[data-role-count]').forEach(el=>{const count=saved.endings.filter(id=>id.startsWith(el.dataset.roleCount+'-')).length;el.textContent=count+'/3';el.classList.toggle('has-ending',count>0);});
    document.querySelectorAll('[data-entry]').forEach(el=>{const found=saved.endings.includes(el.dataset.entry);el.classList.toggle('is-discovered',found);el.querySelector('.entry-state').textContent=found?'已抵达 / DISCOVERED':'尚未抵达 / UNDISCOVERED';el.querySelector('.entry-copy').textContent=found?el.dataset.description:'选择另一条路，听见另一个答案。';});
  }
  function complete(task,text){if(task.dataset.complete==='yes')return;task.dataset.complete='yes';task.classList.add('task-complete');const status=task.querySelector('[data-task-status]');if(status)status.textContent=text;task.querySelectorAll('[data-task-action]').forEach(b=>b.disabled=true);task.querySelectorAll('[data-task-next]').forEach(el=>{el.classList.remove('is-locked');el.removeAttribute('inert');el.removeAttribute('aria-hidden');});const meter=task.querySelector('.task-track span');if(meter)meter.style.width='100%';}
  function setupTask(task,page){
    const kind=task.dataset.task;let count=0;const goal=Number(task.dataset.goal||1);const status=task.querySelector('[data-task-status]'),track=task.querySelector('.task-track span');
    task.querySelectorAll('[data-task-next].is-locked').forEach(el=>{el.setAttribute('inert','');el.setAttribute('aria-hidden','true');});
    if(kind==='ram')task.querySelector('[data-task-action]').addEventListener('click',()=>{if(count>=goal)return;count++;task.dataset.value=String(count);status.textContent='獠牙撞击 · '+count+' / '+goal;if(track)track.style.width=count/goal*100+'%';sound('ram');artworkImpact(page);if(count===goal){complete(task,'第五次撞击落下。它的轮廓，开始改变。');revealGod(page);}});
    if(kind==='chew')task.querySelector('[data-task-action]').addEventListener('click',()=>{sound('chew');artworkImpact(page);complete(task,'咔嚓。奇怪的味道在嘴里散开。');});
    if(kind==='signal')task.querySelector('[data-task-action]').addEventListener('click',()=>{if(count>=goal)return;count++;task.dataset.value=String(count);status.textContent='有人在听 · '+count+' / '+goal;if(track)track.style.width=count/goal*100+'%';if(page.classList.contains('role-pig'))playCall('pig',task.querySelector('[data-task-action]'));else sound('grain');if(count===goal)complete(task,page.classList.contains('role-pig')?'林中传来了回应。那些脚步，正在向你靠近。':'门外的脚步停下了。有人看见了你留下的东西。');});
    if(kind==='duel'){
      const targets=[...task.querySelectorAll('[data-duck-target]')];let previous=-1,hits=[0,0];
      targets.forEach((button,index)=>button.addEventListener('click',event=>{
        if(task.dataset.complete==='yes'||button.disabled)return;
        if(index===previous){status.textContent='它挡住了你。换一个方向，再试一次。';return;}
        previous=index;hits[index]++;count++;task.dataset.value=String(count);sound('grain');button.classList.add('is-hit');setTimeout(()=>button.classList.remove('is-hit'),160);
        const remaining=Math.max(0,3-hits[index]);button.querySelector('[data-target-life]').textContent=remaining===0?'对手已退下':'还需 '+remaining+' 次';
        const grain=task.querySelector('[data-grains]');grain.textContent=String(count);if(track)track.style.width=count/goal*100+'%';status.textContent=remaining===0?'对手已淘汰。圣餐 +1。':'你抢到一粒粮食。换一个方向继续争夺。';
        const rect=button.getBoundingClientRect();for(let i=0;i<5;i++){const dot=document.createElement('i');dot.className='crumb';dot.style.left=(event.clientX?event.clientX-rect.left:rect.width/2)+'px';dot.style.top=(event.clientY?event.clientY-rect.top:rect.height/2)+'px';dot.style.setProperty('--dx',(Math.random()*70-35)+'px');dot.style.setProperty('--dy',(-20-Math.random()*65)+'px');button.append(dot);setTimeout(()=>dot.remove(),800);}
        if(remaining===0)button.disabled=true;if(count>=goal)complete(task,'对手已退下。你终于获得了「被挑选」的资格。');
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
    lastPage?._stopHold?.();lastPage=page;resetPreview();wanted=page.dataset.sound||'';
    document.documentElement.dataset.role=['pig','cat','duck'].find(role=>page.classList.contains('role-'+role))||'selection';
    const ending=page.dataset.ending;if(ending&&!saved.endings.includes(ending)){saved.endings.push(ending);persist();}
    syncProgress();syncAudio();
    page.querySelectorAll('[data-task]').forEach(task=>setupTask(task,page));
    setupCardTabs(page);setupSceneEffects(page);setupTextEffects(page);fitPage(page);
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
    const toggle=event.target.closest('[data-audio-toggle]');if(toggle){saved.muted=!saved.muted;persist();if(saved.muted){resetPreview();stopSceneSounds();}else if(lastPage)startSceneSounds(lastPage);syncAudio();return;}
    const call=event.target.closest('[data-animal]');if(call)playCall(call.dataset.animal,call);
  });
  document.addEventListener('error',event=>{const img=event.target;if(img.tagName!=='IMG'||img.dataset.failed)return;img.dataset.failed='yes';const parent=img.closest('.artwork');if(parent){const note=document.createElement('div');note.className='load-error';note.textContent='画面暂时没有找到';const sub=document.createElement('small');sub.textContent='请保留 HTML 旁的素材文件夹，仍可使用下方按钮继续。';note.append(sub);parent.append(note);}},true);
  document.addEventListener('visibilitychange',()=>{if(document.hidden){ambient.pause();resetPreview();stopSceneSounds();lastPage?._stopHold?.();}else syncAudio();});
  window.addEventListener('pagehide',()=>{ambient.pause();resetPreview();stopSceneSounds();lastPage?._stopHold?.();});
  new MutationObserver(records=>{
    if(setup())return;
    // Counter updates use reserved space; only expanded story content needs a new fit.
    if(records.some(record=>lastPage?.contains(record.target)&&!record.target.closest?.('[data-task], [data-role-count], [data-journal-total], .card-tabs, .story-whisper, .typewriter-line, .word-slot')))fitPage(lastPage);
  }).observe(document.documentElement,{subtree:true,childList:true});
  window.addEventListener('resize',()=>fitPage(lastPage));
  setup();
})();
