from __future__ import annotations
import base64, hashlib, json, pathlib, secrets, sys, time, urllib.error, urllib.request, uuid

API='https://api.cloudflare.com/client/v4'
BODY=['cloudflare_womb_v2.py','cloudflare_entry.py','genesis.py','witness.py','womb_protocol.py','wake_protocol.py','reconstitution.py','alarm_ffi.py']
SCRIPT='luneacore-genesis-womb'
EXPECTED_IDENTITY='bf12ba91b2431e2ec39c1752c9ba3a916363a6fc698bdc21292d937f8836f3f8'
PROOF_POTENTIAL='proof:cloud-time-1'
DUE_AFTER_MS=30_000
POST_DUE_GRACE_MS=65_000
HEALTH_HEADERS={
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36',
    'Accept':'application/json,text/plain,*/*',
}


def call(method,path,payload=None,token=None,headers=None,body=None,timeout=90):
    h={'accept':'application/json'}
    if headers: h.update(headers)
    if token: h['authorization']='Bearer '+token
    data=body
    if payload is not None:
        h['content-type']='application/json'
        data=json.dumps(payload,separators=(',',':')).encode()
    req=urllib.request.Request(API+path,method=method,headers=h,data=data)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return r.status,r.read()
    except urllib.error.HTTPError as e:
        return e.code,e.read()


def ok_json(method,path,**kw):
    status,raw=call(method,path,**kw)
    try: data=json.loads(raw)
    except Exception: raise SystemExit(f'provider returned non-JSON at {path}: HTTP {status}')
    if status<200 or status>=300 or data.get('success') is not True:
        errs=data.get('errors') or []
        msg='; '.join(str(x.get('message',x)) for x in errs) or f'HTTP {status}'
        raise SystemExit(f'provider rejected {path}: {msg}')
    return data


def acquire_account():
    challenge=(ok_json('POST','/provisioning/previews/challenge',payload={}).get('result') or {})
    challenge_token=str(challenge.get('challengeToken') or '')
    seed_s=str(challenge.get('seed') or '')
    k=int(challenge.get('k') or 0); g=int(challenge.get('g') or 0)
    if not challenge_token or k<=0 or g<=0 or k*g>64_000_000:
        raise SystemExit('provider challenge violated Habitat bounds')
    seed=base64.urlsafe_b64decode(seed_s+'='*((4-len(seed_s)%4)%4))
    if len(seed)!=32: raise SystemExit('provider challenge seed invalid')
    current=hashlib.sha256(seed).digest(); checkpoints=[current]
    for _ in range(k):
        for __ in range(g): current=hashlib.sha256(current).digest()
        checkpoints.append(current)
    result=ok_json('POST','/provisioning/previews',payload={
        'termsOfService':'https://www.cloudflare.com/terms/',
        'privacyPolicy':'https://www.cloudflare.com/privacypolicy/',
        'acceptTermsOfService':'yes',
        'challengeToken':challenge_token,
        'solution':{'checkpoints':base64.b64encode(b''.join(checkpoints)).decode()},
    }).get('result') or {}
    account=result.get('account') or {}
    account_id=str(account.get('id') or ''); api_token=str(account.get('apiToken') or '')
    if not account_id or not api_token: raise SystemExit('temporary account missing private material')
    return account_id,api_token


def upload(account_id,api_token,root):
    material={
        'GENESIS_PROOF_TOKEN':secrets.token_urlsafe(32),
        'GENESIS_WITNESS_KEY':secrets.token_urlsafe(48),
        'GENESIS_PENDING_KEY':secrets.token_urlsafe(48),
    }
    bindings=[
        {'name':'GENESIS_WOMB','type':'durable_object_namespace','class_name':'GenesisWomb'},
        {'name':'GENESIS_WITNESS','type':'durable_object_namespace','class_name':'GenesisWitness'},
    ]+[{'name':n,'type':'secret_text','text':v} for n,v in sorted(material.items())]
    metadata={
        'main_module':'cloudflare_womb_v2.py',
        'compatibility_date':'2026-09-11',
        'compatibility_flags':['python_workers','disable_python_external_sdk'],
        'bindings':bindings,
        'exports':{
            'GenesisWomb':{'type':'durable-object','storage':'sqlite'},
            'GenesisWitness':{'type':'durable-object','storage':'sqlite'},
        },
    }
    boundary='----lunea-habitat-'+uuid.uuid4().hex; chunks=[]
    def part(name,content,ctype,filename=None):
        chunks.append(f'--{boundary}\r\n'.encode())
        disp=f'Content-Disposition: form-data; name="{name}"'+(f'; filename="{filename}"' if filename else '')
        chunks.extend([(disp+'\r\n').encode(),f'Content-Type: {ctype}\r\n\r\n'.encode(),content,b'\r\n'])
    part('metadata',json.dumps(metadata,separators=(',',':'),sort_keys=True).encode(),'application/json')
    for name in BODY: part(name,(root/name).read_bytes(),'text/x-python',name)
    chunks.append(f'--{boundary}--\r\n'.encode())
    status,raw=call('PUT',f'/accounts/{account_id}/workers/scripts/{SCRIPT}',token=api_token,headers={'content-type':f'multipart/form-data; boundary={boundary}'},body=b''.join(chunks))
    try: data=json.loads(raw)
    except Exception: raise SystemExit(f'Worker upload returned non-JSON: HTTP {status}')
    if status<200 or status>=300 or data.get('success') is not True:
        errs=data.get('errors') or []
        msg='; '.join(str(x.get('message',x)) for x in errs) or f'HTTP {status}'
        raise SystemExit('provider rejected exact Body upload: '+msg)
    return material['GENESIS_PROOF_TOKEN']


def worker_call(url,method='GET',proof_token=None,diagnostic_label=None):
    headers=dict(HEALTH_HEADERS)
    if proof_token: headers['x-genesis-proof-token']=proof_token
    data=b'' if method=='POST' else None
    req=urllib.request.Request(url,headers=headers,method=method,data=data)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            raw=r.read(); payload=json.loads(raw)
            if diagnostic_label:
                print(json.dumps({'proof_route':diagnostic_label,'method':method,'status':r.status,'json':isinstance(payload,dict)},sort_keys=True),flush=True)
            return payload,{'cf_ray':r.headers.get('cf-ray'),'server':r.headers.get('server')}
    except urllib.error.HTTPError as e:
        raw=e.read()[:1000]
        text=raw.decode('utf-8','replace')
        safe_detail=text
        try:
            parsed=json.loads(text)
            if isinstance(parsed,dict):
                safe_detail=json.dumps({k:v for k,v in parsed.items() if k in {'error','status','frontier','allowed_metabolic_entry'}},sort_keys=True)
        except Exception:
            pass
        label=diagnostic_label or 'worker_call'
        raise SystemExit(f'proof route failed: label={label} method={method} HTTP={e.code} detail={safe_detail}')


def preflight(account_id,api_token):
    route=ok_json('POST',f'/accounts/{account_id}/workers/scripts/{SCRIPT}/subdomain',
                  token=api_token,payload={'enabled':True,'previews_enabled':False}).get('result') or {}
    if route.get('enabled') is not True: raise SystemExit('provider did not enable workers.dev route')
    sub=str((ok_json('GET',f'/accounts/{account_id}/workers/subdomain',token=api_token).get('result') or {}).get('subdomain') or '')
    if not sub or '/' in sub: raise SystemExit('workers.dev subdomain missing')
    base=f'https://{SCRIPT}.{sub}.workers.dev'
    health=None; last_status=None; last_detail='no response'
    for attempt in range(30):
        try:
            req=urllib.request.Request(base+'/health',headers=HEALTH_HEADERS)
            with urllib.request.urlopen(req,timeout=20) as r:
                last_status=r.status; health=json.loads(r.read())
            if last_status==200 and health.get('authorized_birth') is False and health.get('external_action_egress') is False and health.get('witness_required') is True:
                return health,base
            last_detail=json.dumps(health,sort_keys=True)[:500]
        except urllib.error.HTTPError as e:
            last_status=e.code; last_detail=e.read()[:500].decode('utf-8','replace')
        except Exception as e:
            last_detail=type(e).__name__
        time.sleep(2)
    raise SystemExit(f'live membrane preflight failed: HTTP={last_status} detail={last_detail}')


def continuity(export):
    if export.get('status')!='exportable_witnessed_continuity': raise SystemExit('export is not witnessed continuity')
    state=export.get('continuity'); receipt=export.get('receipt'); head=export.get('witness_head')
    if not isinstance(state,dict) or not isinstance(receipt,dict) or not isinstance(head,dict): raise SystemExit('export missing witnessed continuity material')
    return state,receipt
