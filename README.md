# Vyaapari Full-Stack Application

Vyaapari is a full-stack inventory management and business analytics application. It features an automated AI assistant powered by IBM watsonx.ai foundation models to provide smart insights, summaries, and business operations support.

---

## 🛠️ Tech Stack

*   **Frontend:** React, Tailwind CSS (Hosted on Render)
*   **Backend:** FastAPI, Python (Hosted on Render)
*   **AI Engine:** IBM watsonx.ai (Llama 3 Foundation Models)

---

## ⚙️ Environment Configuration

To make the AI features work properly on platforms like Render or during local development, you must configure the following environment variables in your backend service:

| Variable Name | Required Value Description |
| :--- | :--- |
| `WATSONX_PROJECT_ID` | The unique Project ID string found under your project's **Manage > General** tab in watsonx.ai. |
| `IBM_CLOUD_API_KEY` | Your private global IBM Cloud IAM API Key used to authenticate requests. |
| `WATSONX_URL` | The regional IBM ML endpoint (e.g., `https://us-south.ml.cloud.ibm.com` for Dallas). |

> ⚠️ **Important:** Never hardcode your `WATSONX_PROJECT_ID` or `IBM_CLOUD_API_KEY` directly into your Python files. Always use `os.environ.get()` to load them securely from the environment.

---

## 🚀 Quick Start Guide

Click on either tab below to view the respective setup instructions:

<details>
<summary><b>🖥️ Backend Setup (FastAPI)</b></summary>
<br>

Navigate to your backend directory, install the required dependencies, and launch the server:

```bash
# Clone the repository
git clone [https://github.com/your-username/vyaapari-api.git](https://github.com/your-username/vyaapari-api.git)

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload

Navigate to your frontend directory, install the packages, and run the client:

Bash
# Install NPM packages
npm install

# Start the frontend app
npm start
