--
-- PostgreSQL database dump
--

-- Dumped from database version 10.10 (Ubuntu 10.10-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.10 (Ubuntu 10.10-0ubuntu0.18.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: audio_types; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE public.audio_types (
    audio_code character varying(10) NOT NULL
);


ALTER TABLE public.audio_types OWNER TO vagrant;

--
-- Name: audios; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE public.audios (
    audio_id integer NOT NULL,
    name character varying(50) NOT NULL,
    s3_path character varying(300) NOT NULL,
    published boolean NOT NULL,
    audio_code character varying(10) NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.audios OWNER TO vagrant;

--
-- Name: audios_audio_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE public.audios_audio_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audios_audio_id_seq OWNER TO vagrant;

--
-- Name: audios_audio_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE public.audios_audio_id_seq OWNED BY public.audios.audio_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: vagrant
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    uname character varying(30) NOT NULL,
    email character varying(100) NOT NULL
);


ALTER TABLE public.users OWNER TO vagrant;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: vagrant
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_user_id_seq OWNER TO vagrant;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: vagrant
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: audios audio_id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.audios ALTER COLUMN audio_id SET DEFAULT nextval('public.audios_audio_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: audio_types; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY public.audio_types (audio_code) FROM stdin;
pod
ad
edt
\.


--
-- Data for Name: audios; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY public.audios (audio_id, name, s3_path, published, audio_code, user_id) FROM stdin;
88	raw_pod_test1.mp3	https://podcaststudio.s3-us-west-1.amazonaws.com/raw_podcasts/raw_pod_test1.mp3	f	pod	2
89	raw_pod_test2.mp3	https://podcaststudio.s3-us-west-1.amazonaws.com/ads/raw_pod_test2.mp3	f	ad	2
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: vagrant
--

COPY public.users (user_id, uname, email) FROM stdin;
2	caca@hackb.com	caca@hackb.com
3	otrofimo@gmail.com	otrofimo@gmail.com
\.


--
-- Name: audios_audio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('public.audios_audio_id_seq', 89, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: vagrant
--

SELECT pg_catalog.setval('public.users_user_id_seq', 3, true);


--
-- Name: audio_types audio_types_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.audio_types
    ADD CONSTRAINT audio_types_pkey PRIMARY KEY (audio_code);


--
-- Name: audios audios_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.audios
    ADD CONSTRAINT audios_pkey PRIMARY KEY (audio_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_uname_key; Type: CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_uname_key UNIQUE (uname);


--
-- Name: audios audios_audio_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.audios
    ADD CONSTRAINT audios_audio_code_fkey FOREIGN KEY (audio_code) REFERENCES public.audio_types(audio_code);


--
-- Name: audios audios_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: vagrant
--

ALTER TABLE ONLY public.audios
    ADD CONSTRAINT audios_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--

