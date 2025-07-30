💰 SBI Statement Analyzer

A lightweight web app to analyze SBI bank statements (.csv format) and generate meaningful insights, graphs, and summaries — all in one click.

🚀 Features
- 📁 Upload your SBI bank statement (.csv)
- 📊 Generates:
  - Bar chart for monthly Credit vs Debit
  - Line chart for Net Monthly Change
  - Summary insights in readable text
- 📦 Automatically saves a full Excel report to `/reports`
- ⚡ Fast, simple, and works offline

🛠 Tech Stack
- Backend: Python (Flask, Pandas, Matplotlib, Seaborn)
- Frontend: HTML, CSS, Vanilla JS
- Excel Writer: `xlsxwriter`

📂 Folder Structure
SBI_Analyzer/

├── app.py # Flask backend

├── sbi_analysis.py # Core analysis logic

├── templates/

│ └── index.html # Frontend page

├── static/

│ └── style.css # CSS styling

├── uploads/ # Uploaded CSVs

├── reports/ # Output charts + Excel

└── README.md

🧠 Sample Output
- 📈 Charts rendered on-screen
- 🧾 Text insights shown dynamically
- 📥 Downloadable Excel report saved under `/reports`

✅ Sample Input Format
Make sure your SBI statement `.csv` is in the format exported from the SBI NetBanking portal (after removing unnecessary headers if needed).

📌 To-Do
- [ ] Add category-wise spending pie chart
- [ ] Add user authentication (optional)
- [ ] Deploy on Render / Railway

🧑‍💻 Author
Om Prakash Varma
📍 Built with frustration and a lot of trial-and-error.

📜 License
MIT License — Free to use and modify with credits.

📸Screen-Shoots

Home Page:
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6642195b-523a-49b0-89ae-839f888f0e43" />

Output:
📊 Bar Graph
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/254f0375-faef-48ef-a4a4-872d283943c7" />

📈 Line Graph and 💰 Text inshights
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/0da2fa9c-2ea7-404e-a46b-17b5c17249e4" />
