## Database Schema (MySQL)

### users

- `id` INT PK
- `email` VARCHAR(255) UNIQUE NOT NULL
- `hashed_password` VARCHAR(255) NOT NULL
- `full_name` VARCHAR(255)
- `role` VARCHAR(20) NOT NULL (`user` or `admin`)
- `created_at` DATETIME NOT NULL

### tickets

- `id` INT PK
- `title` VARCHAR(255) NOT NULL
- `description` TEXT NOT NULL
- `category` VARCHAR(50) NOT NULL
- `impact` VARCHAR(20) NOT NULL
- `urgency` VARCHAR(20) NOT NULL
- `priority` VARCHAR(5) NOT NULL
- `status` VARCHAR(20) NOT NULL
- `reopen_count` INT NOT NULL
- `sla_deadline` DATETIME NOT NULL
- `created_at` DATETIME NOT NULL
- `updated_at` DATETIME NOT NULL
- `creator_id` INT FK -> `users.id`

### comments

- `id` INT PK
- `ticket_id` INT FK -> `tickets.id`
- `author_id` INT FK -> `users.id`
- `body` TEXT NOT NULL
- `visibility` VARCHAR(20) NOT NULL (`PUBLIC` / `INTERNAL`)
- `created_at` DATETIME NOT NULL

### attachments

- `id` INT PK
- `ticket_id` INT FK -> `tickets.id`
- `filename` VARCHAR(255) NOT NULL
- `content_type` VARCHAR(100) NOT NULL
- `file_path` VARCHAR(500) NOT NULL
- `created_at` DATETIME NOT NULL

### ticket_events

- `id` INT PK
- `ticket_id` INT FK -> `tickets.id`
- `event_type` VARCHAR(50) NOT NULL
- `payload` TEXT
- `created_at` DATETIME NOT NULL

Used event types:

- `TICKET_CREATED`
- `STATUS_CHANGED`
- `PRIORITY_COMPUTED`
- `COMMENT_ADDED`
- `TICKET_REOPENED`
- `ATTACHMENT_ADDED`

