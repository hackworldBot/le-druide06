--
-- PostgreSQL database dump
--

\restrict zZ3Kl6tUinDLouaoIDzRJFh4Quopop6zObgYt9xg4uAM9PBswM9xyQKt8ZxJQWg

-- Dumped from database version 15.19 (Debian 15.19-0+deb12u1)
-- Dumped by pg_dump version 15.19 (Debian 15.19-0+deb12u1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: information; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.information (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    is_active boolean NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.information OWNER TO telegram_shop;

--
-- Name: information_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.information_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.information_id_seq OWNER TO telegram_shop;

--
-- Name: information_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.information_id_seq OWNED BY public.information.id;


--
-- Name: information id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.information ALTER COLUMN id SET DEFAULT nextval('public.information_id_seq'::regclass);


--
-- Data for Name: information; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.information (id, title, content, is_active, updated_at) FROM stdin;
1	test	🛍️ Boutique\n💵 Paiement en liquide sur place\n📦 Retrait directement en boutique\n\nMerci de votre confiance !	f	2026-08-26 21:50:26.080628
2	INFORMATIONS	🛍️ Boutique\n💵 Paiement en liquide sur place\n📦 Retrait directement en boutique\n\nMerci de votre confiance !	t	2026-08-26 21:50:30.839894
\.


--
-- Name: information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.information_id_seq', 2, true);


--
-- Name: information information_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.information
    ADD CONSTRAINT information_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

\unrestrict zZ3Kl6tUinDLouaoIDzRJFh4Quopop6zObgYt9xg4uAM9PBswM9xyQKt8ZxJQWg

