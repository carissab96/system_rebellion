--
-- PostgreSQL database dump
--

\restrict ozeVgK7HM2mnmRc1QgxFTWNpuzv7AGhJ5w83sgi42ht9Ayo4dPqEHfz6xIIVNQJ

-- Dumped from database version 18.2
-- Dumped by pg_dump version 18.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: vector; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA public;


--
-- Name: EXTENSION vector; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION vector IS 'vector data type and ivfflat and hnsw access methods';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: action_outcome_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.action_outcome_records (
    id integer NOT NULL,
    agent_name character varying(50) NOT NULL,
    action character varying(100) NOT NULL,
    pre_metrics json NOT NULL,
    post_metrics json NOT NULL,
    metric_pattern_fingerprint character varying(255) NOT NULL,
    success boolean NOT NULL,
    improvement double precision NOT NULL,
    primary_metric character varying(100),
    severity_score double precision NOT NULL,
    other_actions_considered json,
    created_at timestamp without time zone DEFAULT now(),
    central_memory_id character varying(36)
);


--
-- Name: action_outcome_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.action_outcome_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: action_outcome_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.action_outcome_records_id_seq OWNED BY public.action_outcome_records.id;


--
-- Name: agent_decision_vectors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_decision_vectors (
    id bigint NOT NULL,
    vector_id uuid DEFAULT gen_random_uuid() NOT NULL,
    sql_memory_id character varying(36),
    agent_name character varying(50) NOT NULL,
    user_id character varying(255),
    decision_type character varying(100) NOT NULL,
    event_type character varying(100),
    priority integer DEFAULT 2 NOT NULL,
    occurred_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    embedding double precision[] NOT NULL,
    decision_text text NOT NULL,
    decision_summary text,
    metadata jsonb,
    confidence_score double precision,
    embedding_model character varying(100) DEFAULT 'all-MiniLM-L6-v2'::character varying NOT NULL
);


--
-- Name: agent_decision_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agent_decision_vectors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agent_decision_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agent_decision_vectors_id_seq OWNED BY public.agent_decision_vectors.id;


--
-- Name: agent_global_patterns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_global_patterns (
    id character varying NOT NULL,
    pattern_key character varying NOT NULL,
    value json NOT NULL,
    updated_at timestamp with time zone
);


--
-- Name: agent_interaction_vectors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_interaction_vectors (
    id bigint NOT NULL,
    vector_id uuid DEFAULT gen_random_uuid() NOT NULL,
    primary_agent character varying(50) CONSTRAINT agent_interaction_vectors_from_agent_not_null NOT NULL,
    secondary_agent character varying(50),
    interaction_type character varying(100) NOT NULL,
    occurred_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    embedding double precision[] NOT NULL,
    interaction_text text NOT NULL,
    interaction_summary text,
    metadata jsonb,
    user_id character varying(255) DEFAULT 'system'::character varying NOT NULL,
    outcome character varying(255),
    success_score double precision,
    sql_interaction_id character varying(255)
);


--
-- Name: agent_interaction_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agent_interaction_vectors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agent_interaction_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agent_interaction_vectors_id_seq OWNED BY public.agent_interaction_vectors.id;


--
-- Name: agent_learning_interactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_learning_interactions (
    id integer NOT NULL,
    interaction_id character varying(36),
    user_id character varying NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    source_agent character varying(50) NOT NULL,
    target_agent character varying(50) NOT NULL,
    source_memory_id character varying(36) NOT NULL,
    learning_type character varying(100) NOT NULL,
    adaptation_method jsonb,
    application_context jsonb,
    transfer_success boolean,
    effectiveness_score double precision,
    improvement_measured double precision,
    validated_by_stick boolean,
    cross_validation_count integer
);


--
-- Name: agent_learning_interactions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agent_learning_interactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agent_learning_interactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agent_learning_interactions_id_seq OWNED BY public.agent_learning_interactions.id;


--
-- Name: agent_learning_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_learning_records (
    id integer NOT NULL,
    agent_name character varying(50) NOT NULL,
    fingerprint_l1 character varying(50) NOT NULL,
    fingerprint_l2 character varying(100) NOT NULL,
    fingerprint_l3 character varying(150) NOT NULL,
    resource_type character varying(20) NOT NULL,
    severity character varying(20) NOT NULL,
    root_cause character varying(500),
    process_category character varying(20),
    action character varying(100) NOT NULL,
    parameters json,
    confidence double precision,
    followed_vic20 boolean DEFAULT false,
    success boolean NOT NULL,
    improvement json,
    what_worked character varying(500),
    what_failed character varying(500),
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: agent_learning_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agent_learning_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agent_learning_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agent_learning_records_id_seq OWNED BY public.agent_learning_records.id;


--
-- Name: agent_memories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_memories (
    id uuid NOT NULL,
    user_id character varying NOT NULL,
    agent_name character varying NOT NULL,
    memory_type character varying NOT NULL,
    content json NOT NULL,
    importance integer,
    "timestamp" timestamp with time zone,
    last_accessed timestamp with time zone,
    access_count integer
);


--
-- Name: agent_pattern_vectors; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_pattern_vectors (
    id bigint NOT NULL,
    vector_id uuid DEFAULT gen_random_uuid() NOT NULL,
    agent_name character varying(50) NOT NULL,
    user_id character varying(255),
    pattern_type character varying(100) NOT NULL,
    pattern_name character varying(255),
    pattern_description text NOT NULL,
    first_observed timestamp with time zone NOT NULL,
    last_observed timestamp with time zone NOT NULL,
    observation_count integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    embedding double precision[] NOT NULL,
    confidence_score double precision,
    success_rate double precision,
    application_count integer DEFAULT 0 NOT NULL,
    pattern_data jsonb NOT NULL,
    embedding_model character varying(100) DEFAULT 'all-MiniLM-L6-v2'::character varying NOT NULL
);


--
-- Name: agent_pattern_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agent_pattern_vectors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agent_pattern_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agent_pattern_vectors_id_seq OWNED BY public.agent_pattern_vectors.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: central_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.central_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36) NOT NULL,
    created_at timestamp with time zone,
    updated_at timestamp with time zone NOT NULL,
    occurred_at timestamp with time zone NOT NULL,
    agent_name character varying(50) NOT NULL,
    user_id character varying,
    event_type character varying(100) NOT NULL,
    subject_kind character varying(50),
    subject_id character varying(36),
    priority integer,
    title character varying(255),
    description text,
    details jsonb,
    metadata jsonb,
    correlation_id character varying(36),
    trace_id character varying(36),
    parent_memory_id character varying(36),
    numeric_value double precision,
    string_value text,
    tags jsonb,
    agent_metadata jsonb,
    relevant_agents character varying(255),
    cross_agent_validated boolean,
    validation_count integer,
    stick_anxiety_level double precision,
    never_forget boolean,
    times_referenced integer,
    last_referenced timestamp without time zone,
    successful_applications integer
);


--
-- Name: central_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.central_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: central_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.central_memory_bank_id_seq OWNED BY public.central_memory_bank.id;


--
-- Name: hamsters_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.hamsters_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    contributing_hamster character varying(10) NOT NULL,
    infrastructure_pattern jsonb,
    duct_tape_solution jsonb,
    problem_type character varying(100) NOT NULL,
    solution_effectiveness double precision,
    beer_consumption_correlation jsonb,
    steve_contribution jsonb,
    bob_contribution jsonb,
    carl_contribution jsonb,
    risk_pattern jsonb,
    safety_protocol_adjustment jsonb,
    stick_anxiety_trigger jsonb,
    supply_raids_count integer,
    beer_consumed_count integer,
    duct_tape_used_count integer,
    interventions_count integer,
    last_raid_timestamp timestamp with time zone,
    last_intervention_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: hamsters_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.hamsters_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: hamsters_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.hamsters_memory_bank_id_seq OWNED BY public.hamsters_memory_bank.id;


--
-- Name: learned_sequences; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.learned_sequences (
    id integer NOT NULL,
    agent_name character varying(50) NOT NULL,
    system_id character varying(255) NOT NULL,
    goal character varying(100) NOT NULL,
    primitives json NOT NULL,
    effectiveness_score double precision,
    confidence double precision,
    sample_size integer,
    success_count integer,
    success_rate double precision,
    avg_improvement double precision,
    avg_duration_seconds double precision,
    intervention_type character varying(20),
    trigger_severity double precision,
    trigger_trend character varying(20),
    first_discovered timestamp without time zone DEFAULT now(),
    last_used timestamp without time zone,
    stick_validated boolean,
    promoted boolean,
    deprecated boolean,
    deprecated_reason character varying(500),
    learned_from character varying(50),
    parent_sequence_id integer
);


--
-- Name: learned_sequences_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.learned_sequences_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: learned_sequences_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.learned_sequences_id_seq OWNED BY public.learned_sequences.id;


--
-- Name: memory_bank_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.memory_bank_metadata (
    id integer NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    total_memories integer,
    central_bank_memories integer,
    cross_agent_learnings integer,
    hawkington_memories integer,
    snail_memories integer,
    hamsters_memories integer,
    qsp_memories integer,
    vic20_memories integer,
    stick_memories integer,
    successful_transfers integer,
    failed_transfers integer,
    average_effectiveness_score double precision,
    memory_bank_health_score double precision,
    stick_anxiety_level double precision,
    memory_retrieval_speed_ms double precision,
    cross_agent_query_speed_ms double precision,
    learning_application_success_rate double precision
);


--
-- Name: memory_bank_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.memory_bank_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: memory_bank_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.memory_bank_metadata_id_seq OWNED BY public.memory_bank_metadata.id;


--
-- Name: meth_snail_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.meth_snail_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    optimization_pattern jsonb,
    caffeine_level_context double precision,
    shell_spin_correlation jsonb,
    energy_drink_effectiveness jsonb,
    jitter_threshold_learning jsonb,
    crash_prevention_patterns jsonb,
    performance_improvement double precision,
    resource_efficiency_gain double precision,
    optimization_duration double precision,
    confidence_level double precision,
    replication_success_rate double precision,
    energy_drinks_consumed_count integer,
    shell_spins_count integer,
    optimizations_applied_count integer,
    last_energy_drink_timestamp timestamp with time zone,
    last_shell_spin_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: meth_snail_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.meth_snail_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: meth_snail_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.meth_snail_memory_bank_id_seq OWNED BY public.meth_snail_memory_bank.id;


--
-- Name: metric_pattern_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metric_pattern_history (
    id integer NOT NULL,
    system_id character varying(255) NOT NULL,
    metric_name character varying(100) NOT NULL,
    starting_value double precision NOT NULL,
    starting_timestamp timestamp without time zone NOT NULL,
    value_15min_later double precision,
    value_30min_later double precision,
    value_1hr_later double precision,
    context json,
    context_fingerprint character varying(255)
);


--
-- Name: metric_pattern_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.metric_pattern_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: metric_pattern_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.metric_pattern_history_id_seq OWNED BY public.metric_pattern_history.id;


--
-- Name: metrics_daily; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metrics_daily (
    id integer NOT NULL,
    user_id character varying NOT NULL,
    date timestamp with time zone NOT NULL,
    daily_meth_snail_shell_spins integer,
    daily_hawkington_monocle_yeets integer,
    daily_stick_hyperventilations integer,
    daily_quantum_shadow_phasings integer,
    daily_vic20_wisdom_dispensed integer,
    daily_ai_incident_count integer,
    daily_ai_incident_type character varying,
    daily_ai_incident_reason character varying,
    daily_ai_incident_data_quality_score double precision,
    daily_ai_incident_summary json,
    cpu_avg double precision,
    cpu_peak_time timestamp without time zone,
    cpu_peak_value double precision,
    memory_avg double precision,
    memory_peak_time timestamp without time zone,
    memory_peak_value double precision,
    disk_avg double precision,
    network_bytes_total double precision,
    usage_pattern json
);


--
-- Name: metrics_daily_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.metrics_daily_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: metrics_daily_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.metrics_daily_id_seq OWNED BY public.metrics_daily.id;


--
-- Name: metrics_hourly; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.metrics_hourly (
    id integer NOT NULL,
    user_id character varying NOT NULL,
    hour_start timestamp with time zone NOT NULL,
    meth_snail_shell_spins integer,
    hawkington_monocle_yeets integer,
    stick_hyperventilations integer,
    quantum_shadow_phasings integer,
    vic20_wisdom_dispensed integer,
    ai_agent_incident_count integer,
    ai_agent_incident_type character varying,
    ai_agent_incident_reason character varying,
    ai_agent_incident_data_quality_score double precision,
    ai_agent_incident_summary json,
    cpu_avg double precision,
    cpu_max double precision,
    cpu_min double precision,
    memory_avg double precision,
    memory_max double precision,
    memory_min double precision,
    disk_avg double precision,
    network_bytes_total double precision,
    ai_events json,
    anomaly_count integer,
    sample_count integer,
    created_at timestamp with time zone
);


--
-- Name: metrics_hourly_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.metrics_hourly_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: metrics_hourly_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.metrics_hourly_id_seq OWNED BY public.metrics_hourly.id;


--
-- Name: quantum_shadow_people_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.quantum_shadow_people_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    phase_pattern jsonb,
    quantum_signature jsonb,
    dimensional_correlation jsonb,
    threat_pattern_recognition jsonb,
    network_anomaly_signatures jsonb,
    phase_shift_effectiveness double precision,
    tequila_jello_correlation jsonb,
    comprehensibility_score double precision,
    quantum_confidence double precision,
    parallel_universe_validation jsonb,
    telepathic_hamster_confirmation boolean,
    dimensional_shifts_count integer,
    quantum_fixes_count integer,
    tequila_jello_shots_count integer,
    last_dimensional_shift_timestamp timestamp with time zone,
    last_quantum_fix_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: quantum_shadow_people_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.quantum_shadow_people_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: quantum_shadow_people_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.quantum_shadow_people_memory_bank_id_seq OWNED BY public.quantum_shadow_people_memory_bank.id;


--
-- Name: sir_hawkington_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sir_hawkington_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    memory_category character varying(50) NOT NULL,
    data_quality_pattern jsonb,
    triage_decision_context jsonb,
    quality_threshold_adjustment jsonb,
    accuracy_improvement double precision,
    false_positive_reduction double precision,
    monocle_yeets_count integer,
    alerts_generated_count integer,
    triage_decisions_count integer,
    last_yeet_timestamp timestamp with time zone,
    last_alert_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: sir_hawkington_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sir_hawkington_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sir_hawkington_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sir_hawkington_memory_bank_id_seq OWNED BY public.sir_hawkington_memory_bank.id;


--
-- Name: system_metrics; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_metrics (
    id integer NOT NULL,
    user_id character varying NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    cpu_usage double precision NOT NULL,
    memory_usage double precision NOT NULL,
    disk_usage double precision NOT NULL,
    network json,
    process_count integer,
    additional_metrics json
);


--
-- Name: system_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.system_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: system_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.system_metrics_id_seq OWNED BY public.system_metrics.id;


--
-- Name: the_stick_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.the_stick_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    anxiety_pattern jsonb,
    compliance_tracking jsonb,
    pattern_recognition jsonb,
    hamster_behavior_log jsonb,
    paper_bag_moments jsonb,
    compliance_violations jsonb,
    anxiety_level double precision,
    hyperventilation_count integer,
    pattern_match_accuracy double precision,
    compliance_score double precision,
    bob_proximity_alerts integer,
    paper_bags_consumed_count integer,
    hamster_encounters_count integer,
    anxiety_spikes_count integer,
    last_paper_bag_timestamp timestamp with time zone,
    last_hamster_encounter_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: the_stick_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.the_stick_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: the_stick_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.the_stick_memory_bank_id_seq OWNED BY public.the_stick_memory_bank.id;


--
-- Name: threshold_learning_records; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.threshold_learning_records (
    id integer NOT NULL,
    system_id character varying(255) NOT NULL,
    agent_name character varying(50) NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_value double precision NOT NULL,
    threshold_level character varying(20) NOT NULL,
    action_taken character varying(100),
    outcome_success boolean,
    system_state json,
    context json,
    time_to_critical double precision,
    was_false_alarm boolean DEFAULT false,
    should_have_acted_sooner boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT now()
);


--
-- Name: threshold_learning_records_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.threshold_learning_records_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: threshold_learning_records_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.threshold_learning_records_id_seq OWNED BY public.threshold_learning_records.id;


--
-- Name: user_learning_patterns; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_learning_patterns (
    id integer NOT NULL,
    pattern_id character varying(36),
    user_id character varying NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    interaction_pattern jsonb,
    learning_preference jsonb,
    response_patterns jsonb,
    most_effective_agent character varying(50),
    communication_style_preference jsonb,
    complexity_tolerance double precision,
    skill_improvement_areas jsonb,
    knowledge_gaps jsonb,
    success_patterns jsonb,
    agent_effectiveness_ranking jsonb,
    collaborative_preferences jsonb
);


--
-- Name: user_learning_patterns_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.user_learning_patterns_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: user_learning_patterns_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.user_learning_patterns_id_seq OWNED BY public.user_learning_patterns.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id character varying(36) NOT NULL,
    email character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    is_onboarded boolean,
    onboarding_progress integer,
    onboarding_data json,
    onboarding_started_at timestamp with time zone,
    onboarding_last_step_at timestamp with time zone,
    onboarding_abandoned_count integer NOT NULL,
    onboarding_step_timestamps json,
    onboarding_abandonment_reasons json,
    onboarding_device_info json,
    onboarding_referral_source character varying(100),
    preview_agent_selected character varying(20),
    preview_started_at timestamp with time zone,
    preview_expires_at timestamp with time zone,
    preview_conversion_emails_sent json,
    preview_converted_at timestamp with time zone,
    email_campaign_responses json,
    last_engagement_at timestamp with time zone,
    first_name character varying(50),
    last_name character varying(50),
    company_name character varying(100),
    job_title character varying(50),
    system_name character varying(100),
    avatar character varying(50),
    agent_preferences json,
    monitoring_preferences json,
    system_profile json,
    agent_installed boolean,
    agent_version character varying(20),
    installation_method character varying(50),
    permissions_granted_at timestamp with time zone,
    is_active boolean,
    is_verified boolean,
    is_enterprise boolean,
    last_login timestamp with time zone,
    failed_login_attempts integer,
    lockout_until timestamp with time zone,
    total_interactions integer,
    patterns_learned integer,
    decisions_made integer,
    created_at timestamp with time zone,
    updated_at timestamp with time zone
);


--
-- Name: vic20_memory_bank; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.vic20_memory_bank (
    id integer NOT NULL,
    memory_id character varying(36),
    user_id character varying(255) NOT NULL,
    "timestamp" timestamp with time zone NOT NULL,
    coordination_pattern jsonb,
    mediation_insight jsonb,
    ancient_wisdom_application jsonb,
    conflict_resolution_method jsonb,
    agent_harmony_score double precision,
    coordination_efficiency double precision,
    agent_personality_patterns jsonb,
    successful_mediation_strategies jsonb,
    failure_prevention_wisdom jsonb,
    retro_computing_insight jsonb,
    simplicity_effectiveness double precision,
    modern_complexity_critique jsonb,
    coordinations_count integer,
    mediations_count integer,
    wisdom_dispensed_count integer,
    last_coordination_timestamp timestamp with time zone,
    last_wisdom_timestamp timestamp with time zone,
    shared_with_central boolean,
    central_memory_id character varying(36)
);


--
-- Name: vic20_memory_bank_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.vic20_memory_bank_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: vic20_memory_bank_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.vic20_memory_bank_id_seq OWNED BY public.vic20_memory_bank.id;


--
-- Name: action_outcome_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_outcome_records ALTER COLUMN id SET DEFAULT nextval('public.action_outcome_records_id_seq'::regclass);


--
-- Name: agent_decision_vectors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_decision_vectors ALTER COLUMN id SET DEFAULT nextval('public.agent_decision_vectors_id_seq'::regclass);


--
-- Name: agent_interaction_vectors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_interaction_vectors ALTER COLUMN id SET DEFAULT nextval('public.agent_interaction_vectors_id_seq'::regclass);


--
-- Name: agent_learning_interactions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_interactions ALTER COLUMN id SET DEFAULT nextval('public.agent_learning_interactions_id_seq'::regclass);


--
-- Name: agent_learning_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_records ALTER COLUMN id SET DEFAULT nextval('public.agent_learning_records_id_seq'::regclass);


--
-- Name: agent_pattern_vectors id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_pattern_vectors ALTER COLUMN id SET DEFAULT nextval('public.agent_pattern_vectors_id_seq'::regclass);


--
-- Name: central_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.central_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.central_memory_bank_id_seq'::regclass);


--
-- Name: hamsters_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hamsters_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.hamsters_memory_bank_id_seq'::regclass);


--
-- Name: learned_sequences id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learned_sequences ALTER COLUMN id SET DEFAULT nextval('public.learned_sequences_id_seq'::regclass);


--
-- Name: memory_bank_metadata id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.memory_bank_metadata ALTER COLUMN id SET DEFAULT nextval('public.memory_bank_metadata_id_seq'::regclass);


--
-- Name: meth_snail_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.meth_snail_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.meth_snail_memory_bank_id_seq'::regclass);


--
-- Name: metric_pattern_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metric_pattern_history ALTER COLUMN id SET DEFAULT nextval('public.metric_pattern_history_id_seq'::regclass);


--
-- Name: metrics_daily id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_daily ALTER COLUMN id SET DEFAULT nextval('public.metrics_daily_id_seq'::regclass);


--
-- Name: metrics_hourly id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_hourly ALTER COLUMN id SET DEFAULT nextval('public.metrics_hourly_id_seq'::regclass);


--
-- Name: quantum_shadow_people_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_shadow_people_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.quantum_shadow_people_memory_bank_id_seq'::regclass);


--
-- Name: sir_hawkington_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sir_hawkington_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.sir_hawkington_memory_bank_id_seq'::regclass);


--
-- Name: system_metrics id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_metrics ALTER COLUMN id SET DEFAULT nextval('public.system_metrics_id_seq'::regclass);


--
-- Name: the_stick_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.the_stick_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.the_stick_memory_bank_id_seq'::regclass);


--
-- Name: threshold_learning_records id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.threshold_learning_records ALTER COLUMN id SET DEFAULT nextval('public.threshold_learning_records_id_seq'::regclass);


--
-- Name: user_learning_patterns id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_learning_patterns ALTER COLUMN id SET DEFAULT nextval('public.user_learning_patterns_id_seq'::regclass);


--
-- Name: vic20_memory_bank id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vic20_memory_bank ALTER COLUMN id SET DEFAULT nextval('public.vic20_memory_bank_id_seq'::regclass);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: action_outcome_records pk_action_outcome_records; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.action_outcome_records
    ADD CONSTRAINT pk_action_outcome_records PRIMARY KEY (id);


--
-- Name: agent_decision_vectors pk_agent_decision_vectors; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_decision_vectors
    ADD CONSTRAINT pk_agent_decision_vectors PRIMARY KEY (id);


--
-- Name: agent_global_patterns pk_agent_global_patterns; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_global_patterns
    ADD CONSTRAINT pk_agent_global_patterns PRIMARY KEY (id);


--
-- Name: agent_interaction_vectors pk_agent_interaction_vectors; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_interaction_vectors
    ADD CONSTRAINT pk_agent_interaction_vectors PRIMARY KEY (id);


--
-- Name: agent_learning_interactions pk_agent_learning_interactions; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_interactions
    ADD CONSTRAINT pk_agent_learning_interactions PRIMARY KEY (id);


--
-- Name: agent_learning_records pk_agent_learning_records; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_records
    ADD CONSTRAINT pk_agent_learning_records PRIMARY KEY (id);


--
-- Name: agent_memories pk_agent_memories; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_memories
    ADD CONSTRAINT pk_agent_memories PRIMARY KEY (id);


--
-- Name: agent_pattern_vectors pk_agent_pattern_vectors; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_pattern_vectors
    ADD CONSTRAINT pk_agent_pattern_vectors PRIMARY KEY (id);


--
-- Name: central_memory_bank pk_central_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.central_memory_bank
    ADD CONSTRAINT pk_central_memory_bank PRIMARY KEY (id);


--
-- Name: hamsters_memory_bank pk_hamsters_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hamsters_memory_bank
    ADD CONSTRAINT pk_hamsters_memory_bank PRIMARY KEY (id);


--
-- Name: learned_sequences pk_learned_sequences; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.learned_sequences
    ADD CONSTRAINT pk_learned_sequences PRIMARY KEY (id);


--
-- Name: memory_bank_metadata pk_memory_bank_metadata; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.memory_bank_metadata
    ADD CONSTRAINT pk_memory_bank_metadata PRIMARY KEY (id);


--
-- Name: meth_snail_memory_bank pk_meth_snail_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.meth_snail_memory_bank
    ADD CONSTRAINT pk_meth_snail_memory_bank PRIMARY KEY (id);


--
-- Name: metric_pattern_history pk_metric_pattern_history; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metric_pattern_history
    ADD CONSTRAINT pk_metric_pattern_history PRIMARY KEY (id);


--
-- Name: metrics_daily pk_metrics_daily; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_daily
    ADD CONSTRAINT pk_metrics_daily PRIMARY KEY (id);


--
-- Name: metrics_hourly pk_metrics_hourly; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.metrics_hourly
    ADD CONSTRAINT pk_metrics_hourly PRIMARY KEY (id);


--
-- Name: quantum_shadow_people_memory_bank pk_quantum_shadow_people_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_shadow_people_memory_bank
    ADD CONSTRAINT pk_quantum_shadow_people_memory_bank PRIMARY KEY (id);


--
-- Name: sir_hawkington_memory_bank pk_sir_hawkington_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sir_hawkington_memory_bank
    ADD CONSTRAINT pk_sir_hawkington_memory_bank PRIMARY KEY (id);


--
-- Name: system_metrics pk_system_metrics; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT pk_system_metrics PRIMARY KEY (id);


--
-- Name: the_stick_memory_bank pk_the_stick_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.the_stick_memory_bank
    ADD CONSTRAINT pk_the_stick_memory_bank PRIMARY KEY (id);


--
-- Name: threshold_learning_records pk_threshold_learning_records; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.threshold_learning_records
    ADD CONSTRAINT pk_threshold_learning_records PRIMARY KEY (id);


--
-- Name: user_learning_patterns pk_user_learning_patterns; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_learning_patterns
    ADD CONSTRAINT pk_user_learning_patterns PRIMARY KEY (id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: vic20_memory_bank pk_vic20_memory_bank; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vic20_memory_bank
    ADD CONSTRAINT pk_vic20_memory_bank PRIMARY KEY (id);


--
-- Name: agent_decision_vectors uq_agent_decision_vectors_vector_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_decision_vectors
    ADD CONSTRAINT uq_agent_decision_vectors_vector_id UNIQUE (vector_id);


--
-- Name: agent_interaction_vectors uq_agent_interaction_vectors_vector_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_interaction_vectors
    ADD CONSTRAINT uq_agent_interaction_vectors_vector_id UNIQUE (vector_id);


--
-- Name: agent_learning_interactions uq_agent_learning_interactions_interaction_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_interactions
    ADD CONSTRAINT uq_agent_learning_interactions_interaction_id UNIQUE (interaction_id);


--
-- Name: agent_pattern_vectors uq_agent_pattern_vectors_vector_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_pattern_vectors
    ADD CONSTRAINT uq_agent_pattern_vectors_vector_id UNIQUE (vector_id);


--
-- Name: central_memory_bank uq_central_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.central_memory_bank
    ADD CONSTRAINT uq_central_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: hamsters_memory_bank uq_hamsters_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hamsters_memory_bank
    ADD CONSTRAINT uq_hamsters_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: meth_snail_memory_bank uq_meth_snail_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.meth_snail_memory_bank
    ADD CONSTRAINT uq_meth_snail_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: quantum_shadow_people_memory_bank uq_quantum_shadow_people_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_shadow_people_memory_bank
    ADD CONSTRAINT uq_quantum_shadow_people_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: sir_hawkington_memory_bank uq_sir_hawkington_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sir_hawkington_memory_bank
    ADD CONSTRAINT uq_sir_hawkington_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: the_stick_memory_bank uq_the_stick_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.the_stick_memory_bank
    ADD CONSTRAINT uq_the_stick_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: user_learning_patterns uq_user_learning_patterns_pattern_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_learning_patterns
    ADD CONSTRAINT uq_user_learning_patterns_pattern_id UNIQUE (pattern_id);


--
-- Name: vic20_memory_bank uq_vic20_memory_bank_memory_id; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vic20_memory_bank
    ADD CONSTRAINT uq_vic20_memory_bank_memory_id UNIQUE (memory_id);


--
-- Name: agent_decision_vectors_embedding_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_decision_vectors_embedding_idx ON public.agent_decision_vectors USING hnsw (((embedding)::public.vector(384)) public.vector_cosine_ops) WITH (m='16', ef_construction='64');


--
-- Name: agent_interaction_vectors_embedding_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_interaction_vectors_embedding_idx ON public.agent_interaction_vectors USING hnsw (((embedding)::public.vector(384)) public.vector_cosine_ops) WITH (m='16', ef_construction='64');


--
-- Name: agent_pattern_vectors_embedding_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_pattern_vectors_embedding_idx ON public.agent_pattern_vectors USING hnsw (((embedding)::public.vector(384)) public.vector_cosine_ops) WITH (m='16', ef_construction='64');


--
-- Name: idx_agent_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_action ON public.agent_learning_records USING btree (agent_name, action);


--
-- Name: idx_agent_action_pattern; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_action_pattern ON public.action_outcome_records USING btree (agent_name, action, metric_pattern_fingerprint);


--
-- Name: idx_agent_decision_vectors_agent_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_decision_vectors_agent_time ON public.agent_decision_vectors USING btree (agent_name, occurred_at DESC);


--
-- Name: idx_agent_decision_vectors_metadata; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_decision_vectors_metadata ON public.agent_decision_vectors USING gin (metadata);


--
-- Name: idx_agent_decision_vectors_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_decision_vectors_type ON public.agent_decision_vectors USING btree (decision_type, occurred_at DESC);


--
-- Name: idx_agent_decision_vectors_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_decision_vectors_user ON public.agent_decision_vectors USING btree (user_id, occurred_at DESC);


--
-- Name: idx_agent_event_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_event_time ON public.central_memory_bank USING btree (agent_name, event_type, occurred_at);


--
-- Name: idx_agent_fingerprint_success; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_fingerprint_success ON public.agent_learning_records USING btree (agent_name, fingerprint_l3, success);


--
-- Name: idx_agent_interaction_vectors_pair; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_interaction_vectors_pair ON public.agent_interaction_vectors USING btree (primary_agent, secondary_agent, occurred_at DESC);


--
-- Name: idx_agent_interaction_vectors_primary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_interaction_vectors_primary ON public.agent_interaction_vectors USING btree (primary_agent, occurred_at DESC);


--
-- Name: idx_agent_interaction_vectors_secondary; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_interaction_vectors_secondary ON public.agent_interaction_vectors USING btree (secondary_agent, occurred_at DESC);


--
-- Name: idx_agent_interaction_vectors_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_interaction_vectors_user ON public.agent_interaction_vectors USING btree (user_id, occurred_at DESC);


--
-- Name: idx_agent_pattern_vectors_agent_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_pattern_vectors_agent_type ON public.agent_pattern_vectors USING btree (agent_name, pattern_type);


--
-- Name: idx_agent_pattern_vectors_data; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_pattern_vectors_data ON public.agent_pattern_vectors USING gin (pattern_data);


--
-- Name: idx_agent_pattern_vectors_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_pattern_vectors_user ON public.agent_pattern_vectors USING btree (user_id, last_observed DESC);


--
-- Name: idx_agent_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_agent_user ON public.central_memory_bank USING btree (agent_name, user_id);


--
-- Name: idx_ai_incident_count; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ai_incident_count ON public.metrics_daily USING btree (daily_ai_incident_count, daily_ai_incident_type, daily_ai_incident_reason);


--
-- Name: idx_ali_adaptation_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ali_adaptation_gin ON public.agent_learning_interactions USING gin (adaptation_method jsonb_path_ops);


--
-- Name: idx_ali_appctx_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ali_appctx_gin ON public.agent_learning_interactions USING gin (application_context jsonb_path_ops);


--
-- Name: idx_cmb_details_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cmb_details_gin ON public.central_memory_bank USING gin (details jsonb_path_ops);


--
-- Name: idx_cmb_metadata_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cmb_metadata_gin ON public.central_memory_bank USING gin (metadata jsonb_path_ops);


--
-- Name: idx_cmb_tags_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cmb_tags_gin ON public.central_memory_bank USING gin (tags jsonb_path_ops);


--
-- Name: idx_context_pattern; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_context_pattern ON public.metric_pattern_history USING btree (context_fingerprint, starting_value);


--
-- Name: idx_correlation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_correlation ON public.central_memory_bank USING btree (correlation_id, trace_id);


--
-- Name: idx_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_created ON public.agent_learning_records USING btree (created_at);


--
-- Name: idx_event_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_event_timestamp ON public.central_memory_bank USING btree (event_type, occurred_at);


--
-- Name: idx_fingerprint_l1; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fingerprint_l1 ON public.agent_learning_records USING btree (fingerprint_l1);


--
-- Name: idx_fingerprint_l2; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fingerprint_l2 ON public.agent_learning_records USING btree (fingerprint_l2);


--
-- Name: idx_fingerprint_l3; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_fingerprint_l3 ON public.agent_learning_records USING btree (fingerprint_l3);


--
-- Name: idx_hamsters_contributor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hamsters_contributor ON public.hamsters_memory_bank USING btree (contributing_hamster, problem_type);


--
-- Name: idx_hamsters_effectiveness; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hamsters_effectiveness ON public.hamsters_memory_bank USING btree (solution_effectiveness, "timestamp");


--
-- Name: idx_hawkington_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hawkington_category ON public.sir_hawkington_memory_bank USING btree (memory_category, "timestamp");


--
-- Name: idx_hawkington_shared; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hawkington_shared ON public.sir_hawkington_memory_bank USING btree (shared_with_central, central_memory_id);


--
-- Name: idx_learned_seq_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_learned_seq_active ON public.learned_sequences USING btree (agent_name, goal, deprecated, confidence);


--
-- Name: idx_learned_seq_agent_goal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_learned_seq_agent_goal ON public.learned_sequences USING btree (agent_name, goal);


--
-- Name: idx_learned_seq_system_goal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_learned_seq_system_goal ON public.learned_sequences USING btree (system_id, goal);


--
-- Name: idx_learning_effectiveness; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_learning_effectiveness ON public.agent_learning_interactions USING btree (effectiveness_score, transfer_success);


--
-- Name: idx_learning_transfer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_learning_transfer ON public.agent_learning_interactions USING btree (source_agent, target_agent, learning_type);


--
-- Name: idx_mb_effectiveness; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mb_effectiveness ON public.memory_bank_metadata USING btree (average_effectiveness_score, successful_transfers);


--
-- Name: idx_memory_health; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_memory_health ON public.memory_bank_metadata USING btree (memory_bank_health_score, "timestamp");


--
-- Name: idx_memory_importance; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_memory_importance ON public.central_memory_bank USING btree (priority, never_forget);


--
-- Name: idx_metric_queries; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_metric_queries ON public.central_memory_bank USING btree (event_type, occurred_at, subject_kind);


--
-- Name: idx_metric_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_metric_value ON public.threshold_learning_records USING btree (metric_name, metric_value);


--
-- Name: idx_pattern_success; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_pattern_success ON public.action_outcome_records USING btree (metric_pattern_fingerprint, success);


--
-- Name: idx_priority_access; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_priority_access ON public.central_memory_bank USING btree (priority, last_referenced);


--
-- Name: idx_process_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_process_category ON public.agent_learning_records USING btree (process_category);


--
-- Name: idx_qsp_comprehensibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qsp_comprehensibility ON public.quantum_shadow_people_memory_bank USING btree (comprehensibility_score, phase_shift_effectiveness);


--
-- Name: idx_qsp_phase; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_qsp_phase ON public.quantum_shadow_people_memory_bank USING btree (phase_pattern, quantum_confidence);


--
-- Name: idx_snail_caffeine; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_snail_caffeine ON public.meth_snail_memory_bank USING btree (caffeine_level_context, "timestamp");


--
-- Name: idx_snail_optimization; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_snail_optimization ON public.meth_snail_memory_bank USING btree (optimization_pattern, performance_improvement);


--
-- Name: idx_stick_anxiety; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_stick_anxiety ON public.the_stick_memory_bank USING btree (anxiety_level, "timestamp");


--
-- Name: idx_stick_compliance; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_stick_compliance ON public.the_stick_memory_bank USING btree (compliance_score, "timestamp");


--
-- Name: idx_subject_reference; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_subject_reference ON public.central_memory_bank USING btree (subject_kind, subject_id);


--
-- Name: idx_success; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_success ON public.agent_learning_records USING btree (success);


--
-- Name: idx_system_metric_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metric_time ON public.threshold_learning_records USING btree (system_id, metric_name, created_at);


--
-- Name: idx_system_metric_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_system_metric_value ON public.metric_pattern_history USING btree (system_id, metric_name, starting_value);


--
-- Name: idx_ulp_learning_pref_gin; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ulp_learning_pref_gin ON public.user_learning_patterns USING gin (learning_preference jsonb_path_ops);


--
-- Name: idx_user_complexity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_complexity ON public.user_learning_patterns USING btree (user_id, complexity_tolerance);


--
-- Name: idx_user_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_date ON public.metrics_daily USING btree (user_id, date);


--
-- Name: idx_user_events; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_events ON public.central_memory_bank USING btree (user_id, occurred_at);


--
-- Name: idx_user_hour; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_hour ON public.metrics_hourly USING btree (user_id, hour_start);


--
-- Name: idx_user_patterns; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_user_patterns ON public.user_learning_patterns USING btree (user_id, most_effective_agent);


--
-- Name: idx_vic20_coordination; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vic20_coordination ON public.vic20_memory_bank USING btree (coordination_pattern, agent_harmony_score);


--
-- Name: idx_vic20_mediation; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_vic20_mediation ON public.vic20_memory_bank USING btree (mediation_insight, coordination_efficiency);


--
-- Name: ix_action_outcome_records_action; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_action ON public.action_outcome_records USING btree (action);


--
-- Name: ix_action_outcome_records_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_agent_name ON public.action_outcome_records USING btree (agent_name);


--
-- Name: ix_action_outcome_records_central_memory_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_central_memory_id ON public.action_outcome_records USING btree (central_memory_id);


--
-- Name: ix_action_outcome_records_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_created_at ON public.action_outcome_records USING btree (created_at);


--
-- Name: ix_action_outcome_records_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_id ON public.action_outcome_records USING btree (id);


--
-- Name: ix_action_outcome_records_metric_pattern_fingerprint; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_metric_pattern_fingerprint ON public.action_outcome_records USING btree (metric_pattern_fingerprint);


--
-- Name: ix_action_outcome_records_success; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_action_outcome_records_success ON public.action_outcome_records USING btree (success);


--
-- Name: ix_agent_global_patterns_pattern_key; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_global_patterns_pattern_key ON public.agent_global_patterns USING btree (pattern_key);


--
-- Name: ix_agent_learning_interactions_source_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_learning_interactions_source_agent ON public.agent_learning_interactions USING btree (source_agent);


--
-- Name: ix_agent_learning_interactions_target_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_learning_interactions_target_agent ON public.agent_learning_interactions USING btree (target_agent);


--
-- Name: ix_agent_learning_interactions_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_learning_interactions_timestamp ON public.agent_learning_interactions USING btree ("timestamp");


--
-- Name: ix_agent_learning_interactions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_learning_interactions_user_id ON public.agent_learning_interactions USING btree (user_id);


--
-- Name: ix_agent_memories_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_memories_agent_name ON public.agent_memories USING btree (agent_name);


--
-- Name: ix_agent_memories_memory_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_memories_memory_type ON public.agent_memories USING btree (memory_type);


--
-- Name: ix_agent_memories_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_memories_timestamp ON public.agent_memories USING btree ("timestamp");


--
-- Name: ix_agent_memories_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agent_memories_user_id ON public.agent_memories USING btree (user_id);


--
-- Name: ix_central_memory_bank_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_agent_name ON public.central_memory_bank USING btree (agent_name);


--
-- Name: ix_central_memory_bank_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_created_at ON public.central_memory_bank USING btree (created_at);


--
-- Name: ix_central_memory_bank_event_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_event_type ON public.central_memory_bank USING btree (event_type);


--
-- Name: ix_central_memory_bank_occurred_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_occurred_at ON public.central_memory_bank USING btree (occurred_at);


--
-- Name: ix_central_memory_bank_priority; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_priority ON public.central_memory_bank USING btree (priority);


--
-- Name: ix_central_memory_bank_subject_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_subject_id ON public.central_memory_bank USING btree (subject_id);


--
-- Name: ix_central_memory_bank_subject_kind; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_subject_kind ON public.central_memory_bank USING btree (subject_kind);


--
-- Name: ix_central_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_central_memory_bank_user_id ON public.central_memory_bank USING btree (user_id);


--
-- Name: ix_hamsters_memory_bank_contributing_hamster; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hamsters_memory_bank_contributing_hamster ON public.hamsters_memory_bank USING btree (contributing_hamster);


--
-- Name: ix_hamsters_memory_bank_problem_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hamsters_memory_bank_problem_type ON public.hamsters_memory_bank USING btree (problem_type);


--
-- Name: ix_hamsters_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hamsters_memory_bank_timestamp ON public.hamsters_memory_bank USING btree ("timestamp");


--
-- Name: ix_hamsters_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_hamsters_memory_bank_user_id ON public.hamsters_memory_bank USING btree (user_id);


--
-- Name: ix_learned_sequences_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_learned_sequences_agent_name ON public.learned_sequences USING btree (agent_name);


--
-- Name: ix_learned_sequences_goal; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_learned_sequences_goal ON public.learned_sequences USING btree (goal);


--
-- Name: ix_learned_sequences_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_learned_sequences_id ON public.learned_sequences USING btree (id);


--
-- Name: ix_learned_sequences_system_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_learned_sequences_system_id ON public.learned_sequences USING btree (system_id);


--
-- Name: ix_mem_user_agent_type_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_mem_user_agent_type_time ON public.agent_memories USING btree (user_id, agent_name, memory_type, "timestamp");


--
-- Name: ix_memory_bank_metadata_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_memory_bank_metadata_timestamp ON public.memory_bank_metadata USING btree ("timestamp");


--
-- Name: ix_meth_snail_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_meth_snail_memory_bank_timestamp ON public.meth_snail_memory_bank USING btree ("timestamp");


--
-- Name: ix_meth_snail_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_meth_snail_memory_bank_user_id ON public.meth_snail_memory_bank USING btree (user_id);


--
-- Name: ix_metric_pattern_history_context_fingerprint; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_context_fingerprint ON public.metric_pattern_history USING btree (context_fingerprint);


--
-- Name: ix_metric_pattern_history_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_id ON public.metric_pattern_history USING btree (id);


--
-- Name: ix_metric_pattern_history_metric_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_metric_name ON public.metric_pattern_history USING btree (metric_name);


--
-- Name: ix_metric_pattern_history_starting_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_starting_timestamp ON public.metric_pattern_history USING btree (starting_timestamp);


--
-- Name: ix_metric_pattern_history_starting_value; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_starting_value ON public.metric_pattern_history USING btree (starting_value);


--
-- Name: ix_metric_pattern_history_system_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metric_pattern_history_system_id ON public.metric_pattern_history USING btree (system_id);


--
-- Name: ix_metrics_daily_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_daily_date ON public.metrics_daily USING btree (date);


--
-- Name: ix_metrics_daily_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_daily_id ON public.metrics_daily USING btree (id);


--
-- Name: ix_metrics_daily_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_daily_user_id ON public.metrics_daily USING btree (user_id);


--
-- Name: ix_metrics_hourly_hour_start; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_hourly_hour_start ON public.metrics_hourly USING btree (hour_start);


--
-- Name: ix_metrics_hourly_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_hourly_id ON public.metrics_hourly USING btree (id);


--
-- Name: ix_metrics_hourly_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_metrics_hourly_user_id ON public.metrics_hourly USING btree (user_id);


--
-- Name: ix_quantum_shadow_people_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_quantum_shadow_people_memory_bank_timestamp ON public.quantum_shadow_people_memory_bank USING btree ("timestamp");


--
-- Name: ix_quantum_shadow_people_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_quantum_shadow_people_memory_bank_user_id ON public.quantum_shadow_people_memory_bank USING btree (user_id);


--
-- Name: ix_sir_hawkington_memory_bank_memory_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sir_hawkington_memory_bank_memory_category ON public.sir_hawkington_memory_bank USING btree (memory_category);


--
-- Name: ix_sir_hawkington_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sir_hawkington_memory_bank_timestamp ON public.sir_hawkington_memory_bank USING btree ("timestamp");


--
-- Name: ix_sir_hawkington_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_sir_hawkington_memory_bank_user_id ON public.sir_hawkington_memory_bank USING btree (user_id);


--
-- Name: ix_system_metrics_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_system_metrics_id ON public.system_metrics USING btree (id);


--
-- Name: ix_the_stick_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_the_stick_memory_bank_timestamp ON public.the_stick_memory_bank USING btree ("timestamp");


--
-- Name: ix_the_stick_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_the_stick_memory_bank_user_id ON public.the_stick_memory_bank USING btree (user_id);


--
-- Name: ix_threshold_learning_records_agent_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_threshold_learning_records_agent_name ON public.threshold_learning_records USING btree (agent_name);


--
-- Name: ix_threshold_learning_records_created_at; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_threshold_learning_records_created_at ON public.threshold_learning_records USING btree (created_at);


--
-- Name: ix_threshold_learning_records_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_threshold_learning_records_id ON public.threshold_learning_records USING btree (id);


--
-- Name: ix_threshold_learning_records_metric_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_threshold_learning_records_metric_name ON public.threshold_learning_records USING btree (metric_name);


--
-- Name: ix_threshold_learning_records_system_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_threshold_learning_records_system_id ON public.threshold_learning_records USING btree (system_id);


--
-- Name: ix_user_learning_patterns_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_learning_patterns_timestamp ON public.user_learning_patterns USING btree ("timestamp");


--
-- Name: ix_user_learning_patterns_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_user_learning_patterns_user_id ON public.user_learning_patterns USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_vic20_memory_bank_timestamp; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vic20_memory_bank_timestamp ON public.vic20_memory_bank USING btree ("timestamp");


--
-- Name: ix_vic20_memory_bank_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_vic20_memory_bank_user_id ON public.vic20_memory_bank USING btree (user_id);


--
-- Name: agent_learning_interactions fk_agent_learning_interactions_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_learning_interactions
    ADD CONSTRAINT fk_agent_learning_interactions_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: agent_memories fk_agent_memories_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_memories
    ADD CONSTRAINT fk_agent_memories_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: central_memory_bank fk_central_memory_bank_parent_memory_id_central_memory_bank; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.central_memory_bank
    ADD CONSTRAINT fk_central_memory_bank_parent_memory_id_central_memory_bank FOREIGN KEY (parent_memory_id) REFERENCES public.central_memory_bank(memory_id);


--
-- Name: central_memory_bank fk_central_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.central_memory_bank
    ADD CONSTRAINT fk_central_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: hamsters_memory_bank fk_hamsters_memory_bank_central_memory_id_central_memory_bank; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hamsters_memory_bank
    ADD CONSTRAINT fk_hamsters_memory_bank_central_memory_id_central_memory_bank FOREIGN KEY (central_memory_id) REFERENCES public.central_memory_bank(memory_id);


--
-- Name: hamsters_memory_bank fk_hamsters_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.hamsters_memory_bank
    ADD CONSTRAINT fk_hamsters_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: meth_snail_memory_bank fk_meth_snail_memory_bank_central_memory_id_central_memory_bank; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.meth_snail_memory_bank
    ADD CONSTRAINT fk_meth_snail_memory_bank_central_memory_id_central_memory_bank FOREIGN KEY (central_memory_id) REFERENCES public.central_memory_bank(memory_id);


--
-- Name: meth_snail_memory_bank fk_meth_snail_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.meth_snail_memory_bank
    ADD CONSTRAINT fk_meth_snail_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: quantum_shadow_people_memory_bank fk_quantum_shadow_people_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.quantum_shadow_people_memory_bank
    ADD CONSTRAINT fk_quantum_shadow_people_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: sir_hawkington_memory_bank fk_sir_hawkington_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sir_hawkington_memory_bank
    ADD CONSTRAINT fk_sir_hawkington_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: system_metrics fk_system_metrics_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_metrics
    ADD CONSTRAINT fk_system_metrics_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: the_stick_memory_bank fk_the_stick_memory_bank_central_memory_id_central_memory_bank; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.the_stick_memory_bank
    ADD CONSTRAINT fk_the_stick_memory_bank_central_memory_id_central_memory_bank FOREIGN KEY (central_memory_id) REFERENCES public.central_memory_bank(memory_id);


--
-- Name: the_stick_memory_bank fk_the_stick_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.the_stick_memory_bank
    ADD CONSTRAINT fk_the_stick_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_learning_patterns fk_user_learning_patterns_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_learning_patterns
    ADD CONSTRAINT fk_user_learning_patterns_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: vic20_memory_bank fk_vic20_memory_bank_central_memory_id_central_memory_bank; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vic20_memory_bank
    ADD CONSTRAINT fk_vic20_memory_bank_central_memory_id_central_memory_bank FOREIGN KEY (central_memory_id) REFERENCES public.central_memory_bank(memory_id);


--
-- Name: vic20_memory_bank fk_vic20_memory_bank_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.vic20_memory_bank
    ADD CONSTRAINT fk_vic20_memory_bank_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict ozeVgK7HM2mnmRc1QgxFTWNpuzv7AGhJ5w83sgi42ht9Ayo4dPqEHfz6xIIVNQJ

