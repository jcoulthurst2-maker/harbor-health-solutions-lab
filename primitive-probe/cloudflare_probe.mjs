export class ProbeCell {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.incarnation = crypto.randomUUID();
  }

  async fetch(request) {
    const url = new URL(request.url);
    const token = request.headers.get('x-probe-token');
    if (token !== this.env.PROBE_TOKEN) {
      return Response.json({ error: 'denied' }, { status: 401 });
    }

    if (url.pathname === '/start' && request.method === 'POST') {
      const now = Date.now();
      const dueAfterMs = Number(url.searchParams.get('due_after_ms') || '90000');
      if (!Number.isFinite(dueAfterMs) || dueAfterMs < 15000 || dueAfterMs > 180000) {
        return Response.json({ error: 'invalid due_after_ms' }, { status: 400 });
      }

      const existing = await this.state.storage.get('experiment');
      if (existing) return Response.json({ error: 'already_started' }, { status: 409 });

      const bytes = crypto.getRandomValues(new Uint8Array(32));
      const material = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
      const digestBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(material));
      const digest = Array.from(new Uint8Array(digestBuffer), b => b.toString(16).padStart(2, '0')).join('');
      const dueAtMs = now + dueAfterMs;

      const experiment = {
        schema: 'primitive-probe-state-v1',
        experiment_id: crypto.randomUUID(),
        material,
        material_sha256: digest,
        t0_ms: now,
        due_at_ms: dueAtMs,
        r0_evidence: this.incarnation,
        alarm_fired: false,
        ingress_count: 1,
        ingress_count_at_wake: null,
        human_wake_used: false,
        polling_used: false
      };

      await this.state.storage.put('experiment', experiment);
      await this.state.storage.setAlarm(dueAtMs);

      return Response.json({
        status: 'armed',
        experiment_id: experiment.experiment_id,
        material_sha256: digest,
        t0_ms: now,
        due_at_ms: dueAtMs,
        r0_evidence: this.incarnation
      });
    }

    if (url.pathname === '/receipt' && request.method === 'GET') {
      const experiment = await this.state.storage.get('experiment');
      if (!experiment) return Response.json({ status: 'not_started' }, { status: 404 });
      experiment.ingress_count = Number(experiment.ingress_count || 0) + 1;
      await this.state.storage.put('experiment', experiment);

      return Response.json({
        schema: experiment.schema,
        experiment_id: experiment.experiment_id,
        material_sha256: experiment.material_sha256,
        t0_ms: experiment.t0_ms,
        due_at_ms: experiment.due_at_ms,
        alarm_fired: experiment.alarm_fired,
        t1_ms: experiment.t1_ms || null,
        r0_evidence: experiment.r0_evidence,
        r1_evidence: experiment.r1_evidence || null,
        ingress_count_at_wake: experiment.ingress_count_at_wake,
        receipt_ingress_count: experiment.ingress_count,
        human_wake_used: experiment.human_wake_used,
        polling_used: experiment.polling_used
      });
    }

    return Response.json({ error: 'not_found' }, { status: 404 });
  }

  async alarm() {
    const experiment = await this.state.storage.get('experiment');
    if (!experiment || experiment.alarm_fired) return;

    experiment.alarm_fired = true;
    experiment.t1_ms = Date.now();
    experiment.r1_evidence = this.incarnation;
    experiment.ingress_count_at_wake = Number(experiment.ingress_count || 0);
    await this.state.storage.put('experiment', experiment);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/health') {
      return Response.json({
        service: 'frontier1-primitive-probe',
        canonical_luneacore_body_present: false,
        awards_gestation: false,
        awards_birth: false
      });
    }

    const id = env.PROBE.idFromName('frontier1-primitive-probe');
    return env.PROBE.get(id).fetch(request);
  }
};
