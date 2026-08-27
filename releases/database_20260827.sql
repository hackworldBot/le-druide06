--
-- PostgreSQL database dump
--

\restrict JpvaHIDNmTNkmunv809ArqbFnmHklh0cNzZu6CtGWD92bnCaQlDwDrWK44HjxW4

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
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO telegram_shop;

--
-- Name: cart_items; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.cart_items (
    id integer NOT NULL,
    cart_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.cart_items OWNER TO telegram_shop;

--
-- Name: cart_items_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.cart_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cart_items_id_seq OWNER TO telegram_shop;

--
-- Name: cart_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.cart_items_id_seq OWNED BY public.cart_items.id;


--
-- Name: carts; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.carts (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.carts OWNER TO telegram_shop;

--
-- Name: carts_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.carts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.carts_id_seq OWNER TO telegram_shop;

--
-- Name: carts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.carts_id_seq OWNED BY public.carts.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(1000),
    image character varying(1000),
    sort_order integer NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.categories OWNER TO telegram_shop;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO telegram_shop;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: information; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.information (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    is_active boolean NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    presentation text DEFAULT ''::text NOT NULL,
    address text DEFAULT ''::text NOT NULL,
    opening_hours text DEFAULT ''::text NOT NULL,
    payment text DEFAULT ''::text NOT NULL,
    pickup text DEFAULT ''::text NOT NULL,
    contact text DEFAULT ''::text NOT NULL,
    additional text DEFAULT ''::text NOT NULL
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
-- Name: order_items; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.order_items (
    id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer,
    product_name character varying(255) NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    quantity integer NOT NULL,
    subtotal numeric(10,2) NOT NULL
);


ALTER TABLE public.order_items OWNER TO telegram_shop;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.order_items_id_seq OWNER TO telegram_shop;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    status character varying(50) NOT NULL,
    total numeric(10,2) NOT NULL,
    payment_method character varying(50) NOT NULL,
    customer_note character varying(1000),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.orders OWNER TO telegram_shop;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO telegram_shop;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.products (
    id integer NOT NULL,
    category_id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    price numeric(10,2) NOT NULL,
    stock integer NOT NULL,
    image character varying(1000),
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sku character varying(100),
    product_type character varying(50) DEFAULT 'physical'::character varying NOT NULL,
    sold_count integer DEFAULT 0 NOT NULL,
    download_link text,
    created_by bigint,
    updated_by bigint
);


ALTER TABLE public.products OWNER TO telegram_shop;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.products_id_seq OWNER TO telegram_shop;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: promotions; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.promotions (
    id integer NOT NULL,
    title character varying(255) DEFAULT 'PROMOTIONS'::character varying NOT NULL,
    content text DEFAULT ''::text NOT NULL,
    is_active boolean DEFAULT false NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.promotions OWNER TO telegram_shop;

--
-- Name: promotions_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.promotions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.promotions_id_seq OWNER TO telegram_shop;

--
-- Name: promotions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.promotions_id_seq OWNED BY public.promotions.id;


--
-- Name: support_messages; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.support_messages (
    id integer NOT NULL,
    ticket_id integer NOT NULL,
    sender_type character varying(20) NOT NULL,
    sender_telegram_id bigint NOT NULL,
    message text NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.support_messages OWNER TO telegram_shop;

--
-- Name: support_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.support_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_messages_id_seq OWNER TO telegram_shop;

--
-- Name: support_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.support_messages_id_seq OWNED BY public.support_messages.id;


--
-- Name: support_tickets; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.support_tickets (
    id integer NOT NULL,
    user_id integer NOT NULL,
    topic character varying(255) NOT NULL,
    status character varying(50) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.support_tickets OWNER TO telegram_shop;

--
-- Name: support_tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.support_tickets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.support_tickets_id_seq OWNER TO telegram_shop;

--
-- Name: support_tickets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.support_tickets_id_seq OWNED BY public.support_tickets.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: telegram_shop
--

CREATE TABLE public.users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    username character varying(255),
    first_name character varying(255),
    last_name character varying(255),
    accepted boolean NOT NULL,
    is_blocked boolean NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.users OWNER TO telegram_shop;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: telegram_shop
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO telegram_shop;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: telegram_shop
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: cart_items id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.cart_items ALTER COLUMN id SET DEFAULT nextval('public.cart_items_id_seq'::regclass);


--
-- Name: carts id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.carts ALTER COLUMN id SET DEFAULT nextval('public.carts_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: information id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.information ALTER COLUMN id SET DEFAULT nextval('public.information_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: promotions id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.promotions ALTER COLUMN id SET DEFAULT nextval('public.promotions_id_seq'::regclass);


--
-- Name: support_messages id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_messages ALTER COLUMN id SET DEFAULT nextval('public.support_messages_id_seq'::regclass);


--
-- Name: support_tickets id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_tickets ALTER COLUMN id SET DEFAULT nextval('public.support_tickets_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.alembic_version (version_num) FROM stdin;
9094bd186ddb
\.


--
-- Data for Name: cart_items; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.cart_items (id, cart_id, product_id, quantity, created_at) FROM stdin;
\.


--
-- Data for Name: carts; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.carts (id, user_id, created_at, updated_at) FROM stdin;
1	1	2026-08-26 16:50:09.688364	2026-08-26 16:50:09.688367
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.categories (id, name, description, image, sort_order, is_active, created_at) FROM stdin;
2	Produits test	Catégorie de démonstration	\N	1	t	2026-08-26 18:39:59.802894
\.


--
-- Data for Name: information; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.information (id, title, content, is_active, updated_at, presentation, address, opening_hours, payment, pickup, contact, additional) FROM stdin;
2	INFORMATIONS	🛍️ Boutique\n💵 Paiement en liquide sur place\n📦 Retrait directement en boutique\n\nMerci de votre confiance !	t	2026-08-26 22:15:35.149017	Bienvenue dans notre boutique	test	11h00 / 20h00	sur place			
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.order_items (id, order_id, product_id, product_name, unit_price, quantity, subtotal) FROM stdin;
1	1	1	Produit de test	10.00	3	30.00
2	2	1	Produit de test	10.00	1	10.00
3	3	1	Produit de test	10.00	2	20.00
4	4	1	Produit de test	10.00	1	10.00
5	5	1	Produit de test	10.00	1	10.00
6	6	1	Produit de test	10.00	1	10.00
7	7	1	Produit de test	10.00	1	10.00
8	8	1	Produit de test	10.00	1	10.00
9	9	1	Produit de test	10.00	1	10.00
10	10	1	Produit de test	10.00	2	20.00
11	11	2	457	2353.00	3	7059.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.orders (id, user_id, status, total, payment_method, customer_note, created_at, updated_at) FROM stdin;
5	1	COMPLETED	10.00	CASH	\N	2026-08-26 17:20:27.719958	2026-08-26 17:43:25.095043
6	1	COMPLETED	10.00	CASH	\N	2026-08-26 17:32:59.73338	2026-08-26 17:43:28.551118
4	1	CANCELLED	10.00	CASH	\N	2026-08-26 17:17:46.500349	2026-08-26 17:52:10.658917
3	1	CANCELLED	20.00	CASH	\N	2026-08-26 17:13:43.246637	2026-08-26 17:52:14.868531
2	1	CANCELLED	10.00	CASH	\N	2026-08-26 17:06:47.535689	2026-08-26 17:52:19.608549
1	1	CANCELLED	30.00	CASH	\N	2026-08-26 17:01:18.287915	2026-08-26 17:52:29.393371
7	1	CANCELLED	10.00	CASH	\N	2026-08-26 17:52:44.518378	2026-08-26 17:54:53.250943
8	1	COMPLETED	10.00	CASH	\N	2026-08-26 17:57:42.257197	2026-08-26 17:58:01.891666
9	1	COMPLETED	10.00	CASH	\N	2026-08-26 18:03:04.159037	2026-08-26 18:03:13.804949
10	1	COMPLETED	20.00	CASH	\N	2026-08-26 18:03:56.157137	2026-08-26 18:04:02.658797
11	1	PENDING	7059.00	CASH	\N	2026-08-26 20:04:19.326263	2026-08-26 20:04:19.326266
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.products (id, category_id, name, description, price, stock, image, is_active, created_at, updated_at, sku, product_type, sold_count, download_link, created_by, updated_by) FROM stdin;
1	2	Produit de test	Ceci est un produit de démonstration.	10.00	6	\N	t	2026-08-26 18:40:08.369379	2026-08-26 19:21:09.771344	\N	physical	0	\N	\N	\N
2	2	457	35353	2353.00	20	\N	t	2026-08-26 19:09:47.672297	2026-08-26 20:04:19.341578	\N	physical	0	\N	\N	\N
3	2	eff	zfezf	25.00	20	\N	t	2026-08-27 15:55:20.292028	2026-08-27 15:55:20.29203	.	physical	0	\N	8727592009	8727592009
\.


--
-- Data for Name: promotions; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.promotions (id, title, content, is_active, updated_at) FROM stdin;
1	-20%	-20% sur toutes la boutique	t	2026-08-27 13:02:27.073554
\.


--
-- Data for Name: support_messages; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.support_messages (id, ticket_id, sender_type, sender_telegram_id, message, created_at) FROM stdin;
1	1	USER	8727592009	test	2026-08-26 21:30:18.922355
2	2	USER	8727592009	gsges	2026-08-26 21:30:31.106748
3	3	USER	8727592009	gbffn	2026-08-26 21:30:44.344908
4	4	USER	8727592009	h,xh,	2026-08-26 21:30:50.31259
5	4	ADMIN	8727592009	ok	2026-08-26 21:39:02.361674
\.


--
-- Data for Name: support_tickets; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.support_tickets (id, user_id, topic, status, created_at, updated_at) FROM stdin;
1	1	📦 Problème avec une commande	OPEN	2026-08-26 21:30:18.919108	2026-08-26 21:30:18.919113
2	1	🛍️ Question sur un produit	OPEN	2026-08-26 21:30:31.104962	2026-08-26 21:30:31.104966
3	1	📝 Autre demande	OPEN	2026-08-26 21:30:44.343802	2026-08-26 21:30:44.343806
4	1	📝 Autre demande	CLOSED	2026-08-26 21:30:50.311477	2026-08-26 21:39:17.025455
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: telegram_shop
--

COPY public.users (id, telegram_id, username, first_name, last_name, accepted, is_blocked, created_at, updated_at) FROM stdin;
1	8727592009	Imortallhack	Joe L Imortal	Hackworld	t	f	2026-08-26 18:16:10.443332+02	2026-08-26 18:16:10.443332+02
\.


--
-- Name: cart_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.cart_items_id_seq', 11, true);


--
-- Name: carts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.carts_id_seq', 1, true);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.categories_id_seq', 3, true);


--
-- Name: information_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.information_id_seq', 2, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.order_items_id_seq', 11, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.orders_id_seq', 11, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.products_id_seq', 3, true);


--
-- Name: promotions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.promotions_id_seq', 1, true);


--
-- Name: support_messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.support_messages_id_seq', 5, true);


--
-- Name: support_tickets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.support_tickets_id_seq', 4, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: telegram_shop
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: cart_items cart_items_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_pkey PRIMARY KEY (id);


--
-- Name: carts carts_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_pkey PRIMARY KEY (id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: information information_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.information
    ADD CONSTRAINT information_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: promotions promotions_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.promotions
    ADD CONSTRAINT promotions_pkey PRIMARY KEY (id);


--
-- Name: support_messages support_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_messages
    ADD CONSTRAINT support_messages_pkey PRIMARY KEY (id);


--
-- Name: support_tickets support_tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_pkey PRIMARY KEY (id);


--
-- Name: products uq_products_sku; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT uq_products_sku UNIQUE (sku);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: ix_cart_items_cart_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_cart_items_cart_id ON public.cart_items USING btree (cart_id);


--
-- Name: ix_cart_items_product_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_cart_items_product_id ON public.cart_items USING btree (product_id);


--
-- Name: ix_carts_user_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE UNIQUE INDEX ix_carts_user_id ON public.carts USING btree (user_id);


--
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_order_items_order_id ON public.order_items USING btree (order_id);


--
-- Name: ix_orders_created_at; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_orders_created_at ON public.orders USING btree (created_at);


--
-- Name: ix_orders_status; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_orders_status ON public.orders USING btree (status);


--
-- Name: ix_orders_user_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_orders_user_id ON public.orders USING btree (user_id);


--
-- Name: ix_products_category_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_products_category_id ON public.products USING btree (category_id);


--
-- Name: ix_support_messages_ticket_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_support_messages_ticket_id ON public.support_messages USING btree (ticket_id);


--
-- Name: ix_support_tickets_status; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_support_tickets_status ON public.support_tickets USING btree (status);


--
-- Name: ix_support_tickets_user_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE INDEX ix_support_tickets_user_id ON public.support_tickets USING btree (user_id);


--
-- Name: ix_users_telegram_id; Type: INDEX; Schema: public; Owner: telegram_shop
--

CREATE UNIQUE INDEX ix_users_telegram_id ON public.users USING btree (telegram_id);


--
-- Name: cart_items cart_items_cart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_cart_id_fkey FOREIGN KEY (cart_id) REFERENCES public.carts(id) ON DELETE CASCADE;


--
-- Name: cart_items cart_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.cart_items
    ADD CONSTRAINT cart_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE CASCADE;


--
-- Name: carts carts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.carts
    ADD CONSTRAINT carts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id) ON DELETE SET NULL;


--
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: support_messages support_messages_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_messages
    ADD CONSTRAINT support_messages_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.support_tickets(id) ON DELETE CASCADE;


--
-- Name: support_tickets support_tickets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: telegram_shop
--

ALTER TABLE ONLY public.support_tickets
    ADD CONSTRAINT support_tickets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict JpvaHIDNmTNkmunv809ArqbFnmHklh0cNzZu6CtGWD92bnCaQlDwDrWK44HjxW4

