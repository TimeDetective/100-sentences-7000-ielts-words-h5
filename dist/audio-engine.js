'use strict';
// Prefer prepared neural recordings. Device synthesis is an explicit alternative.
(()=>{
 const normalize=t=>String(t).trim().replace(/\s+/g,' ').toLowerCase();
 const novelty=/\b(Albert|Bad News|Bahh|Bells|Boing|Bubbles|Cellos|Wobble|Fred|Good News|Jester|Junior|Organ|Trinoids|Whisper|Zarvox|Hysterical|Princess|Superstar|Eddy|Flo|Grandma|Grandpa|Reed|Rocko|Shelley|Sandy|Ralph)\b/i;
 function scoreVoice(v){const name=`${v.name} ${v.voiceURI}`;let score=10;if(/neural|natural|premium|enhanced|siri/i.test(name))score+=100;if(/Samantha|Serena|Stephanie|Ava|Zoe|Oliver|Daniel|Alex/i.test(name))score+=35;if(/Google|Microsoft/i.test(name))score+=25;if(v.default)score+=2;return score;}
 function selectDeviceVoice(voices,lang){return voices.filter(v=>v.lang.replace(/_/g,'-').toLowerCase()===lang.toLowerCase()&&!novelty.test(v.name)).sort((a,b)=>scoreVoice(b)-scoreVoice(a))[0]||null;}
 class Narrator{
  constructor({onState,onWord,onError}){this.onState=onState;this.onWord=onWord;this.onError=onError;this.active=null;this.serial=0;this.raf=0;}
  emit(){const a=this.active;this.onState(a?{text:a.text,lang:a.lang,paused:a.paused,loading:a.loading,kind:a.kind,mode:a.mode,voice:a.voice}:null);}
  clearWord(){this.onWord(null);}
  stop(){this.serial++;const a=this.active;this.active=null;cancelAnimationFrame(this.raf);this.clearWord();if(a?.audio){clearTimeout(a.timer);a.audio.pause();a.audio.removeAttribute('src');a.audio.load();}if(a?.utterance&&'speechSynthesis'in window)window.speechSynthesis.cancel();if(a)this.emit();}
  fail(a,message){if(this.active!==a)return;this.stop();this.onError(message);}
  async voices(){const engine=window.speechSynthesis;if(engine.getVoices().length)return engine.getVoices();return new Promise(resolve=>{let timer;const done=()=>{engine.removeEventListener('voiceschanged',ready);clearTimeout(timer);resolve(engine.getVoices());};const ready=()=>{if(engine.getVoices().length)done();};engine.addEventListener('voiceschanged',ready);timer=setTimeout(done,1600);ready();});}
  play(text,lang,{slow=false,mode='natural'}={}){
   const a=this.active;
   if(a&&a.text===text&&a.lang===lang&&a.mode===mode&&a.slow===slow){
    if(a.loading){this.stop();return;}
    if(a.audio){if(a.paused){a.loading=true;this.emit();a.audio.play().catch(()=>this.fail(a,'暂时无法继续播放，请再点一次。'));}else{a.audio.pause();a.paused=true;this.clearWord();this.emit();}}
    else if(a.utterance){if(a.paused){window.speechSynthesis.resume();a.paused=false;}else{window.speechSynthesis.pause();a.paused=true;this.clearWord();}this.emit();}
    return;
   }
   this.stop();const token=this.serial;const record={text,lang,slow,mode,paused:false,loading:true,token};this.active=record;this.emit();
   if(mode==='device'){this.playDevice(record);return;}
   const entry=window.NARRATION?.clips[normalize(text)]?.[lang];const clip=(slow&&entry?.slow)||entry?.natural;
   if(!clip){this.fail(record,'这段自然语音还没有准备好，可在“我的”中选择设备朗读。');return;}
   const audio=new Audio();record.audio=audio;record.kind=clip.kind;record.voice=clip.voice;audio.preload='auto';audio.src=new URL(clip.src,document.baseURI).href;
   // Sentence slow versions are synthesized separately; word slowdown preserves pitch.
   audio.playbackRate=slow&&!entry.slow?0.85:1;
   if('preservesPitch'in audio)audio.preservesPitch=true;
   const matches=[...text.matchAll(/[a-zA-Z]+(?:'[a-zA-Z]+)?/g)].map(m=>m[0].toLowerCase());let cursor=0;
   const timings=(clip.words||[]).flatMap(w=>{const tokens=w.text.toLowerCase().match(/[a-z]+(?:'[a-z]+)?/g)||[];const found=[];for(const token of tokens){const index=matches.indexOf(token,cursor);if(index<0)continue;cursor=index+1;found.push({...w,index});}return found;});let previous=-2;
   const tick=()=>{if(this.active!==record||audio.paused)return;let index=-1;for(const w of timings){if(audio.currentTime>=w.start&&audio.currentTime<=w.end+.06){index=w.index;break;}}
    if(index!==previous){previous=index;this.onWord(index<0?null:{text,lang,index});}this.raf=requestAnimationFrame(tick);};
   audio.addEventListener('playing',()=>{if(this.active!==record)return;clearTimeout(record.timer);record.loading=false;record.paused=false;this.emit();cancelAnimationFrame(this.raf);tick();});
   audio.addEventListener('pause',()=>{if(this.active!==record||audio.ended)return;record.loading=false;record.paused=true;this.clearWord();this.emit();});
   audio.addEventListener('waiting',()=>{if(this.active!==record||audio.paused)return;record.loading=true;this.emit();});
   audio.addEventListener('ended',()=>{if(this.active!==record)return;clearTimeout(record.timer);this.active=null;cancelAnimationFrame(this.raf);this.clearWord();this.emit();});
   audio.addEventListener('error',()=>this.fail(record,'自然语音加载失败，请检查网络后重试；也可在“我的”中切换设备朗读。'));
   record.timer=setTimeout(()=>this.fail(record,'声音加载有些慢，请检查网络后重试。'),15000);
   const p=audio.play();if(p)p.catch(e=>{if(this.active!==record)return;this.fail(record,e.name==='NotAllowedError'?'浏览器尚未允许播放，请再点一次朗读按钮。':'自然语音暂时无法播放，请再试一次。');});
  }
  async playDevice(a){if(!('speechSynthesis'in window)){this.fail(a,'当前浏览器不支持设备朗读，请选择自然朗读。');return;}
   const voices=await this.voices();if(this.active!==a||a.token!==this.serial)return;const voice=selectDeviceVoice(voices,a.lang);if(!voice){this.fail(a,`没有找到清晰的${a.lang==='en-GB'?'英音':'美音'}设备声音，请使用自然朗读。`);return;}
   const u=new SpeechSynthesisUtterance(a.text);a.utterance=u;a.voice=voice.name;u.voice=voice;u.lang=a.lang;u.rate=a.slow?.82:1;u.pitch=1;u.volume=1;
   u.onstart=()=>{if(this.active!==a)return;a.loading=false;this.emit();};
   u.onend=()=>{if(this.active!==a)return;this.active=null;this.clearWord();this.emit();};
   u.onerror=e=>{if(this.active!==a)return;this.active=null;this.clearWord();this.emit();if(!['canceled','interrupted'].includes(e.error))this.onError('设备朗读暂时不可用，建议切换自然朗读。');};
   window.speechSynthesis.speak(u);
  }
 }
 window.Narrator=Narrator;window.selectDeviceVoice=selectDeviceVoice;
})();
