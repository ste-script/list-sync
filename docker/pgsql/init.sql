CREATE TABLE public.newtable (
	id serial4 NOT NULL,
	"text" varchar NULL,
	CONSTRAINT newtable_pk PRIMARY KEY (id)
);

CREATE PUBLICATION my FOR TABLE newtable;