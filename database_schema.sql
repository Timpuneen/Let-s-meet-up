-- ============================================
-- Database Schema for Let's Meet Up Platform
-- ============================================

-- Table: users
-- Кастомная таблица пользователей
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    password VARCHAR(128) NOT NULL,  -- Хешированный пароль
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Комментарии для users
COMMENT ON TABLE users IS 'Таблица пользователей платформы';
COMMENT ON COLUMN users.id IS 'Уникальный идентификатор пользователя';
COMMENT ON COLUMN users.email IS 'Email пользователя (используется для входа)';
COMMENT ON COLUMN users.name IS 'Имя пользователя';
COMMENT ON COLUMN users.password IS 'Хешированный пароль (pbkdf2_sha256)';
COMMENT ON COLUMN users.is_active IS 'Активен ли пользователь';
COMMENT ON COLUMN users.is_staff IS 'Доступ к админ-панели';
COMMENT ON COLUMN users.is_superuser IS 'Суперпользователь (все права)';
COMMENT ON COLUMN users.last_login IS 'Дата последнего входа';
COMMENT ON COLUMN users.created_at IS 'Дата регистрации';

-- ============================================

-- Table: events
-- Таблица мероприятий
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    date TIMESTAMP NOT NULL,
    organizer_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign Key
    CONSTRAINT fk_events_organizer 
        FOREIGN KEY (organizer_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE
);

-- Индексы для events
CREATE INDEX idx_events_date ON events(date);
CREATE INDEX idx_events_organizer_id ON events(organizer_id);
CREATE INDEX idx_events_created_at ON events(created_at);

-- Комментарии для events
COMMENT ON TABLE events IS 'Таблица мероприятий';
COMMENT ON COLUMN events.id IS 'Уникальный идентификатор мероприятия';
COMMENT ON COLUMN events.title IS 'Название мероприятия';
COMMENT ON COLUMN events.description IS 'Описание мероприятия';
COMMENT ON COLUMN events.date IS 'Дата и время проведения';
COMMENT ON COLUMN events.organizer_id IS 'ID организатора (FK -> users)';
COMMENT ON COLUMN events.created_at IS 'Дата создания записи';
COMMENT ON COLUMN events.updated_at IS 'Дата последнего обновления';

-- ============================================

-- Table: events_participants
-- Промежуточная таблица Many-to-Many для участников мероприятий
CREATE TABLE events_participants (
    id BIGSERIAL PRIMARY KEY,
    event_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    
    -- Foreign Keys
    CONSTRAINT fk_participants_event 
        FOREIGN KEY (event_id) 
        REFERENCES events(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_participants_user 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    -- Уникальное ограничение: пользователь может быть зарегистрирован на мероприятие только один раз
    CONSTRAINT unique_event_user 
        UNIQUE (event_id, user_id)
);

-- Индексы для events_participants
CREATE INDEX idx_events_participants_event_id ON events_participants(event_id);
CREATE INDEX idx_events_participants_user_id ON events_participants(user_id);

-- Комментарии для events_participants
COMMENT ON TABLE events_participants IS 'Связь между мероприятиями и участниками (Many-to-Many)';
COMMENT ON COLUMN events_participants.id IS 'Уникальный идентификатор записи';
COMMENT ON COLUMN events_participants.event_id IS 'ID мероприятия (FK -> events)';
COMMENT ON COLUMN events_participants.user_id IS 'ID участника (FK -> users)';

-- ============================================

-- Django-специфичные таблицы (для полноты картины)
-- ============================================

-- Table: django_migrations
CREATE TABLE django_migrations (
    id BIGSERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL
);

-- Table: django_content_type
CREATE TABLE django_content_type (
    id BIGSERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    CONSTRAINT unique_app_model UNIQUE (app_label, model)
);

-- Table: django_session
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL
);

CREATE INDEX idx_django_session_expire_date ON django_session(expire_date);

-- ============================================
-- RELATIONSHIPS SUMMARY
-- ============================================
-- 1. users (1) -> events (N) : One user can organize many events
-- 2. events (N) <-> users (N) : Many-to-Many through events_participants
--    - One event can have many participants
--    - One user can participate in many events
