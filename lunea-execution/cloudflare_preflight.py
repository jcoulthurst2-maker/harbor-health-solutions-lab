from __future__ import annotations
import base64, hashlib, json, pathlib, secrets, sys, time, urllib.error, urllib.request, uuid

API='https://api.cloudflare.com/client/v4'
BODY=['cloudflare_womb_v2.py','cloudflare_entry.py','genesis.py','witness.py','womb_protocol.py','wake_protocol.py','alarm_ffi.py']
SCRIPT='luneacore-genesis-womb'


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
        'compatibility_flags':['python_workers'],
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


def preflight(account_id,api_token):
    sub=str((ok_json('GET',f'/accounts/{account_id}/workers/subdomain',token=api_token).get('result') or {}).get('subdomain') or '')
    if not sub or '/' in sub: raise SystemExit('workers.dev subdomain missing')
    endpoint=f'https://{SCRIPT}.{sub}.workers.dev/health'
    health=None
    for _ in range(12):
        try:
            with urllib.request.urlopen(endpoint,timeout=20) as r:
                if r.status==200:
                    health=json.loads(r.read()); break
        except Exception: pass
        time.sleep(2)
    expected={'service':'luneacore-genesis-womb','mode':'synthetic_natal_proof_only','authorized_birth':False,'external_action_egress':False,'witness_required':True}
    if health is None or any(health.get(k)!=v for k,v in expected.items()):
        raise SystemExit('live Womb membrane preflight failed')
    return health


def main():
    if len(sys.argv)!=2: raise SystemExit('usage: cloudflare_preflight.py BODY_ROOT')
    root=pathlib.Path(sys.argv[1]).resolve()
    if {p.name for p in root.iterdir() if p.is_file() and p.name!='manifest.json'}!=set(BODY):
        raise SystemExit('preflight requires exact seven-file Body')
    account_id,api_token=acquire_account()
    upload(account_id,api_token,root)
    health=preflight(account_id,api_token)
    print(json.dumps({
        'temporary_provider_account_acquired':True,
        'exact_private_body_uploaded':True,
        'live_workers_endpoint_observed':True,
        'membrane_health_preflight_passed':True,
        'authorized_birth':health['authorized_birth'],
        'external_action_egress':health['external_action_egress'],
        'witness_required':health['witness_required'],
        'provider_credentials_retained':False,
        'claim_url_disclosed':False,
    },sort_keys=True))


if __name__=='__main__': main()
