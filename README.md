# AI Medical Chatbot Server

This project is an AI assistant designed to support doctors by providing fast, reliable, and context-aware medical information. The chatbot leverages advanced language models and modern tooling to offer conversational assistance, help with medical queries, and integrate seamlessly into clinical workflows.

## 🚀 Features

- **Contextual Medical Conversations**: Engages with users using medical terminology and understands follow-up questions.
- **Domain-Specific Knowledge**: Tailored for healthcare and medical applications.
- **Framework Integration**: Built using LangChain and LangGraph for powerful conversational AI pipelines.
- **Extensible Architecture**: Easily extendable with new data sources, models, and plug-ins.

## 🧠 Tech Stack

- **LangChain**: For managing language model prompts, memory, and agent workflows.
- **LangGraph**: For building and visualizing reasoning graphs and complex workflows.
- **Python **: The primary programming language version `3.12.1`

## 📂 Repository Structure

```
ai_medical_chatbot_server/
├── README.md          # Project overview (this file)
└── ...                # Additional modules and
```

> **Note:** This is an evolving repository; the structure will expand as features are implemented.

## 🛠️ Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/myprescription2026/mypresc-chatbot.git
   cd mypresc-chatbot
   ```

2. **Install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Create a `.env` file to store API keys  
     see `.env.example`

4. **Run the server**
   ```bash
   uvicorn server.main:app
   ```
   or
   ```bash
   python -m server.main
   ```
5. **using nginx**:
   ```bash
   #install nginx
   sudo apt install nginx
   # start nginx
   sudo nginx
   # remove default config
   sudo rm /etc/nginx/sites-enabled/default
   sudo rm /etc/nginx/sites-available/default
   # copy the nginx folder in /etc/nginx/conf.d/
   sudo cp ./nginx/conf.conf /etc/nginx/conf.d/
   # reload nginx
   sudo nginx -s reload
   # test if runing
   curl localhost/health #should get {"status":"ok"}
   ```
6. **Interact with the chatbot**
   - Use the provided API endpoint or CLI interface to ask medical questions.

## 🧩 Extending the Assistant

- Add new LangChain tools and agents for specialized tasks (e.g., drug interactions, diagnostics).
- Integrate LangGraph nodes for complex decision-making and reasoning paths.
- Connect with external medical databases or EHR systems.

## ✅ Contribution

Contributions are welcome! Please fork the repo and create a pull request with detailed descriptions of your changes. Adhere to standard code quality practices and include tests where applicable.
