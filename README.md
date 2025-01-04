# Synthia

Synthia is a Streamlit-based AI application that allows users to upload PDFs and interact with the document’s content through natural language queries. The assistant provides answers via video responses from customizable avatars powered by HeyGen API.

---

# 🌟 Features

📄 **PDF Viewer:** Upload and view PDF documents within the app.

🧠 **AI-Powered Chat:** Ask questions about the content of the uploaded PDF and receive relevant answers.

🎥 **Avatar Video Responses:** Choose from a variety of avatars to deliver answers in a video format using HeyGen.

⚙️ **Session Management:** Manage video streaming sessions seamlessly (create, start, and close sessions).

🔎 **Semantic Search:** Retrieve relevant document chunks to generate accurate answers.

---

# 🛠️ Demo

![Synthia Demo]()

---

# 🎥 UI in Action

###  📄 Upload a PDF

### 🤖 Select an Avatar


### 🎥 Create and Start a Video Session

### Ask a Question and Get a Video Response

### Close the Video Session

---

# 🚀 Getting Started

1️⃣ Installation

1. Clone this repository:
    ```bash
    git clone git@github.com:anujdutt9/Synthia.git
    cd synthia
    ```

2. Create a virtual environment and activate it:
    ```bash
   python3 -m venv venv
    source venv/bin/activate   # macOS/Linux
    .\venv\Scripts\activate    # Windows
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2️⃣ Setup Environment Variables

Create a .env file in the root directory with the following content:
   ```bash
   # HeyGen API Settings
  HEYGEN_API_KEY=<your_heygen_api_key>
  HEYGEN_SERVER_URL=<your_heygen_server_url>
  OPENAI_API_KEY=<your_openai_api_key>
   ```

3️⃣ Run the Application

1.	Launch the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2.	Access the app in your browser: Navigate to the local URL provided in the terminal (e.g., http://localhost:8501).

3. Upload a PDF, select an avatar, and start interacting with Synthia!

---

# 🖼️ Avatar Options

| Avatar Name | Role	 |  Description   |
| ------- | ------------ | --------------------- |
| Judy	  | Teacher	     | Formal and professional avatar |
| Bryan	  | Fitness Coach |	Energetic and engaging avatar |
| Silas	  | Customer Support |	Helpful and friendly avatar |

---

# 🔍 How It Works

1.	**PDF Upload:** Users upload a PDF file, which is processed to extract text and create vector embeddings. 
2. **Text Chunking & Retrieval:** The document content is split into chunks, and the most relevant chunks are retrieved based on user queries. 
3. **Avatar Video Responses:** The HeyGen API is used to create and manage video sessions where avatars deliver AI-generated responses.

---

# 🛠️ Troubleshooting

| Issue                                                                        | Solution	                                                    | 
|------------------------------------------------------------------------------|--------------------------------------------------------------|
| Missing API Keys	                                                            | Ensure the HEYGEN_API_KEY is correctly set in the .env file. |
| Video Not Loading                                                            | 	Verify the HeyGen server URL and API key.                   |
 | PDF Processing Error | 	Ensure the uploaded file is a valid PDF and not empty.      |

---

# 🤝 Contribution

Contributions are welcome! Please fork this repository, create a new branch for your feature or bug fix, and submit a pull request. For major changes, please open an issue to discuss them first.

---

# 📜 License

This project is licensed under the MIT License. See the LICENSE file for more details.