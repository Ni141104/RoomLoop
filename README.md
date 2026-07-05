# RoomLoop Database Foundation

## MySQL Prerequisites

- MySQL Community Server 8.x or a compatible MySQL 8 server
- MySQL client tools or MySQL Workbench to run the SQL scripts

## Database Creation

Create the `roomloop` database before running the SQL scripts. The schema script creates it if it does not already exist, so `DATABASE_NAME` should be set to `roomloop`.

## Execute `schema.sql`

Run the schema initialization script to create the `rooms`, `recurring_series`, and `bookings` tables:

```bash
mysql -h "$DATABASE_HOST" -P "$DATABASE_PORT" -u "$DATABASE_USER" -p < database/schema.sql
```

## Execute `seed.sql`

After the schema is created, load the seed data:

```bash
mysql -h "$DATABASE_HOST" -P "$DATABASE_PORT" -u "$DATABASE_USER" -p "$DATABASE_NAME" < database/seed.sql
```

## Required Environment Variables

Set the following environment variables for the MySQL connection used by the application:

- `DATABASE_HOST`
- `DATABASE_PORT`
- `DATABASE_NAME`
- `DATABASE_USER`
- `DATABASE_PASSWORD`