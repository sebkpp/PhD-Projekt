--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-11-09 22:38:29

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 221 (class 1259 OID 16468)
-- Name: area_of_interest; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.area_of_interest (
    aoi character varying(255) NOT NULL,
    aoi_id integer NOT NULL,
    label character varying(255) NOT NULL
);


ALTER TABLE public.area_of_interest OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 16796)
-- Name: area_of_interest_aoi_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.area_of_interest_aoi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.area_of_interest_aoi_id_seq OWNER TO postgres;

--
-- TOC entry 5115 (class 0 OID 0)
-- Dependencies: 242
-- Name: area_of_interest_aoi_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.area_of_interest_aoi_id_seq OWNED BY public.area_of_interest.aoi_id;


--
-- TOC entry 237 (class 1259 OID 16696)
-- Name: avatar_visibility; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.avatar_visibility (
    avatar_visibility_id integer NOT NULL,
    avatar_visibility_name character varying(100) NOT NULL,
    label character varying(255) NOT NULL
);


ALTER TABLE public.avatar_visibility OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16695)
-- Name: avatar_visibility_avatar_visibility_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.avatar_visibility_avatar_visibility_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.avatar_visibility_avatar_visibility_id_seq OWNER TO postgres;

--
-- TOC entry 5116 (class 0 OID 0)
-- Dependencies: 236
-- Name: avatar_visibility_avatar_visibility_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.avatar_visibility_avatar_visibility_id_seq OWNED BY public.avatar_visibility.avatar_visibility_id;


--
-- TOC entry 217 (class 1259 OID 16389)
-- Name: experiment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment (
    description text,
    created_at timestamp without time zone DEFAULT now(),
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    researcher character varying(255),
    experiment_id integer NOT NULL,
    study_id integer NOT NULL
);


ALTER TABLE public.experiment OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16617)
-- Name: experiment_experiment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.experiment_experiment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.experiment_experiment_id_seq OWNER TO postgres;

--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 228
-- Name: experiment_experiment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.experiment_experiment_id_seq OWNED BY public.experiment.experiment_id;


--
-- TOC entry 257 (class 1259 OID 17735)
-- Name: experiment_questionnaire; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.experiment_questionnaire (
    experiment_id integer NOT NULL,
    questionnaire_id integer NOT NULL
);


ALTER TABLE public.experiment_questionnaire OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16473)
-- Name: eye_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.eye_tracking (
    starttime timestamp without time zone,
    endtime timestamp without time zone,
    duration integer,
    participant_id integer NOT NULL,
    handover_id integer NOT NULL,
    aoi_id integer NOT NULL,
    eye_tracking_id integer NOT NULL
);


ALTER TABLE public.eye_tracking OWNER TO postgres;

--
-- TOC entry 246 (class 1259 OID 16844)
-- Name: eye_tracking_eye_tracking_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.eye_tracking_eye_tracking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.eye_tracking_eye_tracking_id_seq OWNER TO postgres;

--
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 246
-- Name: eye_tracking_eye_tracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.eye_tracking_eye_tracking_id_seq OWNED BY public.eye_tracking.eye_tracking_id;


--
-- TOC entry 223 (class 1259 OID 16498)
-- Name: handover; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.handover (
    grasped_object character varying(255),
    giver_grasped_object timestamp without time zone,
    receiver_touched_object timestamp without time zone,
    receiver_grasped_object timestamp without time zone,
    trial_id integer NOT NULL,
    giver integer NOT NULL,
    receiver integer,
    handover_id integer NOT NULL,
    giver_released_object timestamp without time zone
);


ALTER TABLE public.handover OWNER TO postgres;

--
-- TOC entry 241 (class 1259 OID 16783)
-- Name: handover_handover_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.handover_handover_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.handover_handover_id_seq OWNER TO postgres;

--
-- TOC entry 5119 (class 0 OID 0)
-- Dependencies: 241
-- Name: handover_handover_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.handover_handover_id_seq OWNED BY public.handover.handover_id;


--
-- TOC entry 220 (class 1259 OID 16463)
-- Name: participant; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participant (
    gender character varying(255),
    age integer,
    participant_id integer NOT NULL,
    handedness character varying(20)
);


ALTER TABLE public.participant OWNER TO postgres;

--
-- TOC entry 240 (class 1259 OID 16750)
-- Name: participant_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.participant_participant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.participant_participant_id_seq OWNER TO postgres;

--
-- TOC entry 5120 (class 0 OID 0)
-- Dependencies: 240
-- Name: participant_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.participant_participant_id_seq OWNED BY public.participant.participant_id;


--
-- TOC entry 227 (class 1259 OID 16593)
-- Name: questionnaire_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questionnaire_item (
    item_name character varying,
    questionnaire_item_id integer NOT NULL,
    questionnaire_id integer NOT NULL,
    item_label character varying(255),
    item_description text,
    min_label character varying(100),
    max_label character varying(100),
    order_index integer DEFAULT 0
);


ALTER TABLE public.questionnaire_item OWNER TO postgres;

--
-- TOC entry 244 (class 1259 OID 16817)
-- Name: questionaire_item_questionnaire_item_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questionaire_item_questionnaire_item_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questionaire_item_questionnaire_item_id_seq OWNER TO postgres;

--
-- TOC entry 5121 (class 0 OID 0)
-- Dependencies: 244
-- Name: questionaire_item_questionnaire_item_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questionaire_item_questionnaire_item_id_seq OWNED BY public.questionnaire_item.questionnaire_item_id;


--
-- TOC entry 226 (class 1259 OID 16588)
-- Name: questionnaire; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questionnaire (
    name character varying NOT NULL,
    questionnaire_id integer NOT NULL,
    scale_type character varying(20) DEFAULT 'slider',
    scale_min double precision DEFAULT 0,
    scale_max double precision DEFAULT 100
);


ALTER TABLE public.questionnaire OWNER TO postgres;

--
-- TOC entry 243 (class 1259 OID 16809)
-- Name: questionaire_questionnaire_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questionaire_questionnaire_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questionaire_questionnaire_id_seq OWNER TO postgres;

--
-- TOC entry 5122 (class 0 OID 0)
-- Dependencies: 243
-- Name: questionaire_questionnaire_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questionaire_questionnaire_id_seq OWNED BY public.questionnaire.questionnaire_id;


--
-- TOC entry 225 (class 1259 OID 16573)
-- Name: questionnaire_response; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questionnaire_response (
    trial_id integer NOT NULL,
    participant_id integer NOT NULL,
    questionnaire_response_id integer NOT NULL,
    questionnaire_item_id integer NOT NULL,
    response_value double precision NOT NULL
);


ALTER TABLE public.questionnaire_response OWNER TO postgres;

--
-- TOC entry 245 (class 1259 OID 16831)
-- Name: questionare_response_qestionnaire_response_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questionare_response_qestionnaire_response_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questionare_response_qestionnaire_response_id_seq OWNER TO postgres;

--
-- TOC entry 5123 (class 0 OID 0)
-- Dependencies: 245
-- Name: questionare_response_qestionnaire_response_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questionare_response_qestionnaire_response_id_seq OWNED BY public.questionnaire_response.questionnaire_response_id;


--
-- TOC entry 218 (class 1259 OID 16440)
-- Name: stimuli_combination; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimuli_combination (
    combination text NOT NULL,
    stimulus_combination_id integer NOT NULL
);


ALTER TABLE public.stimuli_combination OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16732)
-- Name: simuli_combination_stimulu_combination_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.simuli_combination_stimulu_combination_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.simuli_combination_stimulu_combination_id_seq OWNER TO postgres;

--
-- TOC entry 5124 (class 0 OID 0)
-- Dependencies: 239
-- Name: simuli_combination_stimulu_combination_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.simuli_combination_stimulu_combination_id_seq OWNED BY public.stimuli_combination.stimulus_combination_id;


--
-- TOC entry 230 (class 1259 OID 16632)
-- Name: stimuli; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimuli (
    stimulus_id integer NOT NULL,
    stimulus_type_id integer NOT NULL,
    name character varying(255),
    description text
);


ALTER TABLE public.stimuli OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16631)
-- Name: stimuli_stimulus_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stimuli_stimulus_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stimuli_stimulus_id_seq OWNER TO postgres;

--
-- TOC entry 5125 (class 0 OID 0)
-- Dependencies: 229
-- Name: stimuli_stimulus_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stimuli_stimulus_id_seq OWNED BY public.stimuli.stimulus_id;


--
-- TOC entry 234 (class 1259 OID 16664)
-- Name: stimulus_auditiv; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimulus_auditiv (
    stimulus_id integer NOT NULL,
    frequency integer NOT NULL,
    volume integer NOT NULL
);


ALTER TABLE public.stimulus_auditiv OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16445)
-- Name: stimulus_combination_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimulus_combination_item (
    stimulus_id integer NOT NULL,
    stimulus_combination_id integer NOT NULL
);


ALTER TABLE public.stimulus_combination_item OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16674)
-- Name: stimulus_tactile; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimulus_tactile (
    stimulus_id integer NOT NULL,
    pattern character varying(255) NOT NULL,
    intensity integer NOT NULL
);


ALTER TABLE public.stimulus_tactile OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16643)
-- Name: stimulus_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimulus_type (
    stimulus_type_id integer NOT NULL,
    type_name character varying(255)
);


ALTER TABLE public.stimulus_type OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16642)
-- Name: stimulus_type_stimulus_type_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.stimulus_type_stimulus_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.stimulus_type_stimulus_type_id_seq OWNER TO postgres;

--
-- TOC entry 5126 (class 0 OID 0)
-- Dependencies: 231
-- Name: stimulus_type_stimulus_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.stimulus_type_stimulus_type_id_seq OWNED BY public.stimulus_type.stimulus_type_id;


--
-- TOC entry 233 (class 1259 OID 16654)
-- Name: stimulus_visual; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.stimulus_visual (
    stimulus_id integer NOT NULL,
    stimulus_name character varying(255) NOT NULL
);


ALTER TABLE public.stimulus_visual OWNER TO postgres;

--
-- TOC entry 248 (class 1259 OID 17248)
-- Name: study; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study (
    study_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    started_at date,
    ended_at date,
    status character varying(255)
);


ALTER TABLE public.study OWNER TO postgres;

--
-- TOC entry 251 (class 1259 OID 17458)
-- Name: study_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_config (
    study_config_id integer NOT NULL,
    name character varying(255),
    description text,
    principal_investigator character varying(255),
    study_id integer,
    trial_number integer,
    trials_permuted boolean
);


ALTER TABLE public.study_config OWNER TO postgres;

--
-- TOC entry 250 (class 1259 OID 17457)
-- Name: study_config_study_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.study_config_study_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.study_config_study_config_id_seq OWNER TO postgres;

--
-- TOC entry 5127 (class 0 OID 0)
-- Dependencies: 250
-- Name: study_config_study_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.study_config_study_config_id_seq OWNED BY public.study_config.study_config_id;


--
-- TOC entry 249 (class 1259 OID 17440)
-- Name: study_questionnaire; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_questionnaire (
    study_id integer NOT NULL,
    questionnaire_id integer NOT NULL,
    order_index integer,
    trigger_timing character varying(50)
);


ALTER TABLE public.study_questionnaire OWNER TO postgres;

--
-- TOC entry 252 (class 1259 OID 17472)
-- Name: study_stimuli; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.study_stimuli (
    study_id integer NOT NULL,
    stimuli_type_id integer NOT NULL
);


ALTER TABLE public.study_stimuli OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 17247)
-- Name: sudy_study_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sudy_study_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sudy_study_id_seq OWNER TO postgres;

--
-- TOC entry 5128 (class 0 OID 0)
-- Dependencies: 247
-- Name: sudy_study_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sudy_study_id_seq OWNED BY public.study.study_id;


--
-- TOC entry 224 (class 1259 OID 16553)
-- Name: trial; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trial (
    experiment_id integer,
    trial_number integer,
    trial_id integer NOT NULL,
    is_finished boolean DEFAULT false
);


ALTER TABLE public.trial OWNER TO postgres;

--
-- TOC entry 256 (class 1259 OID 17602)
-- Name: trial_participant_slot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trial_participant_slot (
    trial_slot_id integer NOT NULL,
    participant_id integer NOT NULL
);


ALTER TABLE public.trial_participant_slot OWNER TO postgres;

--
-- TOC entry 254 (class 1259 OID 17569)
-- Name: trial_slot; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trial_slot (
    trial_slot_id integer NOT NULL,
    trial_id integer NOT NULL,
    slot integer NOT NULL,
    avatar_visibility_id integer
);


ALTER TABLE public.trial_slot OWNER TO postgres;

--
-- TOC entry 255 (class 1259 OID 17587)
-- Name: trial_slot_stimulus; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trial_slot_stimulus (
    trial_slot_id integer NOT NULL,
    stimulus_id integer NOT NULL
);


ALTER TABLE public.trial_slot_stimulus OWNER TO postgres;

--
-- TOC entry 253 (class 1259 OID 17568)
-- Name: trial_slot_trial_slot_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trial_slot_trial_slot_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trial_slot_trial_slot_id_seq OWNER TO postgres;

--
-- TOC entry 5129 (class 0 OID 0)
-- Dependencies: 253
-- Name: trial_slot_trial_slot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trial_slot_trial_slot_id_seq OWNED BY public.trial_slot.trial_slot_id;


--
-- TOC entry 238 (class 1259 OID 16709)
-- Name: trial_trial_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trial_trial_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trial_trial_id_seq OWNER TO postgres;

--
-- TOC entry 5130 (class 0 OID 0)
-- Dependencies: 238
-- Name: trial_trial_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trial_trial_id_seq OWNED BY public.trial.trial_id;


--
-- TOC entry 4857 (class 2604 OID 16797)
-- Name: area_of_interest aoi_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.area_of_interest ALTER COLUMN aoi_id SET DEFAULT nextval('public.area_of_interest_aoi_id_seq'::regclass);


--
-- TOC entry 4867 (class 2604 OID 16699)
-- Name: avatar_visibility avatar_visibility_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avatar_visibility ALTER COLUMN avatar_visibility_id SET DEFAULT nextval('public.avatar_visibility_avatar_visibility_id_seq'::regclass);


--
-- TOC entry 4854 (class 2604 OID 16618)
-- Name: experiment experiment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment ALTER COLUMN experiment_id SET DEFAULT nextval('public.experiment_experiment_id_seq'::regclass);


--
-- TOC entry 4858 (class 2604 OID 16845)
-- Name: eye_tracking eye_tracking_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eye_tracking ALTER COLUMN eye_tracking_id SET DEFAULT nextval('public.eye_tracking_eye_tracking_id_seq'::regclass);


--
-- TOC entry 4859 (class 2604 OID 16784)
-- Name: handover handover_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handover ALTER COLUMN handover_id SET DEFAULT nextval('public.handover_handover_id_seq'::regclass);


--
-- TOC entry 4856 (class 2604 OID 16751)
-- Name: participant participant_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participant ALTER COLUMN participant_id SET DEFAULT nextval('public.participant_participant_id_seq'::regclass);


--
-- TOC entry 4863 (class 2604 OID 16810)
-- Name: questionnaire questionnaire_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire ALTER COLUMN questionnaire_id SET DEFAULT nextval('public.questionaire_questionnaire_id_seq'::regclass);


--
-- TOC entry 4864 (class 2604 OID 16818)
-- Name: questionnaire_item questionnaire_item_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_item ALTER COLUMN questionnaire_item_id SET DEFAULT nextval('public.questionaire_item_questionnaire_item_id_seq'::regclass);


--
-- TOC entry 4862 (class 2604 OID 16832)
-- Name: questionnaire_response questionnaire_response_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_response ALTER COLUMN questionnaire_response_id SET DEFAULT nextval('public.questionare_response_qestionnaire_response_id_seq'::regclass);


--
-- TOC entry 4865 (class 2604 OID 16635)
-- Name: stimuli stimulus_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli ALTER COLUMN stimulus_id SET DEFAULT nextval('public.stimuli_stimulus_id_seq'::regclass);


--
-- TOC entry 4855 (class 2604 OID 16733)
-- Name: stimuli_combination stimulus_combination_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli_combination ALTER COLUMN stimulus_combination_id SET DEFAULT nextval('public.simuli_combination_stimulu_combination_id_seq'::regclass);


--
-- TOC entry 4866 (class 2604 OID 16646)
-- Name: stimulus_type stimulus_type_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_type ALTER COLUMN stimulus_type_id SET DEFAULT nextval('public.stimulus_type_stimulus_type_id_seq'::regclass);


--
-- TOC entry 4868 (class 2604 OID 17251)
-- Name: study study_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study ALTER COLUMN study_id SET DEFAULT nextval('public.sudy_study_id_seq'::regclass);


--
-- TOC entry 4870 (class 2604 OID 17461)
-- Name: study_config study_config_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_config ALTER COLUMN study_config_id SET DEFAULT nextval('public.study_config_study_config_id_seq'::regclass);


--
-- TOC entry 4860 (class 2604 OID 16710)
-- Name: trial trial_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial ALTER COLUMN trial_id SET DEFAULT nextval('public.trial_trial_id_seq'::regclass);


--
-- TOC entry 4871 (class 2604 OID 17572)
-- Name: trial_slot trial_slot_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot ALTER COLUMN trial_slot_id SET DEFAULT nextval('public.trial_slot_trial_slot_id_seq'::regclass);


--
-- TOC entry 4883 (class 2606 OID 16799)
-- Name: area_of_interest area_of_interest_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.area_of_interest
    ADD CONSTRAINT area_of_interest_pk PRIMARY KEY (aoi_id);


--
-- TOC entry 4913 (class 2606 OID 16701)
-- Name: avatar_visibility avatar_visibility_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avatar_visibility
    ADD CONSTRAINT avatar_visibility_pk PRIMARY KEY (avatar_visibility_id);


--
-- TOC entry 4915 (class 2606 OID 16703)
-- Name: avatar_visibility avatar_visibility_pk_2; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.avatar_visibility
    ADD CONSTRAINT avatar_visibility_pk_2 UNIQUE (avatar_visibility_name);


--
-- TOC entry 4873 (class 2606 OID 16625)
-- Name: experiment experiment_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment
    ADD CONSTRAINT experiment_pk PRIMARY KEY (experiment_id);


--
-- TOC entry 4933 (class 2606 OID 17739)
-- Name: experiment_questionnaire experiment_questionnaire_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_questionnaire
    ADD CONSTRAINT experiment_questionnaire_pkey PRIMARY KEY (experiment_id, questionnaire_id);


--
-- TOC entry 4885 (class 2606 OID 16847)
-- Name: eye_tracking eye_tracking_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eye_tracking
    ADD CONSTRAINT eye_tracking_pk PRIMARY KEY (eye_tracking_id);


--
-- TOC entry 4887 (class 2606 OID 16786)
-- Name: handover handover_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT handover_pk PRIMARY KEY (handover_id);


--
-- TOC entry 4881 (class 2606 OID 16753)
-- Name: participant participant_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participant
    ADD CONSTRAINT participant_pk PRIMARY KEY (participant_id);


--
-- TOC entry 4897 (class 2606 OID 16820)
-- Name: questionnaire_item questionnaire_item_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_item
    ADD CONSTRAINT questionnaire_item_pk PRIMARY KEY (questionnaire_item_id);


--
-- TOC entry 4893 (class 2606 OID 16812)
-- Name: questionnaire questionnaire_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_pk PRIMARY KEY (questionnaire_id);


--
-- TOC entry 4895 (class 2606 OID 16955)
-- Name: questionnaire questionnaire_pk_2; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire
    ADD CONSTRAINT questionnaire_pk_2 UNIQUE (name);


--
-- TOC entry 4891 (class 2606 OID 16834)
-- Name: questionnaire_response questionnaire_response_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_response
    ADD CONSTRAINT questionnaire_response_pk PRIMARY KEY (questionnaire_response_id);


--
-- TOC entry 4875 (class 2606 OID 16735)
-- Name: stimuli_combination stimuli_combination_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli_combination
    ADD CONSTRAINT stimuli_combination_pk PRIMARY KEY (stimulus_combination_id);


--
-- TOC entry 4877 (class 2606 OID 16857)
-- Name: stimuli_combination stimuli_combination_pk_2; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli_combination
    ADD CONSTRAINT stimuli_combination_pk_2 UNIQUE (combination);


--
-- TOC entry 4899 (class 2606 OID 16641)
-- Name: stimuli stimuli_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli
    ADD CONSTRAINT stimuli_pk PRIMARY KEY (stimulus_id);


--
-- TOC entry 4901 (class 2606 OID 16694)
-- Name: stimuli stimuli_pk_2; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli
    ADD CONSTRAINT stimuli_pk_2 UNIQUE (name, stimulus_type_id);


--
-- TOC entry 4909 (class 2606 OID 16668)
-- Name: stimulus_auditiv stimulus_auditiv_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_auditiv
    ADD CONSTRAINT stimulus_auditiv_pk PRIMARY KEY (stimulus_id);


--
-- TOC entry 4879 (class 2606 OID 16861)
-- Name: stimulus_combination_item stimulus_combination_item_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_combination_item
    ADD CONSTRAINT stimulus_combination_item_pk UNIQUE (stimulus_id, stimulus_combination_id);


--
-- TOC entry 4911 (class 2606 OID 16678)
-- Name: stimulus_tactile stimulus_tactile_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_tactile
    ADD CONSTRAINT stimulus_tactile_pk PRIMARY KEY (stimulus_id);


--
-- TOC entry 4903 (class 2606 OID 16648)
-- Name: stimulus_type stimulus_type_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_type
    ADD CONSTRAINT stimulus_type_pk PRIMARY KEY (stimulus_type_id);


--
-- TOC entry 4905 (class 2606 OID 16690)
-- Name: stimulus_type stimulus_type_pk_2; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_type
    ADD CONSTRAINT stimulus_type_pk_2 UNIQUE (type_name);


--
-- TOC entry 4907 (class 2606 OID 16658)
-- Name: stimulus_visual stimulus_visual_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_visual
    ADD CONSTRAINT stimulus_visual_pk PRIMARY KEY (stimulus_id);


--
-- TOC entry 4921 (class 2606 OID 17465)
-- Name: study_config study_config_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_config
    ADD CONSTRAINT study_config_pk PRIMARY KEY (study_config_id);


--
-- TOC entry 4917 (class 2606 OID 17256)
-- Name: study study_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study
    ADD CONSTRAINT study_pk PRIMARY KEY (study_id);


--
-- TOC entry 4919 (class 2606 OID 17444)
-- Name: study_questionnaire study_questionnaire_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_questionnaire
    ADD CONSTRAINT study_questionnaire_pkey PRIMARY KEY (study_id, questionnaire_id);


--
-- TOC entry 4923 (class 2606 OID 17476)
-- Name: study_stimuli study_stimuli_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_stimuli
    ADD CONSTRAINT study_stimuli_pk PRIMARY KEY (study_id, stimuli_type_id);


--
-- TOC entry 4931 (class 2606 OID 17606)
-- Name: trial_participant_slot trial_participant_slot_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_participant_slot
    ADD CONSTRAINT trial_participant_slot_pk PRIMARY KEY (trial_slot_id, participant_id);


--
-- TOC entry 4889 (class 2606 OID 16712)
-- Name: trial trial_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial
    ADD CONSTRAINT trial_pk PRIMARY KEY (trial_id);


--
-- TOC entry 4925 (class 2606 OID 17574)
-- Name: trial_slot trial_slot_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot
    ADD CONSTRAINT trial_slot_pk PRIMARY KEY (trial_slot_id);


--
-- TOC entry 4929 (class 2606 OID 17591)
-- Name: trial_slot_stimulus trial_slot_stimulus_pk; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot_stimulus
    ADD CONSTRAINT trial_slot_stimulus_pk PRIMARY KEY (trial_slot_id, stimulus_id);


--
-- TOC entry 4927 (class 2606 OID 17576)
-- Name: trial_slot trial_slot_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot
    ADD CONSTRAINT trial_slot_unique UNIQUE (trial_id, slot);


--
-- TOC entry 4957 (class 2606 OID 17582)
-- Name: trial_slot avatar_visibility_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot
    ADD CONSTRAINT avatar_visibility_id_fk FOREIGN KEY (avatar_visibility_id) REFERENCES public.avatar_visibility(avatar_visibility_id);


--
-- TOC entry 4963 (class 2606 OID 17740)
-- Name: experiment_questionnaire experiment_questionnaire_experiment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_questionnaire
    ADD CONSTRAINT experiment_questionnaire_experiment_id_fkey FOREIGN KEY (experiment_id) REFERENCES public.experiment(experiment_id);


--
-- TOC entry 4964 (class 2606 OID 17745)
-- Name: experiment_questionnaire experiment_questionnaire_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment_questionnaire
    ADD CONSTRAINT experiment_questionnaire_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(questionnaire_id);


--
-- TOC entry 4937 (class 2606 OID 16804)
-- Name: eye_tracking eye_tracking_area_of_interest_aoi_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eye_tracking
    ADD CONSTRAINT eye_tracking_area_of_interest_aoi_id_fk FOREIGN KEY (aoi_id) REFERENCES public.area_of_interest(aoi_id);


--
-- TOC entry 4938 (class 2606 OID 16758)
-- Name: eye_tracking eye_tracking_participant_participant_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eye_tracking
    ADD CONSTRAINT eye_tracking_participant_participant_id_fk FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id);


--
-- TOC entry 4940 (class 2606 OID 16763)
-- Name: handover giver_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT giver_id_fk FOREIGN KEY (giver) REFERENCES public.participant(participant_id);


--
-- TOC entry 4939 (class 2606 OID 16791)
-- Name: eye_tracking handover_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.eye_tracking
    ADD CONSTRAINT handover_id_fk FOREIGN KEY (handover_id) REFERENCES public.handover(handover_id);


--
-- TOC entry 4944 (class 2606 OID 16773)
-- Name: questionnaire_response participant_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_response
    ADD CONSTRAINT participant_id_fk FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id);


--
-- TOC entry 4961 (class 2606 OID 17612)
-- Name: trial_participant_slot participant_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_participant_slot
    ADD CONSTRAINT participant_id_fk FOREIGN KEY (participant_id) REFERENCES public.participant(participant_id);


--
-- TOC entry 4947 (class 2606 OID 16825)
-- Name: questionnaire_item questionaire_item_questionaire_questionnaire_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_item
    ADD CONSTRAINT questionaire_item_questionaire_questionnaire_id_fk FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(questionnaire_id);


--
-- TOC entry 4945 (class 2606 OID 16839)
-- Name: questionnaire_response questionnaire_item_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_response
    ADD CONSTRAINT questionnaire_item_id_fk FOREIGN KEY (questionnaire_item_id) REFERENCES public.questionnaire_item(questionnaire_item_id);


--
-- TOC entry 4941 (class 2606 OID 16768)
-- Name: handover reciever_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT reciever_id_fk FOREIGN KEY (receiver) REFERENCES public.participant(participant_id);


--
-- TOC entry 4935 (class 2606 OID 16740)
-- Name: stimulus_combination_item stimulu_combination_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_combination_item
    ADD CONSTRAINT stimulu_combination_id_fk FOREIGN KEY (stimulus_combination_id) REFERENCES public.stimuli_combination(stimulus_combination_id);


--
-- TOC entry 4949 (class 2606 OID 16659)
-- Name: stimulus_visual stimulus_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_visual
    ADD CONSTRAINT stimulus_id_fk FOREIGN KEY (stimulus_id) REFERENCES public.stimuli(stimulus_id);


--
-- TOC entry 4950 (class 2606 OID 16669)
-- Name: stimulus_auditiv stimulus_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_auditiv
    ADD CONSTRAINT stimulus_id_fk FOREIGN KEY (stimulus_id) REFERENCES public.stimuli(stimulus_id);


--
-- TOC entry 4936 (class 2606 OID 16684)
-- Name: stimulus_combination_item stimulus_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_combination_item
    ADD CONSTRAINT stimulus_id_fk FOREIGN KEY (stimulus_id) REFERENCES public.stimuli(stimulus_id);


--
-- TOC entry 4959 (class 2606 OID 17597)
-- Name: trial_slot_stimulus stimulus_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot_stimulus
    ADD CONSTRAINT stimulus_id_fk FOREIGN KEY (stimulus_id) REFERENCES public.stimuli(stimulus_id);


--
-- TOC entry 4951 (class 2606 OID 16679)
-- Name: stimulus_tactile stimulus_tactile_stimuli_stimulus_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimulus_tactile
    ADD CONSTRAINT stimulus_tactile_stimuli_stimulus_id_fk FOREIGN KEY (stimulus_id) REFERENCES public.stimuli(stimulus_id);


--
-- TOC entry 4948 (class 2606 OID 16649)
-- Name: stimuli stimulus_type_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.stimuli
    ADD CONSTRAINT stimulus_type_id_fk FOREIGN KEY (stimulus_type_id) REFERENCES public.stimulus_type(stimulus_type_id);


--
-- TOC entry 4955 (class 2606 OID 17482)
-- Name: study_stimuli stimulus_type_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_stimuli
    ADD CONSTRAINT stimulus_type_id_fk FOREIGN KEY (stimuli_type_id) REFERENCES public.stimulus_type(stimulus_type_id);


--
-- TOC entry 4954 (class 2606 OID 17466)
-- Name: study_config study_config_study_study_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_config
    ADD CONSTRAINT study_config_study_study_id_fk FOREIGN KEY (study_id) REFERENCES public.study(study_id);


--
-- TOC entry 4934 (class 2606 OID 17303)
-- Name: experiment study_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.experiment
    ADD CONSTRAINT study_id_fk FOREIGN KEY (study_id) REFERENCES public.study(study_id);


--
-- TOC entry 4956 (class 2606 OID 17477)
-- Name: study_stimuli study_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_stimuli
    ADD CONSTRAINT study_id_fk FOREIGN KEY (study_id) REFERENCES public.study(study_id);


--
-- TOC entry 4952 (class 2606 OID 17450)
-- Name: study_questionnaire study_questionnaire_questionnaire_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_questionnaire
    ADD CONSTRAINT study_questionnaire_questionnaire_id_fkey FOREIGN KEY (questionnaire_id) REFERENCES public.questionnaire(questionnaire_id) ON DELETE CASCADE;


--
-- TOC entry 4953 (class 2606 OID 17445)
-- Name: study_questionnaire study_questionnaire_study_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.study_questionnaire
    ADD CONSTRAINT study_questionnaire_study_id_fkey FOREIGN KEY (study_id) REFERENCES public.study(study_id) ON DELETE CASCADE;


--
-- TOC entry 4943 (class 2606 OID 16626)
-- Name: trial trial_experiment_experiment_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial
    ADD CONSTRAINT trial_experiment_experiment_id_fk FOREIGN KEY (experiment_id) REFERENCES public.experiment(experiment_id);


--
-- TOC entry 4942 (class 2606 OID 16717)
-- Name: handover trial_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handover
    ADD CONSTRAINT trial_id_fk FOREIGN KEY (trial_id) REFERENCES public.trial(trial_id);


--
-- TOC entry 4946 (class 2606 OID 16722)
-- Name: questionnaire_response trial_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questionnaire_response
    ADD CONSTRAINT trial_id_fk FOREIGN KEY (trial_id) REFERENCES public.trial(trial_id);


--
-- TOC entry 4958 (class 2606 OID 17577)
-- Name: trial_slot trial_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot
    ADD CONSTRAINT trial_id_fk FOREIGN KEY (trial_id) REFERENCES public.trial(trial_id) ON DELETE CASCADE;


--
-- TOC entry 4960 (class 2606 OID 17592)
-- Name: trial_slot_stimulus trial_slot_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_slot_stimulus
    ADD CONSTRAINT trial_slot_id_fk FOREIGN KEY (trial_slot_id) REFERENCES public.trial_slot(trial_slot_id) ON DELETE CASCADE;


--
-- TOC entry 4962 (class 2606 OID 17607)
-- Name: trial_participant_slot trial_slot_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trial_participant_slot
    ADD CONSTRAINT trial_slot_id_fk FOREIGN KEY (trial_slot_id) REFERENCES public.trial_slot(trial_slot_id) ON DELETE CASCADE;


-- Completed on 2025-11-09 22:38:29

--
-- PostgreSQL database dump complete
--

-- Schema extensions added post-dump

ALTER TABLE public.handover
  ADD COLUMN IF NOT EXISTS is_error BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS error_type VARCHAR(100);

ALTER TABLE public.study_config
  ADD COLUMN IF NOT EXISTS study_type VARCHAR(50) DEFAULT 'stimulus_comparison';

