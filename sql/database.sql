create sequence simuli_combination_stimulu_combination_id_seq
    as integer;

alter sequence simuli_combination_stimulu_combination_id_seq owner to postgres;

create sequence questionaire_questionnaire_id_seq
    as integer;

alter sequence questionaire_questionnaire_id_seq owner to postgres;

create sequence questionaire_item_questionnaire_item_id_seq
    as integer;

alter sequence questionaire_item_questionnaire_item_id_seq owner to postgres;

create sequence questionare_response_qestionnaire_response_id_seq
    as integer;

alter sequence questionare_response_qestionnaire_response_id_seq owner to postgres;

create sequence sudy_study_id_seq
    as integer;

alter sequence sudy_study_id_seq owner to postgres;

create table if not exists stimuli_combination
(
    combination             text                                                                               not null
        constraint stimuli_combination_pk_2
            unique,
    stimulus_combination_id integer default nextval('simuli_combination_stimulu_combination_id_seq'::regclass) not null
        constraint stimuli_combination_pk
            primary key
);

alter table stimuli_combination
    owner to postgres;

alter sequence simuli_combination_stimulu_combination_id_seq owned by stimuli_combination.stimulus_combination_id;

create table if not exists participant
(
    gender         varchar(255),
    age            integer,
    participant_id serial
        constraint participant_pk
            primary key,
    handedness     varchar(20)
);

alter table participant
    owner to postgres;

create table if not exists area_of_interest
(
    aoi    varchar(255) not null,
    aoi_id serial
        constraint area_of_interest_pk
            primary key,
    label  varchar(255) not null
);

alter table area_of_interest
    owner to postgres;

create table if not exists questionnaire
(
    name             varchar                                                                not null
        constraint questionnaire_pk_2
            unique,
    questionnaire_id integer default nextval('questionaire_questionnaire_id_seq'::regclass) not null
        constraint questionnaire_pk
            primary key
);

alter table questionnaire
    owner to postgres;

alter sequence questionaire_questionnaire_id_seq owned by questionnaire.questionnaire_id;

create table if not exists questionnaire_item
(
    item_name             varchar,
    questionnaire_item_id integer default nextval('questionaire_item_questionnaire_item_id_seq'::regclass) not null
        constraint questionnaire_item_pk
            primary key,
    questionnaire_id      integer                                                                          not null
        constraint questionaire_item_questionaire_questionnaire_id_fk
            references questionnaire
);

alter table questionnaire_item
    owner to postgres;

alter sequence questionaire_item_questionnaire_item_id_seq owned by questionnaire_item.questionnaire_item_id;

create table if not exists stimulus_type
(
    stimulus_type_id serial
        constraint stimulus_type_pk
            primary key,
    type_name        varchar(255)
        constraint stimulus_type_pk_2
            unique
);

alter table stimulus_type
    owner to postgres;

create table if not exists stimuli
(
    stimulus_id      serial
        constraint stimuli_pk
            primary key,
    stimulus_type_id integer not null
        constraint stimulus_type_id_fk
            references stimulus_type,
    name             varchar(255),
    description      text,
    constraint stimuli_pk_2
        unique (name, stimulus_type_id)
);

alter table stimuli
    owner to postgres;

create table if not exists stimulus_combination_item
(
    stimulus_id             integer not null
        constraint stimulus_id_fk
            references stimuli,
    stimulus_combination_id integer not null
        constraint stimulu_combination_id_fk
            references stimuli_combination,
    constraint stimulus_combination_item_pk
        unique (stimulus_id, stimulus_combination_id)
);

alter table stimulus_combination_item
    owner to postgres;

create table if not exists stimulus_visual
(
    stimulus_id   integer      not null
        constraint stimulus_visual_pk
            primary key
        constraint stimulus_id_fk
            references stimuli,
    stimulus_name varchar(255) not null
);

alter table stimulus_visual
    owner to postgres;

create table if not exists stimulus_auditiv
(
    stimulus_id integer not null
        constraint stimulus_auditiv_pk
            primary key
        constraint stimulus_id_fk
            references stimuli,
    frequency   integer not null,
    volume      integer not null
);

alter table stimulus_auditiv
    owner to postgres;

create table if not exists stimulus_tactile
(
    stimulus_id integer      not null
        constraint stimulus_tactile_pk
            primary key
        constraint stimulus_tactile_stimuli_stimulus_id_fk
            references stimuli,
    pattern     varchar(255) not null,
    intensity   integer      not null
);

alter table stimulus_tactile
    owner to postgres;

create table if not exists avatar_visibility
(
    avatar_visibility_id   serial
        constraint avatar_visibility_pk
            primary key,
    avatar_visibility_name varchar(100) not null
        constraint avatar_visibility_pk_2
            unique,
    label                  varchar(255) not null
);

alter table avatar_visibility
    owner to postgres;

create table if not exists study
(
    study_id   integer   default nextval('sudy_study_id_seq'::regclass) not null
        constraint study_pk
            primary key,
    created_at timestamp default now(),
    started_at date,
    ended_at   date,
    status     varchar(255)
);

alter table study
    owner to postgres;

alter sequence sudy_study_id_seq owned by study.study_id;

create table if not exists experiment
(
    description   text,
    created_at    timestamp default now(),
    started_at    timestamp,
    completed_at  timestamp,
    researcher    varchar(255),
    experiment_id serial
        constraint experiment_pk
            primary key,
    study_id      integer not null
        constraint study_id_fk
            references study
);

alter table experiment
    owner to postgres;

create table if not exists trial
(
    experiment_id integer
        constraint trial_experiment_experiment_id_fk
            references experiment,
    trial_number  integer,
    trial_id      serial
        constraint trial_pk
            primary key,
    is_finished   boolean default false
);

alter table trial
    owner to postgres;

create table if not exists handover
(
    grasped_object          varchar(255),
    giver_grasped_object    timestamp,
    receiver_touched_object timestamp,
    receiver_grasped_object timestamp,
    trial_id                integer not null
        constraint trial_id_fk
            references trial,
    giver                   integer not null
        constraint giver_id_fk
            references participant,
    receiver                integer
        constraint reciever_id_fk
            references participant,
    handover_id             serial
        constraint handover_pk
            primary key,
    giver_released_object   timestamp
);

alter table handover
    owner to postgres;

create table if not exists eye_tracking
(
    starttime       timestamp,
    endtime         timestamp,
    duration        integer,
    participant_id  integer not null
        constraint eye_tracking_participant_participant_id_fk
            references participant,
    hanover_id      integer not null
        constraint handover_id_fk
            references handover,
    aoi_id          integer not null
        constraint eye_tracking_area_of_interest_aoi_id_fk
            references area_of_interest,
    eye_tracking_id serial
        constraint eye_tracking_pk
            primary key
);

alter table eye_tracking
    owner to postgres;

create table if not exists questionnaire_response
(
    trial_id                  integer                                                                                not null
        constraint trial_id_fk
            references trial,
    participant_id            integer                                                                                not null
        constraint participant_id_fk
            references participant,
    questionnaire_response_id integer default nextval('questionare_response_qestionnaire_response_id_seq'::regclass) not null
        constraint questionnaire_response_pk
            primary key,
    questionnaire_item_id     integer                                                                                not null
        constraint questionnaire_item_id_fk
            references questionnaire_item,
    response_value            double precision                                                                       not null
);

alter table questionnaire_response
    owner to postgres;

alter sequence questionare_response_qestionnaire_response_id_seq owned by questionnaire_response.questionnaire_response_id;

create table if not exists study_questionnaire
(
    study_id         integer not null
        references study
            on delete cascade,
    questionnaire_id integer not null
        references questionnaire
            on delete cascade,
    order_index      integer,
    trigger_timing   varchar(50),
    primary key (study_id, questionnaire_id)
);

alter table study_questionnaire
    owner to postgres;

create table if not exists study_config
(
    study_config_id        serial
        constraint study_config_pk
            primary key,
    name                   varchar(255),
    description            text,
    principal_investigator varchar(255),
    study_id               integer
        constraint study_config_study_study_id_fk
            references study,
    trial_number           integer,
    trials_permuted        boolean
);

alter table study_config
    owner to postgres;

create table if not exists study_stimuli
(
    study_id        integer not null
        constraint study_id_fk
            references study,
    stimuli_type_id integer not null
        constraint stimulus_type_id_fk
            references stimulus_type,
    constraint study_stimuli_pk
        primary key (study_id, stimuli_type_id)
);

alter table study_stimuli
    owner to postgres;

create table if not exists trial_slot
(
    trial_slot_id        serial
        constraint trial_slot_pk
            primary key,
    trial_id             integer not null
        constraint trial_id_fk
            references trial
            on delete cascade,
    slot                 integer not null,
    avatar_visibility_id integer
        constraint avatar_visibility_id_fk
            references avatar_visibility,
    constraint trial_slot_unique
        unique (trial_id, slot)
);

alter table trial_slot
    owner to postgres;

create table if not exists trial_slot_stimulus
(
    trial_slot_id integer not null
        constraint trial_slot_id_fk
            references trial_slot
            on delete cascade,
    stimulus_id   integer not null
        constraint stimulus_id_fk
            references stimuli,
    constraint trial_slot_stimulus_pk
        primary key (trial_slot_id, stimulus_id)
);

alter table trial_slot_stimulus
    owner to postgres;

create table if not exists trial_participant_slot
(
    trial_slot_id  integer not null
        constraint trial_slot_id_fk
            references trial_slot
            on delete cascade,
    participant_id integer not null
        constraint participant_id_fk
            references participant,
    constraint trial_participant_slot_pk
        primary key (trial_slot_id, participant_id)
);

alter table trial_participant_slot
    owner to postgres;

create table if not exists experiment_questionnaire
(
    experiment_id    integer not null
        references experiment,
    questionnaire_id integer not null
        references questionnaire,
    primary key (experiment_id, questionnaire_id)
);

alter table experiment_questionnaire
    owner to postgres;


