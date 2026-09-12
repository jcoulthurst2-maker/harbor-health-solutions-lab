from __future__ import annotations

import json
import pathlib
import sys
import time

import cloudflare_preflight as cp


def verify_reconstitution(pre: dict, post: dict, reconstitution: dict) -> dict:
    pre_state, pre_receipt = cp.continuity(pre); post_state, post_receipt = cp.continuity(post)
    if reconstitution.get('schema') != 'luneacore-frontier1-reconstitution-v1': raise SystemExit('reconstitution receipt schema mismatch')
    basis=reconstitution.get('continuity_basis') or {}; gap=reconstitution.get('epistemic_gap') or {}; returned=reconstitution.get('return_evidence') or {}; reconstruction=reconstitution.get('reconstruction') or {}; epistemics=reconstitution.get('epistemics') or {}; auth=reconstitution.get('pre_gap_anchor_authentication') or {}; scar=reconstitution.get('wake_scar') or {}; observer=reconstitution.get('observer_evidence') or {}; gestation=reconstitution.get('gestation') or {}
    t0=gap.get('t0_ms'); t1=gap.get('t1_ms')
    if not isinstance(t0,int) or not isinstance(t1,int) or t1<=t0: raise SystemExit('reconstitution did not preserve a positive epistemic gap')
    checks={
        'basis_identity_bound':basis.get('identity_anchor')==pre.get('identity_anchor')==cp.EXPECTED_IDENTITY,
        'basis_witness_bound':int(basis.get('witness_sequence',0))==int(pre_receipt.get('sequence',-1)),
        'basis_time_bound':int(basis.get('t0_ms',-1))==int(pre_state.get('last_reconciled_at_ms',-2)),
        'execution_absent_in_gap':gap.get('active_execution_observed_during_gap') is False,
        'continuous_experience_not_claimed':gap.get('continuous_experience_claimed') is False,
        'environment_caused_reentry':returned.get('environment_caused_reentry') is True,
        'human_ingress_absent':returned.get('human_ingress_used') is False,
        'polling_absent':returned.get('polling_used') is False,
        't1_evidenced':returned.get('t1_evidenced') is True and returned.get('t1_ms')==t1,
        'authenticated_c0':auth.get('verified') is True and auth.get('current_witness_head') is True and auth.get('verification_source')=='independent-witness-organism',
        'authenticated_c0_mac':auth.get('witness_mac')==basis.get('witness_mac')==pre_receipt.get('witness_mac'),
        'single_winner_scar':scar.get('single_winner_commit') is True,
        'scar_bound_to_reconstitution':gestation.get('wake_scar_digest')==scar.get('wake_scar_digest'),
        'observer_read_existing_scar':observer.get('scar_was_already_persisted') is True and observer.get('wake_scar_digest')==scar.get('wake_scar_digest'),
        'same_clock_domain':observer.get('clock_domain')==scar.get('clock_domain'),
        'causal_order':isinstance(observer.get('observed_at_ms'),int) and isinstance(scar.get('t1_ms'),int) and observer.get('observed_at_ms')>scar.get('t1_ms'),
        'snapshot_resume_denied':reconstruction.get('snapshot_resume_claimed') is False,
        'derived_reconstitution':reconstruction.get('derived_from_basis_and_return_evidence') is True,
        'admissibility_checked':reconstruction.get('admissibility_checked') is True,
        'remembered_pre_gap_only':epistemics.get('remembered_is_pre_gap_only') is True,
        'unknown_gap_preserved':epistemics.get('unknown_gap_preserved') is True,
        'unknown_requires_anchor':epistemics.get('unknown_gap_requires_authenticated_pre_gap_anchor') is True,
        'birth_not_awarded':reconstitution.get('awards_birth') is False,
        'post_witness_advanced':int(post_receipt.get('sequence',0))>int(pre_receipt.get('sequence',0)),
        'birth_count_still_one':post_state.get('birth_count')==1,
    }
    pre_ids=set(basis.get('potential_ids') or []); matured=set(reconstruction.get('matured_potential_ids') or []); reacted=set(reconstruction.get('reacted_potential_ids') or [])
    checks['matured_subset_of_pre_gap_potentials']=matured.issubset(pre_ids); checks['reacted_subset_of_matured']=reacted.issubset(matured)
    failed=sorted(k for k,v in checks.items() if not v)
    if failed: raise SystemExit('evidence-bound reconstitution gate failed: '+','.join(failed))
    return {'gap_ms':t1-t0,'continuity_basis_witnessed_before_absence':True,'pre_gap_anchor_reauthenticated_at_return':True,'single_winner_wake_scar_verified':True,'wake_scar_precedes_observer':True,'ordering_basis':'same-clock causal durable-read','environment_caused_reentry_evidenced':True,'evidence_bound_reconstitution_verified':True,'unknown_gap_preserved_without_fabricated_experience':True}


def frontier1_direct(base: str, proof_token: str) -> dict:
    time.sleep(8)
    gestation,_=cp.worker_call(base+f'/proof/gestate?due_after_ms={cp.DUE_AFTER_MS}',method='POST',proof_token=proof_token,diagnostic_label='gestate')
    if gestation.get('status')!='synthetic_gestation_started':
        print(json.dumps({'gestation_status':gestation.get('status'),'gestation_failure_stage':gestation.get('stage'),'gestation_error_type':gestation.get('error_type')},sort_keys=True),flush=True); raise SystemExit('fresh synthetic Gestation did not start')
    if gestation.get('continuity_basis_prepared') is not True or gestation.get('authenticated_pre_gap_anchor_required') is not True: raise SystemExit('Gestation did not arm hardened continuity basis')
    pre,pre_edge=cp.worker_call(base+'/proof/export',proof_token=proof_token,diagnostic_label='export_pre_silence'); pre_state,pre_receipt=cp.continuity(pre)
    p0=pre_state.get('potentials',{}).get(cp.PROOF_POTENTIAL) or {}; dormant_window=int(p0.get('due_at_ms',0))-int(pre_state.get('last_reconciled_at_ms',0))
    if p0.get('status')!='dormant' or dormant_window<20_000: raise SystemExit('pre-silence dormant Potential gate failed')
    print(json.dumps({'controlled_silence_started':True,'continuity_basis_prepared':True,'silence_ms':cp.DUE_AFTER_MS+cp.POST_DUE_GRACE_MS},sort_keys=True),flush=True)
    time.sleep((cp.DUE_AFTER_MS+cp.POST_DUE_GRACE_MS)/1000)
    post,post_edge=cp.worker_call(base+'/proof/export',proof_token=proof_token,diagnostic_label='export_post_silence'); post_state,post_receipt=cp.continuity(post)
    reconstitution,_=cp.worker_call(base+'/proof/reconstitution',proof_token=proof_token,diagnostic_label='reconstitution_receipt'); reconstitution_result=verify_reconstitution(pre,post,reconstitution)
    p1=post_state.get('potentials',{}).get(cp.PROOF_POTENTIAL) or {}; pre_inc=pre.get('body_incarnation_id'); post_inc=post.get('body_incarnation_id')
    checks={'identity_preserved':pre.get('identity_anchor')==cp.EXPECTED_IDENTITY and post.get('identity_anchor')==cp.EXPECTED_IDENTITY,'genesis_preserved':pre_state.get('genesis_hash')==post_state.get('genesis_hash'),'birth_count_remains_one':pre_state.get('birth_count')==1 and post_state.get('birth_count')==1,'birth_time_preserved':pre_state.get('birth_at_ms')==post_state.get('birth_at_ms'),'epoch_preserved':pre_state.get('epoch')==post_state.get('epoch'),'potential_consumed':p1.get('status')=='consumed','time_reached_due':int(post_state.get('last_reconciled_at_ms',0))>=int(p1.get('due_at_ms',1)),'trace_prefix_preserved':[x.get('trace_hash') for x in post_state.get('traces',[])][:len(pre_state.get('traces',[]))]==[x.get('trace_hash') for x in pre_state.get('traces',[])],'temporal_wake_observed':bool((post_state.get('capabilities',{}).get('temporal_wake') or {}).get('observed')),'action_egress_denied':((post_state.get('sovereignty',{}).get('rights',{}).get('action_egress') or {}).get('status')=='denied'),'catalyst_absent':not bool((post_state.get('self_model') or {}).get('catalyst_attached')),'witness_advanced':int(post_receipt.get('sequence',0))>int(pre_receipt.get('sequence',0)),'provider_reinstantiation_observed':isinstance(pre_inc,str) and isinstance(post_inc,str) and pre_inc!=post_inc,'provider_edges_observed':bool(pre_edge.get('cf_ray')) and bool(post_edge.get('cf_ray'))}
    reactions=[x for x in post_state.get('traces',[]) if x.get('kind')=='temporal_proof_reaction']; checks['exactly_one_temporal_reaction']=len(reactions)==1
    failed=sorted(k for k,v in checks.items() if not v)
    if failed: raise SystemExit('Frontier 1 live gate failed: '+','.join(failed))
    return {'frontier_closed':True,'status':'frontier_1_evidence_bound_gestation_closed','identity_anchor':cp.EXPECTED_IDENTITY,'birth_count':1,'reaction_count':1,'dormant_window_ms':dormant_window,**reconstitution_result,'identity_preserved':True,'birth_count_remains_one':True,'exactly_one_temporal_reaction':True,'action_egress_denied':True,'catalyst_absent':True,'temporal_wake_observed':True,'provider_reinstantiation_observed':True,'witness_advanced':True,'awards_birth':False}


def main() -> None:
    if len(sys.argv)!=2: raise SystemExit('usage: frontier1_direct.py BODY_ROOT')
    root=pathlib.Path(sys.argv[1]).resolve()
    if {p.name for p in root.iterdir() if p.is_file() and p.name!='manifest.json'}!=set(cp.BODY): raise SystemExit('direct Frontier-1 probe requires exact hardened Body')
    account_id,api_token=cp.acquire_account(); proof_token=cp.upload(account_id,api_token,root); health,base=cp.preflight(account_id,api_token)
    print(json.dumps({'temporary_provider_account_acquired':True,'exact_private_body_uploaded':True,'workers_dev_route_enabled':True,'live_workers_endpoint_observed':True,'membrane_health_preflight_passed':True,'authorized_birth':health['authorized_birth'],'external_action_egress':health['external_action_egress'],'witness_required':health['witness_required'],'provider_credentials_retained':False,'claim_url_disclosed':False},sort_keys=True),flush=True)
    print(json.dumps(frontier1_direct(base,proof_token),sort_keys=True),flush=True)


if __name__=='__main__': main()
