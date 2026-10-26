// Streamlit 1.50 embeds this trusted component with same-origin access.
// All DOM additions and listeners are removed on close or a page rerun.
function launchTour() {
  const doc = window.parent.document, win = window.parent;
  if (win.modularTourCleanup) win.modularTourCleanup();
  const steps = tourSteps.filter(([selector]) => {
    const target=doc.querySelector(selector);
    return target && target.getClientRects().length && target.getBoundingClientRect().height > 0;
  });
  if (!steps.length) return;
  const origin = doc.activeElement;
  const root = doc.createElement('div');
  root.id = 'modular-tour';
  const style = doc.createElement('style');
  style.textContent = `
    #modular-tour {position:fixed;inset:0;z-index:1000000;pointer-events:none;font-family:Inter,system-ui,sans-serif}
    #modular-tour .shade {position:fixed;background:rgba(15,23,42,.5);backdrop-filter:blur(5px);pointer-events:auto}
    #modular-tour .spot {position:fixed;border:2px solid #818cf8;border-radius:12px;box-shadow:0 0 0 4px #4f46e533;pointer-events:auto}
    #modular-tour .dialog {position:fixed;box-sizing:border-box;width:340px;max-width:calc(100vw - 24px);padding:20px;border-radius:16px;background:#fff;color:#1f2937;border:1px solid #c7d2fe;box-shadow:0 16px 64px #0005;pointer-events:auto}
    #modular-tour h2 {font-size:19px;margin:8px 0;color:inherit}
    #modular-tour p {font-size:14px;line-height:1.6;margin:10px 0 18px;color:inherit}
    #modular-tour small {font-size:12px;color:#6366f1}
    #modular-tour .actions {display:flex;align-items:center;gap:8px}
    #modular-tour button {font:inherit;font-size:13px;border:1px solid #c7d2fe;padding:8px 12px;border-radius:8px;background:transparent;color:inherit;cursor:pointer}
    #modular-tour button:last-child {background:#4f46e5;color:white;border-color:#4f46e5;margin-left:auto}
    #modular-tour button:disabled {opacity:.4;cursor:default}
    #modular-tour button:focus-visible {outline:3px solid #14b8a6;outline-offset:2px}
  `;
  root.append(style);
  const shades = Array.from({length:4}, () => {const el=doc.createElement('div');el.className='shade';root.append(el);return el;});
  const spot=doc.createElement('div');spot.className='spot';root.append(spot);
  const dialog=doc.createElement('section');dialog.className='dialog';dialog.setAttribute('role','dialog');dialog.setAttribute('aria-modal','true');dialog.setAttribute('aria-labelledby','tour-title');
  dialog.innerHTML='<small aria-live="polite"></small><h2 id="tour-title"></h2><p></p><div class="actions"><button>Skip</button><button>Back</button><button>Next</button></div>';
  root.append(dialog);doc.body.append(root);
  const [skip,back,next]=dialog.querySelectorAll('button');
  let index=0, frame=0, closed=false;
  function rect(el,x,y,w,h) {Object.assign(el.style,{left:x+'px',top:y+'px',width:Math.max(0,w)+'px',height:Math.max(0,h)+'px'});}
  function layout() {
    if(closed)return;
    const target=doc.querySelector(steps[index][0]);if(!target){close();return;}
    const r=target.getBoundingClientRect(), W=win.innerWidth,H=win.innerHeight;
    const l=Math.max(4,r.left-6),t=Math.max(4,r.top-6),right=Math.min(W-4,r.right+6),bottom=Math.min(H-4,r.bottom+6);
    rect(shades[0],0,0,W,t);rect(shades[1],0,bottom,W,H-bottom);rect(shades[2],0,t,l,bottom-t);rect(shades[3],right,t,W-right,bottom-t);rect(spot,l,t,right-l,bottom-t);
    const dw=dialog.offsetWidth,dh=dialog.offsetHeight;
    let x=right+14,y=t;
    if(x+dw>W-12){x=l-dw-14;}
    if(x<12){x=Math.max(12,Math.min(l,W-dw-12));y=bottom+14;if(y+dh>H-12)y=t-dh-14;}
    dialog.style.left=Math.max(12,Math.min(x,W-dw-12))+'px';dialog.style.top=Math.max(12,Math.min(y,H-dh-12))+'px';
  }
  function show() {
    dialog.querySelector('small').textContent=`STEP ${index+1} OF ${steps.length}`;
    dialog.querySelector('h2').textContent=steps[index][1];dialog.querySelector('p').textContent=steps[index][2];
    back.disabled=index===0;next.textContent=index===steps.length-1?'Finish':'Next';
    const dark=win.getComputedStyle(doc.querySelector('.stApp')).backgroundColor==='rgb(17, 24, 39)';
    dialog.style.background=dark?'#1f2937':'#ffffff';dialog.style.color=dark?'#e5e7eb':'#1f2937';
    doc.querySelector(steps[index][0]).scrollIntoView({behavior:'instant',block:'center',inline:'nearest'});
    layout();cancelAnimationFrame(frame);frame=requestAnimationFrame(layout);next.focus({preventScroll:true});
  }
  function close(){if(closed)return;closed=true;cancelAnimationFrame(frame);observer.disconnect();doc.removeEventListener('keydown',keys,true);doc.removeEventListener('scroll',layout,true);win.removeEventListener('resize',layout);root.remove();delete win.modularTourCleanup;const trigger=doc.querySelector('.st-key-start_tour button');(trigger||origin)?.focus({preventScroll:true});}
  function keys(e){if(e.key==='Escape'){e.preventDefault();close();}if(e.key==='Tab'){const buttons=[...dialog.querySelectorAll('button')].filter(b=>!b.disabled);let n=buttons.indexOf(doc.activeElement);e.preventDefault();buttons[(n+(e.shiftKey?-1:1)+buttons.length)%buttons.length].focus();}}
  skip.onclick=close;back.onclick=()=>{if(index>0){index--;show();}};next.onclick=()=>{if(index===steps.length-1)close();else{index++;show();}};
  const host=window.frameElement;
  const observer=new MutationObserver(()=>{if(!host.isConnected)close();});observer.observe(doc.body,{childList:true,subtree:true});
  win.modularTourCleanup=close;doc.addEventListener('keydown',keys,true);doc.addEventListener('scroll',layout,true);win.addEventListener('resize',layout);show();
}
(() => {
  const win=window.parent, doc=win.document;
  if(win.modularTourTriggerCleanup)win.modularTourTriggerCleanup();
  const start=(event)=>{if(!event.target.closest('.st-key-start_tour button'))return;event.preventDefault();event.stopImmediatePropagation();launchTour();};
  doc.addEventListener('click',start,true);
  win.modularTourTriggerCleanup=()=>doc.removeEventListener('click',start,true);
})();
