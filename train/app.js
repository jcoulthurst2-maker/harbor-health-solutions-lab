(()=>{
const LAB=window.LAB_SCENARIOS;
const KEY='solutions-lab-v2-runtime';
const phases=['DISCOVER','FRAME','REALITY','DIAGNOSE','DESIGN','ACT','OBSERVE','IMPROVE'];
const mentorStage={
'OBSERVE + ASSIST':'The mentor narrates attention, demonstrates how to structure the work, and teaches new technical concepts just in time.',
'GUIDED':'You choose the path. The mentor asks questions, challenges assumptions, and avoids prescribing steps.',
'CO-LEAD':'You frame the engagement and propose the intervention. The mentor tests tradeoffs and evidence.',
'LEAD':'You own the path. The mentor reviews material decisions and blind spots.',
'INDEPENDENT':'Minimal support. Consultation is available, but the work is yours.',
'ASSESSMENT':'No teaching during primary execution. Professional review follows the work.'
};
const mentorPrompt={
DISCOVER:'What decision is the organization actually trying to make? Do not confuse the loudest complaint with the problem.',
FRAME:'Write the problem in a way that can be tested. What is in scope, what is not, and what outcome matters?',
REALITY:'Which sources are claims, which are observations, and which can falsify your current story?',
DIAGNOSE:'What mechanism best explains the evidence? Name the strongest alternative explanation too.',
DESIGN:'Generate more than one option. Which tradeoffs matter most here, not in an abstract architecture review?',
ACT:'Choose the smallest intervention that can create evidence or value without creating unnecessary irreversible risk.',
OBSERVE:'What changed after the intervention? Do not grade your own idea on intent—look at reality.',
IMPROVE:'What should persist, what should change, and what did this engagement teach that transfers elsewhere?'
};
let S={week:1,maxUnlocked:1,view:'engagement',phase:0,weekState:{},ledger:{},mentorOverride:null};
try{S={...S,...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch{}
const save=()=>localStorage.setItem(KEY,JSON.stringify(S));
const qs=s=>document.querySelector(s), qsa=s=>[...document.querySelectorAll(s)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const toast=m=>{const t=qs('#toast');t.textContent=m;t.classList.add('on');setTimeout(()=>t.classList.remove('on'),2200)};
function W(n=S.week){return LAB.weeks.find(x=>x.w===n)}
function org(w=W()){return LAB.organizations[w.org]}
function ws(n=S.week){if(!S.weekState[n])S.weekState[n]={seen:[],notes:'',frame:'',hypothesis:'',disproof:'',next:'',decisions:[],proof:false,phase:0,completed:false,workbench:''};return S.weekState[n]}
function stageText(w=W()){return mentorStage[w.stage]||mentorStage['GUIDED']}
function renderChrome(){
 const w=W(),o=org(w),st=ws();
 qs('#currentOrg').textContent=o.name;
 qs('#currentTitle').textContent=w.title;
 qs('#currentSummary').textContent=w.situation;
 qs('#weekCount').innerHTML=`WEEK ${String(w.w).padStart(2,'0')} <small>/ 26</small>`;
 qs('#progressFill').style.width=`${Math.max(3,(S.maxUnlocked/26)*100)}%`;
 qs('#mentorCopy').textContent=stageText(w);
 qs('#topPhase').textContent=`${w.stage} · ${phases[st.phase||0]}`;
 qsa('[data-view]').forEach(b=>b.classList.toggle('on',b.dataset.view===S.view));
 qsa('.view').forEach(v=>v.classList.toggle('on',v.id===S.view));
}
function renderEngagement(){
 const w=W(),o=org(w),st=ws(),locked=w.w>S.maxUnlocked;
 qs('#engagement').innerHTML=`
 <div class="hero"><div><div class="eyebrow">ENGAGEMENT ${String(w.w).padStart(2,'0')} · ${esc(w.stage)} · ${esc(w.region)}</div>
 <h1>${esc(w.title)}</h1><p>${esc(w.situation)}</p></div>
 <aside class="hero-meta"><div class="kv"><span>Organization</span><span>${esc(o.name)}</span></div><div class="kv"><span>Industry</span><span>${esc(o.industry)}</span></div><div class="kv"><span>HQ</span><span>${esc(o.hq)}</span></div><div class="kv"><span>Workbench</span><span>${esc(w.workbench)}</span></div><div class="kv"><span>Status</span><span>${locked?'PREVIEW':st.completed?'COMPLETE':'ACTIVE'}</span></div></aside></div>
 <div class="phases">${phases.map((p,i)=>`<button data-phase="${i}" class="${i===(st.phase||0)?'on':''}" ${locked?'disabled':''}><small>${String(i+1).padStart(2,'0')}</small><b>${p}</b></button>`).join('')}</div>
 ${locked?renderLocked(w):renderWorkspace(w,o,st)} `;
 qsa('[data-phase]').forEach(b=>b.addEventListener('click',()=>{st.phase=+b.dataset.phase;save();renderEngagement()}));
 if(!locked)bindWorkspace(w,st);
}
function renderLocked(w){return `<section class="panel"><div class="panelhead"><span>FUTURE ENGAGEMENT PREVIEW</span><span>LOCKED</span></div><div class="panelbody"><h3>${esc(w.objective)}</h3><p style="color:var(--m);line-height:1.65">This engagement opens after the preceding mastery gate is completed. You can inspect the roadmap, but the operating evidence and workbench stay locked.</p><div class="gate"><b>WHY LOCK IT?</b><p>The apprenticeship is longitudinal. Later cases assume capability and consequences from earlier work rather than functioning as disconnected portfolio demos.</p></div></div></section>`}
function renderWorkspace(w,o,st){
 const phase=phases[st.phase||0];
 return `<div class="workspace">
 <section class="panel brief"><div class="panelhead"><span>ENGAGEMENT BRIEF</span><span>${phase}</span></div><div class="panelbody">
 <h3>${esc(w.objective)}</h3><p>${esc(o.summary)}</p><div class="label">ACTIVE PROFESSIONAL LENSES</div><div class="tags">${w.lenses.map(x=>`<span class="tag on">${esc(x)}</span>`).join('')}</div>
 <div class="mentor"><small>MASTER PRACTITIONER // ${esc(w.stage)}</small><p>${esc(mentorPrompt[phase])}</p></div>
 <div class="label" style="margin-top:20px">SKILLS / CONCEPTS THAT MAY APPEAR</div><div class="tags">${w.skills.map(x=>`<span class="tag">${esc(x)}</span>`).join('')}</div>
 <div class="gate"><b>MASTERY GATE</b><p>${esc(w.gate)}</p></div>
 </div></section>
 <section class="panel"><div class="tabs"><button class="on" data-tool="evidence">EVIDENCE</button><button data-tool="workbench">WORKBENCH</button><button data-tool="notes">FIELD NOTES</button><button data-tool="decision">DECISION LOG</button><button data-tool="review">REVIEW</button></div>
 ${renderEvidenceTool(w,st)}${renderWorkbench(w,st)}${renderNotes(st)}${renderDecision(st)}${renderReview(w,st)}
 </section></div>`
}
function renderEvidenceTool(w,st){return `<div class="tool on" id="tool-evidence"><div class="panelbody"><div class="label">AVAILABLE EVIDENCE · ATTENTION IS SCARCE</div><div class="evidence-grid">${w.evidence.map((e,i)=>`<button class="evidence ${st.seen.includes(i)?'seen':''}" data-evidence="${i}"><small>${esc(e[0])}</small><strong>${esc(e[0])}</strong><span>${esc(e[1])}</span></button>`).join('')}</div><div class="inspect" id="inspect"><h4>No source selected.</h4><p>Choose evidence because it resolves uncertainty, not because it is available.</p></div></div></div>`}
function starterFor(w){
 if(w.workbench==='sql')return `-- Start with the business question, then interrogate evidence.\nSELECT * FROM evidence LIMIT 10;`;
 if(w.workbench==='python')return `# Write a reproducible analysis.\n# The local Python chamber loads a small case dataset when available.\nprint("State the question before the code")`;
 if(w.workbench==='api')return `GET /v1/partner/events?limit=20\nAuthorization: Bearer <token>\n\n# Inspect status, headers, body, retries, and idempotency.`;
 if(w.workbench==='architecture')return `OPTION A:\n- components:\n- data flow:\n- failure behavior:\n- cost implications:\n\nOPTION B:\n- components:\n- data flow:\n- failure behavior:\n- cost implications:\n\nDECISION:\nTRADEOFFS:`;
 if(w.workbench==='ai')return `TASK BOUNDARY:\nINPUTS:\nTOOLS / RETRIEVAL:\nEVALUATION SET:\nFAILURE THRESHOLD:\nHUMAN AUTHORITY:\nMONITORING:\nCOST / LATENCY TARGET:`;
 if(w.workbench==='incident')return `CURRENT STATE:\nCUSTOMER IMPACT:\nKNOWN / UNKNOWN:\nCONTAINMENT ACTION:\nVERIFICATION:\nCOMMUNICATION:`;
 if(w.workbench==='experiment')return `HYPOTHESIS:\nALTERNATIVE EXPLANATION:\nTEST DESIGN:\nPRIMARY METRIC:\nGUARDRAIL METRIC:\nDECISION RULE:`;
 return `PROBLEM:\nOPTIONS:\nEVIDENCE:\nTRADEOFFS:\nDECISION:\nVERIFICATION:`
}
function renderWorkbench(w,st){return `<div class="tool" id="tool-workbench"><div class="panelhead"><span>${esc(w.workbench.toUpperCase())} WORKBENCH</span><span>PERFORMANCE EVIDENCE</span></div><textarea class="terminal" id="workbenchInput">${esc(st.workbench||starterFor(w))}</textarea><div class="actions"><button class="btn primary" id="runWorkbench">RUN / RECORD WORK</button><button class="btn" id="openSkill">OPEN SKILL CHAMBER</button><button class="btn" id="resetWorkbench">RESET</button></div><div class="output" id="workbenchOutput"><div class="empty">Working output appears here. The Lab records evidence of execution, not merely completion.</div></div></div>`}
function renderNotes(st){return `<div class="tool" id="tool-notes"><div class="field"><div class="label">FIELD NOTES</div><textarea id="notesInput" placeholder="Claims vs observations. Unknowns. Evidence hierarchy. Questions worth asking. Tradeoffs worth preserving.">${esc(st.notes)}</textarea></div></div>`}
function renderDecision(st){return `<div class="tool" id="tool-decision"><div class="field"><div class="decisiongrid"><div class="decision"><label>PROBLEM FRAME</label><textarea id="frame">${esc(st.frame)}</textarea></div><div class="decision"><label>CURRENT HYPOTHESIS</label><textarea id="hypothesis">${esc(st.hypothesis)}</textarea></div><div class="decision"><label>WHAT WOULD DISPROVE IT?</label><textarea id="disproof">${esc(st.disproof)}</textarea></div><div class="decision"><label>NEXT HIGHEST-VALUE ACTION</label><textarea id="next">${esc(st.next)}</textarea></div></div></div><div class="statusbar"><span class="status" id="decisionStatus">${st.decisions.length} decision record(s).</span><button class="btn primary" id="recordDecision">RECORD DECISION</button></div></div>`}
function renderReview(w,st){
 const ev=st.seen.length,dec=st.decisions.length,proof=st.proof;
 const ready=ev>=Math.min(2,w.evidence.length)&&dec>=1&&proof;
 return `<div class="tool" id="tool-review"><div class="panelbody"><div class="label">PROFESSIONAL REVIEW</div><div class="ledger"><article><div class="level">${ev?'OBSERVED':'PENDING'}</div><div><h3>Evidence discipline</h3><p>${ev} source(s) inspected. The standard is purposeful evidence selection, not opening everything.</p></div><div class="right status">${ev>=2?'READY':'MORE EVIDENCE'}</div></article><article><div class="level">${dec?'ASSISTED':'PENDING'}</div><div><h3>Decision discipline</h3><p>${dec} decision record(s) with frame, hypothesis, disproof condition, and next action.</p></div><div class="right status">${dec?'RECORDED':'MISSING'}</div></article><article><div class="level">${proof?'DEMONSTRATED':'PENDING'}</div><div><h3>Hands-on execution</h3><p>Workbench execution is required before technical capability can advance.</p></div><div class="right status">${proof?'EVIDENCE CAPTURED':'MISSING'}</div></article></div><div class="gate"><b>${ready?'GATE READY':'GATE NOT READY'}</b><p>${ready?'You have produced the minimum evidence chain. Complete the engagement to unlock the next week.':'Inspect evidence, record a falsifiable decision, and produce workbench evidence.'}</p></div><div class="actions" style="padding-left:0;border:0"><button class="btn primary" id="completeWeek" ${ready?'':'disabled'}>${st.completed?'ENGAGEMENT COMPLETE':'COMPLETE ENGAGEMENT'}</button><button class="btn" id="exportWeek">EXPORT EVIDENCE JSON</button></div></div></div>`
}
function bindWorkspace(w,st){
 qsa('[data-tool]').forEach(b=>b.addEventListener('click',()=>{qsa('[data-tool]').forEach(x=>x.classList.toggle('on',x===b));qsa('.tool').forEach(x=>x.classList.toggle('on',x.id===`tool-${b.dataset.tool}`))}));
 qsa('[data-evidence]').forEach(b=>b.addEventListener('click',()=>{const i=+b.dataset.evidence;if(!st.seen.includes(i))st.seen.push(i);save();const e=w.evidence[i];b.classList.add('seen');qs('#inspect').innerHTML=`<h4>${esc(e[0])}</h4><p>${esc(e[1])}</p><div class="mentor"><small>MENTOR QUESTION</small><p>What uncertainty did this source reduce? What does it still not prove?</p></div>`}));
 const notes=qs('#notesInput');notes?.addEventListener('input',()=>{st.notes=notes.value;save()});
 ['frame','hypothesis','disproof','next'].forEach(id=>qs(`#${id}`)?.addEventListener('input',e=>{st[id]=e.target.value;save()}));
 qs('#recordDecision')?.addEventListener('click',()=>{if(['frame','hypothesis','disproof','next'].some(k=>!st[k].trim()))return toast('Complete all four decision fields.');st.decisions.push({at:new Date().toISOString(),frame:st.frame,hypothesis:st.hypothesis,disproof:st.disproof,next:st.next,evidence:[...st.seen]});save();toast('Decision recorded.');renderEngagement()});
 qs('#workbenchInput')?.addEventListener('input',e=>{st.workbench=e.target.value;save()});
 qs('#resetWorkbench')?.addEventListener('click',()=>{st.workbench=starterFor(w);st.proof=false;save();renderEngagement()});
 qs('#openSkill')?.addEventListener('click',()=>openSkill(w));
 qs('#runWorkbench')?.addEventListener('click',()=>runWorkbench(w,st));
 qs('#completeWeek')?.addEventListener('click',()=>completeWeek(w,st));
 qs('#exportWeek')?.addEventListener('click',()=>exportWeek(w,st));
}
async function runWorkbench(w,st){
 st.workbench=qs('#workbenchInput').value;save();const out=qs('#workbenchOutput');out.innerHTML='<div class="empty">Running / validating work…</div>';
 if(w.workbench==='sql')return runSQL(w,st,out);
 if(w.workbench==='python')return runPython(w,st,out);
 if(w.workbench==='api')return runAPISim(w,st,out);
 const txt=st.workbench.trim();if(txt.length<80){out.innerHTML='<div class="empty" style="color:var(--r)">The artifact is too thin to count as execution evidence. Develop the reasoning or design further.</div>';return}
 st.proof=true;save();out.innerHTML=`<div class="empty" style="color:var(--g)">Artifact recorded. Review will evaluate coherence, tradeoffs, verification, and fit to the engagement—not word count.</div>`
}
let SQLDB=null;
async function initSQL(){if(SQLDB)return SQLDB;if(!window.initSqlJs)throw new Error('sql.js not loaded');const SQL=await initSqlJs({locateFile:f=>`https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.11.0/${f}`});SQLDB=new SQL.Database();SQLDB.run('CREATE TABLE evidence(account_id INTEGER,cohort_week TEXT,segment TEXT,region TEXT,arr INTEGER,activated_14d INTEGER,provisioning_days INTEGER,mapping_rework INTEGER);');const rows=[[1,'W-6','Enterprise','US',420000,1,4,0],[2,'W-6','Mid-market','US',180000,1,3,0],[3,'W-5','Enterprise','UK',380000,1,5,1],[4,'W-4','Enterprise','US',620000,0,16,3],[5,'W-4','Mid-market','US',170000,1,6,1],[6,'W-3','Enterprise','UK',450000,0,18,4],[7,'W-2','Enterprise','US',690000,0,23,6],[8,'W-2','Mid-market','UK',190000,1,8,1],[9,'W-1','Enterprise','US',720000,0,24,7],[10,'W-1','Mid-market','UK',200000,1,9,1]];const stmt=SQLDB.prepare('INSERT INTO evidence VALUES (?,?,?,?,?,?,?,?)');rows.forEach(r=>stmt.run(r));stmt.free();return SQLDB}
function tableHTML(res){if(!res.length)return '<div class="empty">Query executed. No rows returned.</div>';const x=res[0];return `<table><thead><tr>${x.columns.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${x.values.map(r=>`<tr>${r.map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('')}</tbody></table>`}
async function runSQL(w,st,out){try{const db=await initSQL();const r=db.exec(st.workbench);st.proof=true;save();out.innerHTML=tableHTML(r)}catch(e){out.innerHTML=`<div class="empty" style="color:var(--r)">${esc(e.message||e)}</div>`}}
async function runPython(w,st,out){try{if(!window.loadPyodide){out.innerHTML='<div class="empty">Loading Python runtime…</div>';await loadScript('https://cdn.jsdelivr.net/pyodide/v0.27.7/full/pyodide.js')}if(!window.__py){window.__py=await loadPyodide({indexURL:'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/'})}const r=await window.__py.runPythonAsync(st.workbench);st.proof=true;save();out.innerHTML=`<div class="empty" style="color:var(--g)">${esc(r===undefined?'Python executed successfully.':r)}</div>`}catch(e){out.innerHTML=`<div class="empty" style="color:var(--r)">${esc(e.message||e)}</div>`}}
function loadScript(src){return new Promise((ok,bad)=>{const s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=bad;document.head.appendChild(s)})}
function runAPISim(w,st,out){const q=st.workbench.toLowerCase();let response={status:200,headers:{'x-rate-limit-remaining':'0','retry-after':'2'},body:{events:[{id:'evt_91',attempt:3,status:'timeout'},{id:'evt_92',attempt:2,status:'duplicate'}],next_cursor:'c_20'}};if(q.includes('post'))response={status:409,body:{error:'idempotency_conflict',message:'Duplicate operation detected'}};st.proof=true;save();out.innerHTML=`<pre class="empty" style="white-space:pre-wrap;color:var(--g)">${esc(JSON.stringify(response,null,2))}</pre>`}
function openSkill(w){const modal=qs('#skillModal');const title=qs('#skillTitle'),body=qs('#skillBody');const map={sql:['SQL as evidence','SELECT chooses fields. WHERE filters. GROUP BY compares groups. JOIN connects evidence. Start with the business question; write the smallest query that can answer it.'],python:['Python for reproducible analysis','Use code to make transformations and tests repeatable. Name inputs, keep intermediate checks visible, and separate data cleaning from interpretation.'],api:['API diagnosis','Inspect method, endpoint, auth, headers, status, body, retries, idempotency, timeouts, rate limits, and webhook behavior as one contract.'],architecture:['Architecture as tradeoffs','Define workload scope, constraints, failure behavior, data boundaries, operations, and economics. Produce alternatives before choosing.'],ai:['Production AI','Define the task before the model. Build evaluation before rollout. Bound authority, measure failure, plan abstention and human escalation, monitor cost/latency.'],incident:['SRE incident practice','Stabilize first. State known/unknown. Protect customers. Use SLOs and observable signals. Preserve evidence. Verify recovery before declaring it.']};const k=map[w.workbench]||['Professional judgment','Frame the problem, establish reality, create options, expose tradeoffs, choose the next action, and define how you will know whether it worked.'];title.textContent=k[0];body.textContent=k[1];modal.classList.add('on')}
function completeWeek(w,st){st.completed=true;S.ledger[w.w]={title:w.title,org:org(w).name,completedAt:new Date().toISOString(),evidence:st.seen.length,decisions:st.decisions.length,workbench:w.workbench,lenses:w.lenses,level:w.stage};if(S.maxUnlocked===w.w&&w.w<26)S.maxUnlocked++;if(w.w<26){S.week=w.w+1;ws(S.week);S.view='engagement'}save();toast(w.w===26?'Capstone recorded. Professional review complete.':'Engagement complete. Next week unlocked.');renderAll()}
function exportWeek(w,st){const payload={lab:'Solutions Lab v2',week:w.w,organization:org(w),engagement:w,learnerEvidence:{seenEvidence:st.seen.map(i=>w.evidence[i]),notes:st.notes,decisions:st.decisions,workbenchType:w.workbench,workbenchArtifact:st.workbench,executionEvidence:st.proof,completed:st.completed},disclosure:'Independent simulated apprenticeship evidence; not a real client engagement unless separately identified.'};download(`solutions-lab-week-${String(w.w).padStart(2,'0')}.json`,JSON.stringify(payload,null,2))}
function download(name,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)}
function renderRoadmap(){const groups=[1,2,3,4,5,6].map(m=>LAB.weeks.filter(w=>w.month===m));qs('#roadmap').innerHTML=`<div class="page"><div class="eyebrow">26-WEEK OPERATING MAP</div><h2>Problems drive the curriculum.</h2><p class="lead">The technologies are real, but they are subordinate to the engagement. Capabilities recur under decreasing guidance, different industries, different regions, and changing consequences.</p><div class="roadmap">${groups.map((g,i)=>`<section class="month"><div class="monthhead"><b>MONTH ${i+1}</b><span>${esc(g[0]?.stage||'')}</span></div><div class="weeks">${g.map(w=>`<article class="weekcard ${w.w===S.week?'active':''}"><small>W${String(w.w).padStart(2,'0')} · ${esc(w.region)}</small><h4>${esc(w.title)}</h4><p>${esc(LAB.organizations[w.org].name)} · ${esc(w.workbench)}</p><button data-week="${w.w}" aria-label="Open week ${w.w}"></button></article>`).join('')}</div></section>`).join('')}</div></div>`;qsa('[data-week]').forEach(b=>b.addEventListener('click',()=>{S.week=+b.dataset.week;S.view='engagement';save();renderAll()}))}
function renderStandards(){qs('#standards').innerHTML=`<div class="page"><div class="eyebrow">EXTERNAL LEGITIMACY LAYER</div><h2>Professional standards define good.</h2><p class="lead">The Lab is independent and is not affiliated with or endorsed by these organizations. Their public frameworks provide inspectable review lenses; the Lab combines them inside longitudinal engagements.</p><div class="standards">${LAB.standards.map(s=>`<article class="standard"><small>${esc(s[0])}</small><h3>${esc(s[1])}</h3><p>${esc(s[2])}</p></article>`).join('')}</div></div>`}
function renderEvidence(){const done=Object.entries(S.ledger).sort((a,b)=>+a[0]-+b[0]);qs('#evidence').innerHTML=`<div class="page"><div class="eyebrow">EVIDENCE ENGINE</div><h2>Claims require artifacts.</h2><p class="lead">A capability does not become Independent because a lesson was completed. It advances through observed work, execution, defense, transfer, and later consequence.</p><div class="ledger">${done.length?done.map(([n,x])=>`<article><div class="level">W${String(n).padStart(2,'0')} · ${esc(x.level)}</div><div><h3>${esc(x.org)} · ${esc(x.title)}</h3><p>${x.evidence} evidence source(s), ${x.decisions} decision record(s), ${esc(x.workbench)} workbench proof.</p></div><div class="right status">RECORDED</div></article>`).join(''):'<article><div class="level">START</div><div><h3>No engagement completed yet.</h3><p>Evidence appears here after a mastery gate is completed.</p></div><div class="right status">WEEK 01</div></article>'}</div></div>`}
function renderPortfolio(){const done=Object.entries(S.ledger);qs('#portfolio').innerHTML=`<div class="page"><div class="eyebrow">PORTFOLIO OUTPUT</div><h2>Build a record, not a highlight reel.</h2><p class="lead">Each completed engagement can export its evidence chain. Public presentation should distinguish simulated work from real deployments and link claims to inspectable artifacts.</p><div class="portfolio-grid"><article class="artifact"><small>ENGAGEMENTS COMPLETE</small><h3>${done.length} / 26</h3><p>Longitudinal record across regions, industries, technologies, and professional lenses.</p></article><article class="artifact"><small>INDEPENDENCE</small><h3>${Math.round((S.maxUnlocked-1)/26*100)}%</h3><p>Progress is tied to completed gates, not elapsed calendar time.</p></article><article class="artifact"><small>EXPORT</small><h3>Evidence package</h3><p>Export the current week from its Review tab, or export the complete ledger below.</p><button class="btn primary" id="exportAll">EXPORT FULL LEDGER</button></article><article class="artifact"><small>INTEGRITY</small><h3>Simulation stays labeled.</h3><p>No modeled result should be represented as real customer impact. External deployments can be added separately when they exist.</p></article></div></div>`;qs('#exportAll')?.addEventListener('click',()=>download('solutions-lab-evidence-ledger.json',JSON.stringify({meta:LAB.meta,progress:{maxUnlocked:S.maxUnlocked,currentWeek:S.week},ledger:S.ledger,weekState:S.weekState,disclosure:'Independent simulated apprenticeship unless separately identified.'},null,2)))}
function bindNav(){qsa('[data-view]').forEach(b=>b.onclick=()=>{S.view=b.dataset.view;save();renderAll()});qs('#closeSkill').onclick=()=>qs('#skillModal').classList.remove('on');qs('#skillModal').onclick=e=>{if(e.target.id==='skillModal')e.currentTarget.classList.remove('on')}}
function renderAll(){renderChrome();renderEngagement();renderRoadmap();renderStandards();renderEvidence();renderPortfolio();renderChrome();bindNav()}
document.addEventListener('DOMContentLoaded',renderAll);
})();