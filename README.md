# Single Agent Task Assistant

A FastAPI-based task management application developed for **COIT12204 – AI-Assisted Software Development, Assessment 3**.

The project extends a standard task-management REST API with a **single AI Due Date Agent**. The agent uses **LangChain** and **Google Gemini** to suggest suitable due dates based on task information and priority.

The application also includes LangChain tool usage, internal agent state, input/output validation, deterministic fallback logic, logging, and automated testing with pytest.

## Features

### Task Management

The application provides REST API endpoints for basic task management:

- Create a task
- View all tasks
- View a task by ID
- Update a task
- Delete a task

### AI Due Date Agent

The Due Date Agent can:

- Accept a task title, description, and priority
- Accept an optional existing task ID
- Retrieve stored task information using a LangChain tool
- Send structured task information to Google Gemini
- Generate a suggested due date
- Validate the AI-generated date
- Reject past or incorrectly formatted dates
- Use deterministic fallback dates when AI output is invalid
- Continue operating when the LLM raises an exception
- Record agent state and activity
- Produce logs for debugging and observability

## Technology Stack

- Python 3.11
- FastAPI
- Pydantic
- LangChain
- Google Gemini
- langchain-google-genai
- google-genai
- Uvicorn
- pytest
- HTTPX
- python-dotenv


## Project Structure

```text
Single-Agent-Task-Assistant/
│
├── agents/
│   ├── __init__.py
│   ├── agent_state.py
│   ├── due_date_agent.py
│   └── tools.py
│
├── api/
│   ├── __init__.py
│   ├── agent_routes.py
│   └── routes.py
│
├── models/
│   ├── __init__.py
│   └── task.py
│
├── services/
│   ├── __init__.py
│   └── task_service.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_agent_routes.py
│   ├── test_agent_state.py
│   ├── test_agent_tools.py
│   ├── test_api_routes.py
│   ├── test_due_date_agent.py
│   ├── test_task_model.py
│   └── test_task_service.py
│
├── utils/
│   ├── __init__.py
│   └── llm_client.py
│
├── .env.example
├── .gitignore
├── main.py
├── requirements.txt
└── README.md
```

## System Architecture

The main agent workflow is:

```text
User Request
     |
     v
FastAPI Endpoint
     |
     v
Pydantic Input Validation
     |
     v
Due Date Agent
     |
     +--------------------+
     |                    |
     v                    |
lookup_task Tool          |
(optional task_id)        |
     |                    |
     +--------------------+
     |
     v
LangChain Prompt
     |
     v
Google Gemini
     |
     v
Extract AI Response
     |
     v
Validate Due Date
     |
     +----------------------+
     |                      |
   Valid                  Invalid/Error
     |                      |
     v                      v
AI Date              Fallback Date
     |                      |
     +----------+-----------+
                |
                v
         Update AgentState
                |
                v
             Logging
                |
                v
      Structured API Response
```

## Agent Prompt

The Due Date Agent uses a LangChain `ChatPromptTemplate`.

The prompt provides Gemini with:

- Today's date
- Task title
- Task description
- Task priority
- Stored task information

The agent is instructed to:

1. Return only one date.
2. Use `YYYY-MM-DD` format.
3. Never return a date before today's date.
4. Return no additional explanation.

The generated output is still validated by Python before it is accepted.

## LangChain Tool

The application contains a `lookup_task` LangChain tool.

The tool retrieves an existing task from the shared task service using its task ID.

Example:

```python
lookup_task.invoke(
    {
        "task_id": 1
    }
)
```

The tool can provide the agent with:

- Task ID
- Title
- Description
- Priority
- Existing due date

This allows the agent to use information already stored by the task-management application.

## Agent State

The application maintains an internal `AgentState`.

The state tracks:

```text
last_suggestion
error_count
history
last_tool_call
```

### `last_suggestion`

Stores the most recent final due-date suggestion.

### `error_count`

Tracks validation or execution errors encountered by the agent.

### `history`

Stores important actions performed during agent execution.

### `last_tool_call`

Stores the most recently used LangChain tool.

The application logs important state information to make agent behaviour easier to inspect and debug.

## Due Date Validation

AI-generated output is not trusted automatically.

The application checks that the result:

- Uses `YYYY-MM-DD`
- Represents a real date
- Is not before today's date

For example:

```text
2026-09-25
```

is valid if it is a current or future date.

An output such as:

```text
next Friday
```

is rejected because it does not match the required format.

## Fallback Guardrails

If Gemini returns an invalid response or an unexpected LLM error occurs, the application generates a deterministic fallback date.

| Priority | Fallback |
|---|---|
| High | Today + 3 days |
| Normal | Today + 7 days |
| Low | Today + 14 days |

For example, if Gemini returns:

```text
next Friday
```

for a high-priority task, the invalid response is rejected and the application returns:

```text
today + 3 days
```

This prevents malformed LLM output from causing the complete agent workflow to fail.

# API Endpoints

## Root Endpoint

```http
GET /
```

Example response:

```json
{
  "message": "Single Agent Task Assistant API"
}
```

---

## Create Task

```http
POST /tasks
```

Example request:

```json
{
  "title": "Complete Assessment 3",
  "description": "Finish the assessment",
  "priority": "high"
}
```

## Get All Tasks

```http
GET /tasks
```

## Get Task by ID

```http
GET /tasks/{task_id}
```

Example:

```http
GET /tasks/1
```

## Update Task

```http
PUT /tasks/{task_id}
```

## Delete Task

```http
DELETE /tasks/{task_id}
```

# AI Agent Endpoint

The main AI endpoint is:

```http
POST /api/agent/suggest_due_date
```

Example request:

```json
{
  "task_id": 1,
  "title": "Complete Assessment 3",
  "description": "Finish coding, testing, report and demonstration video",
  "priority": "high"
}
```

Example successful response:

```json
{
  "suggested_due_date": "2026-09-21",
  "status": "success"
}
```

The `task_id` is optional.

Example request without an existing task:

```json
{
  "title": "Study pytest",
  "description": "Review automated testing",
  "priority": "normal"
}
```

## Input Validation

The API validates incoming data before calling the agent.

Supported priority values are:

```text
low
normal
high
```

For example:

```json
{
  "title": "Complete Assessment 3",
  "priority": "urgent"
}
```

is rejected because `urgent` is not an accepted priority.

FastAPI returns:

```text
422 Unprocessable Entity
```

This acts as an input guardrail and prevents invalid data from reaching the AI workflow.

# Installation and Setup

The following instructions explain how to install and run the project on both **Windows** and **macOS**.

## Prerequisites

Before installing the project, make sure you have:

- Python 3.11 or a compatible Python 3 version
- pip
- Git
- Internet connection
- Google Gemini API key

# Windows Installation

## 1. Check Python and Git

Open **PowerShell** and run:

```powershell
python --version
```

Check Git:

```powershell
git --version
```

The project was developed using Python 3.11.

## 2. Clone the Repository

Clone the GitHub repository:

```powershell
git clone https://github.com/prajitabhandari1234/Single-Agent-Task-Assistant.git
```

Move into the project directory:

```powershell
cd Single-Agent-Task-Assistant
```

## 3. Create a Virtual Environment

Create the virtual environment:

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal should display something similar to:

```text
(.venv) PS C:\...\Single-Agent-Task-Assistant>
```

### PowerShell Execution Policy Error

If PowerShell prevents the activation script from running, execute:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

If using Windows Command Prompt instead of PowerShell:

```cmd
.venv\Scripts\activate.bat
```

## 4. Upgrade pip

Run:

```powershell
python -m pip install --upgrade pip
```

## 5. Install Dependencies

Install all required dependencies:

```powershell
pip install -r requirements.txt
```

This installs the libraries required by the application, including FastAPI, Uvicorn, LangChain, Google Gemini integration, Pydantic, pytest, HTTPX, and python-dotenv.

## 6. Configure the Gemini API Key

The application requires a Google Gemini API key.

The repository contains:

```text
.env.example
```

Create a `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Open the newly created `.env` file and add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace:

```text
your_gemini_api_key_here
```

with your actual Gemini API key.

## 7. Run the Application

Start the FastAPI application:

```powershell
uvicorn main:app --reload
```

For detailed logging:

```powershell
uvicorn main:app --reload --access-log --log-level info
```

The application will run locally at:

```text
http://127.0.0.1:8000
```

## 8. Open Swagger UI

Open a browser and go to:

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to manually test the CRUD endpoints and the AI Due Date Agent.

## 9. Run Automated Tests

With the virtual environment still activated, run:

```powershell
pytest -v
```

The completed project test suite produced:

```text
51 passed, 3 warnings
```

The warnings are deprecation warnings and do not represent failed tests.

To run only the Due Date Agent tests:

```powershell
pytest tests/test_due_date_agent.py -v
```

## 10. Stop the Application

Press:

```text
Ctrl + C
```

in the terminal running Uvicorn.

To deactivate the virtual environment:

```powershell
deactivate
```

# macOS Installation

## 1. Check Python and Git

Open **Terminal**.

Check Python:

```bash
python3 --version
```

Check Git:

```bash
git --version
```

The project was developed using Python 3.11.

## 2. Clone the Repository

Clone the GitHub repository:

```bash
git clone https://github.com/prajitabhandari1234/Single-Agent-Task-Assistant.git
```

Move into the project:

```bash
cd Single-Agent-Task-Assistant
```

## 3. Create a Virtual Environment

Create the Python virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, the terminal should display something similar to:

```text
(.venv) user@MacBook Single-Agent-Task-Assistant %
```

## 4. Upgrade pip

Run:

```bash
python -m pip install --upgrade pip
```

## 5. Install Dependencies

Install all project dependencies:

```bash
pip install -r requirements.txt
```

Alternatively:

```bash
python -m pip install -r requirements.txt
```

## 6. Configure the Gemini API Key

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

You can open the file using any text editor.

For example:

```bash
nano .env
```

Add your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Replace the placeholder with your actual Gemini API key.

If using `nano`, save using:

```text
Control + O
```

Press Enter, then exit using:

```text
Control + X
```

## 7. Run the Application

Start the FastAPI application:

```bash
uvicorn main:app --reload
```

For detailed logging:

```bash
uvicorn main:app --reload --access-log --log-level info
```

If the `uvicorn` command is not found, run:

```bash
python -m uvicorn main:app --reload
```

The application will run locally at:

```text
http://127.0.0.1:8000
```

## 8. Open Swagger UI

Open a browser and go to:

```text
http://127.0.0.1:8000/docs
```

Swagger UI can be used to test:

- Task creation
- Task retrieval
- Task updates
- Task deletion
- Due Date Agent
- Request validation
- Structured responses

## 9. Run Automated Tests

With the virtual environment activated, run:

```bash
pytest -v
```

The completed test suite produced:

```text
51 passed, 3 warnings
```

To run only the Due Date Agent tests:

```bash
pytest tests/test_due_date_agent.py -v
```

## 10. Stop the Application

Press:

```text
Control + C
```

in the Terminal window running Uvicorn.

Deactivate the virtual environment:

```bash
deactivate
```

# Quick Start

## Windows PowerShell

```powershell
git clone https://github.com/prajitabhandari1234/Single-Agent-Task-Assistant.git
cd Single-Agent-Task-Assistant

python -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env

# Add your Gemini API key to .env

uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## macOS

```bash
git clone https://github.com/prajitabhandari1234/Single-Agent-Task-Assistant.git
cd Single-Agent-Task-Assistant

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env

# Add your Gemini API key to .env

uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

# Environment Configuration

The application requires a Google Gemini API key.

The `.env` file should contain:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

## Important Security Requirement

Do **not** commit your real `.env` file or Gemini API key to GitHub.

The `.gitignore` file should exclude:

```text
.env
.venv/
__pycache__/
.pytest_cache/
```

Only `.env.example` should be committed.

A safe `.env.example` file should contain:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

# Troubleshooting

## Gemini API Key Missing

If the application reports:

```text
GEMINI_API_KEY is missing from the environment
```

check that:

1. A `.env` file exists in the project root.
2. The variable is named exactly `GEMINI_API_KEY`.
3. The placeholder has been replaced with a valid API key.
4. Uvicorn has been restarted after changing `.env`.

## Module Not Found

If Python reports that a module cannot be found, confirm that the virtual environment is activated.

Then run:

```bash
pip install -r requirements.txt
```

## Port 8000 Already in Use

If port `8000` is already being used, stop the existing process or start the application using another port:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001/docs
```

## Virtual Environment Is Not Active

On Windows PowerShell, the terminal normally begins with:

```text
(.venv) PS ...
```

On macOS, it normally begins with:

```text
(.venv) ...
```

If `(.venv)` is not displayed, activate the environment again before running the application.

# Testing

The project uses **pytest** for automated testing.

Run the complete test suite with:

```bash
pytest -v
```

The completed test suite produced:

```text
51 passed, 3 warnings
```

The warnings are deprecation warnings and do not represent test failures.

## Test Coverage

The tests cover:

- Task model validation
- Task service CRUD operations
- FastAPI CRUD endpoints
- Agent state
- LangChain task lookup tool
- Due-date validation
- Priority-based fallback logic
- LLM response extraction
- Due Date Agent behaviour
- FastAPI agent endpoint
- Invalid API input
- Missing tasks
- Invalid LLM responses
- Empty LLM responses
- LLM exceptions
- Agent fallback behaviour
- State updates

## Mocked LLM Testing

Automated tests do not depend on real Gemini responses.

The Gemini/LangChain call is mocked using pytest `monkeypatch`.

Example:

```python
def mock_invoke(data):
    return AIMessage(content=future_date)

monkeypatch.setattr(
    due_date_agent.due_date_chain,
    "invoke",
    mock_invoke
)
```

This allows agent behaviour to be tested without:

- Making real Gemini API calls
- Depending on network connectivity
- Consuming API quota
- Receiving unpredictable LLM responses

# Failure Testing

The agent was deliberately tested against several failure scenarios.

## Invalid LLM Output

Example mocked output:

```text
next Friday
```

Result:

```text
Validation failed
→ fallback date generated
→ agent continued successfully
```

## Empty LLM Output

Example:

```text
""
```

Result:

```text
Empty response rejected
→ fallback date generated
```

## LLM Exception

Example simulated error:

```python
raise RuntimeError("Mock Gemini failure")
```

Result:

```text
Exception recorded
→ AgentState updated
→ fallback date generated
→ application continued
```

These tests demonstrate that the application does not rely on the LLM always returning a valid response.

# Logging and Observability

Logging is used throughout the application to make agent execution observable.

Example log sequence:

```text
Due date request received
Agent state before run
Due date agent started
lookup_task called
Raw Gemini output received
Valid due date accepted
Final due date suggestion
Agent state after run
Agent endpoint returning due date
```

Errors and fallback decisions are also logged.

This helps with debugging and evaluating agent behaviour.

# Limitations

The current version has several limitations.

## In-Memory Storage

Tasks and agent state are stored in memory.

Restarting the application clears stored data.

This means that if a task is created and the Uvicorn server is restarted, the task must be created again before its `task_id` can be used by the Due Date Agent.

## Simple Fallback Strategy

Fallback dates are based only on priority and do not consider:

- Weekends
- Public holidays
- User workload
- Calendar availability
- Actual assignment deadlines

## LLM Date Suitability

Validation ensures that the output is correctly formatted and not in the past, but it cannot guarantee that every AI-generated date is the ideal deadline.

## Tool Selection

The `lookup_task` tool is called by the application when a `task_id` is supplied.

The LLM does not currently autonomously decide when the tool should be called.

# Future Improvements

Possible future improvements include:

- Persistent database storage
- Per-user agent state
- Calendar integration
- Workload-aware due-date suggestions
- Structured LLM output
- Additional LangChain tools
- Autonomous tool selection
- More advanced scheduling rules
- Additional integration tests
- Deployment to a cloud environment

# Security

The Gemini API key is stored using an environment variable and is not hard-coded into the application.

Never commit:

```text
.env
```

to the repository.

If an API key is accidentally committed or publicly exposed, it should be revoked and replaced immediately.

# AI Assistance Declaration

Generative AI tools were used during the development of this assignment as a supporting resource for understanding technical concepts, troubleshooting implementation issues, reviewing code structure, improving documentation, and assisting with the testing and development process.

AI-generated suggestions were reviewed, tested, and adapted before being incorporated into the project. The final implementation was developed and verified through the FastAPI application, LangChain-based Due Date Agent, Google Gemini integration, agent state management, tool usage, validation and fallback mechanisms, logging, and automated testing using pytest. Git and GitHub were used throughout the development process to maintain version history and document incremental changes.

The final application reflects my understanding of the implemented architecture, FastAPI endpoint integration, LangChain and LLM integration, agent state management, tool usage, input and output validation, fallback and error handling, logging, and automated testing. All final implementation decisions, testing results, and submitted work were reviewed and verified by me.

# Author

**Prajita Bhandari**
