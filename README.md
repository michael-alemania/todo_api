# ✅ TODO API

---

## ⚙️ Setup

1. **Create PostgreSQL database**  
   Name it `todo_dev` (or any name you prefer).

2. **Set environment variable**  
   export env variable:

   ```bash
   export DATABASE_URL='postgresql://username:password@localhost:5432/todo_dev'
   ```

3. **Install dependencies and set up the app**  
   ```bash
   make setup
   ```

4. **Run database migration to create tables**  
   ```bash
   make migrate
   ```

5. **Start the server**  
   ```bash
   make run
   ```

---

## 🌱 Seed the Database (Optional)

1. **Generate SQL for 1 million tasks**
   ```bash
   python3 generate_tasks_sql.py
   ```

2. **Import the SQL file into PostgreSQL**
   ```bash
   psql $DATABASE_URL -f tasks.sql
   ```

---

## 📘 API Endpoints

### 🗂 Tasks

| Method | Endpoint         | Description                            |
|--------|------------------|----------------------------------------|
| GET    | `/tasks`         | List tasks (offset pagination)         |
| GET    | `/tasks/{id}`    | Get a single task by ID                |
| POST   | `/tasks`         | Create a new task                      |
| PUT    | `/tasks/{id}`    | Update a task                          |
| DELETE | `/tasks/{id}`    | Delete a task                          |
| POST   | `/tasks/reorder` | Reorder a task                         |
