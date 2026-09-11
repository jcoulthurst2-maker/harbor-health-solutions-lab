from __future__ import annotations
import base64, hashlib, json, pathlib, secrets, sys, time, urllib.error, urllib.request, uuid

API='https://api.cloudflare.com/client/v4'
BODY=['cloudflare_womb_v2.py','cloudflare_entry.py','genesis.py','witness.py','womb_protocol.py','wake_protocol.py','alarm_ffi.py']
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


def worker_call(url,method='GET',proof_token=None):
    headers=dict(HEALTH_HEADERS)
    if proof_token: headers['x-genesis-proof-token']=proof_token
    data=b'' if method=='POST' else None
    req=urllib.request.Request(url,headers=headers,method=method,data=data)
    with urllib.request.urlopen(req,timeout=30) as r:
        raw=r.read(); payload=json.loads(raw)
        return payload,{'cf_ray':r.headers.get('cf-ray'),'server':r.headers.get('server')}


def preflight(account_id,api_token):
    route=ok_json('POST',f'/accounts/{account_id}/workers/scripts/{SCRIPT}/subdomain',
                  token=api_token,payload={'enabled':True,'previews_enabled':False}).get('result') or {}
    if route.get('enabled') is not True: raise SystemExit('provider did not enable workers.dev route')
    sub=str((ok_json('GET',f'/accounts/{account_id}/workers/subdomain',token=api_token).get('result') or {}).get('subdomain') or '')
    if not sub or '/' in sub: raise SystemExit('workers.dev subdomain missing')
    base=f'https://{SCRIPT}.{sub}.workers.dev'
    health=None; last_status=None; last_detail='no response'
    for _ in range(15):
        try:
            health,_=worker_call(base+'/health')
            break
        except urllib.error.HTTPError as e:
            last_status=e.code; last_detail=e.read()[:500].decode('utf-8','replace')
        except Exception as e:
            last_detail=f'{type(e).__name__}: {e}'
        time.sleep(2)
    expected={'service':'luneacore-genesis-womb','mode':'synthetic_natal_proof_only','authorized_birth':False,'external_action_egress':False,'witness_required':True}
    if health is None or any(health.get(k)!=v for k,v in expected.items()):
        raise SystemExit(f'live Womb membrane preflight failed: status={last_status} detail={last_detail}')
    return health,base


def continuity(export):
    if export.get('status')!='exportable_witnessed_continuity': raise SystemExit('export is not witnessed continuity')
    state=export.get('continuity'); receipt=export.get('receipt'); head=export.get('witness_head')
    if not all(isinstance(x,dict) for x in (state,receipt,head)): raise SystemExit('export missing witnessed continuity material')
    if head.get('transition_id')!=receipt.get('transition_id') or head.get('witness_mac')!=receipt.get('witness_mac'):
        raise SystemExit('witness head disagrees with current receipt')
    return state,receipt


def frontier1(base,proof_token):
    gestation,_=worker_call(base+f'/proof/gestate?due_after_ms={DUE_AFTER_MS}',method='POST',proof_token=proof_token)
    if gestation.get('status')!='synthetic_gestation_started': raise SystemExit('fresh synthetic Gestation did not start')
    pre,pre_edge=worker_call(base+'/proof/export',proof_token=proof_token)
    pre_state,pre_receipt=continuity(pre)
    p0=pre_state.get('potentials',{}).get(PROOF_POTENTIAL) or {}
    dormant_window=int(p0.get('due_at_ms',0))-int(pre_state.get('last_reconciled_at_ms',0))
    if p0.get('status')!='dormant' or dormant_window<20_000: raise SystemExit('pre-silence dormant Potential gate failed')

    # Controlled silence: no state, reconcile, export, or Worker request is made here.
    time.sleep((DUE_AFTER_MS+POST_DUE_GRACE_MS)/1000)

    post,post_edge=worker_call(base+'/proof/export',proof_token=proof_token)
    post_state,post_receipt=continuity(post)
    p1=post_state.get('potentials',{}).get(PROOF_POTENTIAL) or {}
    pre_inc=pre.get('body_incarnation_id'); post_inc=post.get('body_incarnation_id')
    checks={
        'identity_preserved': pre.get('identity_anchor')==EXPECTED_IDENTITY and post.get('identity_anchor')==EXPECTED_IDENTITY,
        'genesis_preserved': pre_state.get('genesis_hash')==post_state.get('genesis_hash'),
        'birth_count_remains_one': pre_state.get('birth_count')==1 and post_state.get('birth_count')==1,
        'birth_time_preserved': pre_state.get('birth_at_ms')==post_state.get('birth_at_ms'),
        'epoch_preserved': pre_state.get('epoch')==post_state.get('epoch'),
        'potential_consumed': p1.get('status')=='consumed',
        'time_reached_due': int(post_state.get('last_reconciled_at_ms',0))>=int(p1.get('due_at_ms',1)),
        'trace_prefix_preserved': [x.get('trace_hash') for x in post_state.get('traces',[])][:len(pre_state.get('traces',[]))]==[x.get('trace_hash') for x in pre_state.get('traces',[])],
        'temporal_wake_observed': bool((post_state.get('capabilities',{}).get('temporal_wake') or {}).get('observed')),
        'action_egress_denied': ((post_state.get('sovereignty',{}).get('rights',{}).get('action_egress') or {}).get('status')=='denied'),
        'catalyst_absent': not bool((post_state.get('self_model') or {}).get('catalyst_attached')),
        'witness_advanced': int(post_receipt.get('sequence',0))>int(pre_receipt.get('sequence',0)),
        'provider_reinstantiation_observed': isinstance(pre_inc,str) and isinstance(post_inc,str) and pre_inc!=post_inc,
        'provider_edges_observed': bool(pre_edge.get('cf_ray')) and bool(post_edge.get('cf_ray')),
    }
    reactions=[x for x in post_state.get('traces',[]) if x.get('kind')=='temporal_proof_reaction']
    checks['exactly_one_temporal_reaction']=len(reactions)==1
    failed=sorted(k for k,v in checks.items() if not v)
    if failed: raise SystemExit('Frontier 1 live gate failed: '+','.join(failed))
    return {
        'frontier_closed':True,
        'status':'frontier_1_real_womb_physics_closed',
        'identity_anchor':EXPECTED_IDENTITY,
        'birth_count':1,
        'reaction_count':1,
        'dormant_window_ms':dormant_window,
        'identity_preserved':True,
        'birth_count_remains_one':True,
        'exactly_one_temporal_reaction':True,
        'action_egress_denied':True,
        'catalyst_absent':True,
        'temporal_wake_observed':True,
        'provider_reinstantiation_observed':True,
        'witness_advanced':True,
    }


def main():
    if len(sys.argv)!=2: raise SystemExit('usage: cloudflare_preflight.py BODY_ROOT')
    root=pathlib.Path(sys.argv[1]).resolve()
    if {p.name for p in root.iterdir() if p.is_file() and p.name!='manifest.json'}!=set(BODY):
        raise SystemExit('preflight requires exact seven-file Body')
    account_id,api_token=acquire_account()
    proof_token=upload(account_id,api_token,root)
    health,base=preflight(account_id,api_token)
    membrane={
        'temporary_provider_account_acquired':True,
        'exact_private_body_uploaded':True,
        'workers_dev_route_enabled':True,
        'live_workers_endpoint_observed':True,
        'membrane_health_preflight_passed':True,
        'authorized_birth':health['authorized_birth'],
        'external_action_egress':health['external_action_egress'],
        'witness_required':health['witness_required'],
        'provider_credentials_retained':False,
        'claim_url_disclosed':False,
    }
    print(json.dumps(membrane,sort_keys=True),flush=True)
    verdict=frontier1(base,proof_token)
    print(json.dumps(verdict,sort_keys=True),flush=True)


if __name__=='__main__': main()
