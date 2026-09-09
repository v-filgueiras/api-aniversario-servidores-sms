CREATE TABLE IF NOT EXISTS api_aniversario_servidores (

    id SERIAL PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    full_name VARCHAR(150) NOT NULL,
    birth_date TIMESTAMP NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS birthday_send_history (

    id SERIAL PRIMARY KEY,
    employee_id INTEGER REFERENCES api_aniversario_servidores(id),
    full_name VARCHAR(150) NOT NULL,
    recipient_email VARCHAR(150) NOT NULL,
    status VARCHAR(20) NOT NULL,
    error_message TEXT,
    provider_id VARCHAR(120),
    sent_at TIMESTAMP NOT NULL DEFAULT NOW()
);
