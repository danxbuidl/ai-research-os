CREATE TABLE IF NOT EXISTS observations (
    observation_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    source_type TEXT NOT NULL,
    source_ref TEXT NOT NULL DEFAULT '',
    content_type TEXT NOT NULL,
    asset_refs_json TEXT NOT NULL DEFAULT '[]',
    payload_json TEXT NOT NULL DEFAULT '{}',
    event_time TEXT NOT NULL,
    ingested_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS observation_fts USING fts5(
    observation_id UNINDEXED,
    title,
    body,
    tokenize = 'unicode61'
);

CREATE TABLE IF NOT EXISTS feature_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    entity_type TEXT NOT NULL,
    entity_ref TEXT NOT NULL,
    features_json TEXT NOT NULL DEFAULT '{}',
    as_of TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    hypothesis_type TEXT NOT NULL,
    entity_refs_json TEXT NOT NULL DEFAULT '[]',
    time_horizon TEXT NOT NULL,
    thesis TEXT NOT NULL,
    supporting_evidence_json TEXT NOT NULL DEFAULT '[]',
    key_risks_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL NOT NULL DEFAULT 0.0,
    generated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_cards (
    decision_card_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    title TEXT NOT NULL,
    action TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS human_reviews (
    review_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    decision_card_id TEXT NOT NULL,
    reviewer TEXT NOT NULL,
    review_action TEXT NOT NULL,
    reason_tags_json TEXT NOT NULL DEFAULT '[]',
    edited_fields_json TEXT NOT NULL DEFAULT '{}',
    payload_json TEXT NOT NULL,
    reviewed_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outcome_records (
    outcome_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    decision_card_id TEXT NOT NULL,
    entity_ref TEXT NOT NULL,
    horizon TEXT NOT NULL,
    return_pct REAL NOT NULL DEFAULT 0.0,
    max_drawdown_pct REAL NOT NULL DEFAULT 0.0,
    hit_trigger INTEGER NOT NULL DEFAULT 0,
    hit_invalidation INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL DEFAULT '{}',
    evaluated_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    lesson_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    source_review_id TEXT NOT NULL,
    lesson_type TEXT NOT NULL,
    scope TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'candidate',
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evolution_proposals (
    evolution_proposal_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    schema_version TEXT NOT NULL DEFAULT 'v1',
    proposal_type TEXT NOT NULL,
    scope TEXT NOT NULL,
    challenger_name TEXT NOT NULL,
    hypothesis TEXT NOT NULL,
    change_summary TEXT NOT NULL,
    expected_gain TEXT NOT NULL DEFAULT '',
    risks_json TEXT NOT NULL DEFAULT '[]',
    validation_plan_json TEXT NOT NULL DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'candidate',
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proposal_runs (
    proposal_id TEXT PRIMARY KEY,
    trace_id TEXT NOT NULL,
    current_state TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    resume_token TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS proposal_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    agent_name TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_runs (
    run_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL,
    input_ref TEXT NOT NULL DEFAULT '',
    output_ref TEXT NOT NULL DEFAULT '',
    error_text TEXT NOT NULL DEFAULT '',
    started_at TEXT NOT NULL,
    finished_at TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS llm_calls (
    llm_call_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    prompt_version TEXT NOT NULL DEFAULT '',
    model_name TEXT NOT NULL DEFAULT '',
    token_in INTEGER NOT NULL DEFAULT 0,
    token_out INTEGER NOT NULL DEFAULT 0,
    cost_estimate REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL DEFAULT 'ok',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outbox_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    correlation_id TEXT NOT NULL DEFAULT '',
    proposal_id TEXT NOT NULL DEFAULT '',
    trace_id TEXT NOT NULL DEFAULT '',
    producer_agent TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    available_at TEXT NOT NULL,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agent_tasks (
    task_id TEXT PRIMARY KEY,
    task_type TEXT NOT NULL,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    assigned_agent TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    checkpoint_state TEXT NOT NULL DEFAULT 'NEW',
    status TEXT NOT NULL DEFAULT 'pending',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    resume_token TEXT NOT NULL DEFAULT '',
    available_at TEXT NOT NULL,
    last_error TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_timelines (
    event_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL,
    trend_impact_score REAL NOT NULL DEFAULT 0.0,
    human_escalation_score REAL NOT NULL DEFAULT 0.0,
    current_status TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_timeline_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    summary TEXT NOT NULL,
    evidence_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS event_asset_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL,
    asset_ref TEXT NOT NULL,
    linkage_type TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_factor_snapshots (
    factor_snapshot_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    asset_ref TEXT NOT NULL,
    factor_family TEXT NOT NULL,
    features_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_weight_versions (
    weight_version_id TEXT PRIMARY KEY,
    scope TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'candidate',
    weights_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS signal_tracking_tasks (
    tracking_task_id TEXT PRIMARY KEY,
    proposal_id TEXT NOT NULL,
    decision_card_id TEXT NOT NULL,
    asset_ref TEXT NOT NULL,
    horizon TEXT NOT NULL,
    due_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_outbox_topic_status ON outbox_events(topic, status, available_at);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent_status ON agent_tasks(assigned_agent, status, available_at);
CREATE INDEX IF NOT EXISTS idx_reviews_card ON human_reviews(decision_card_id, reviewed_at);
CREATE INDEX IF NOT EXISTS idx_outcomes_card ON outcome_records(decision_card_id, horizon);
CREATE INDEX IF NOT EXISTS idx_transition_proposal ON proposal_transitions(proposal_id, created_at);
