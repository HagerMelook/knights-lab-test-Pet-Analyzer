# Pet Analyzer

**Pet Analyzer** is an AI-powered web application that enables users to upload pet images and receive intelligent insights, including pet classification, detection, and segmentation. The application is built with Flask and integrates state-of-the-art computer vision models to deliver fast and accurate results.

---

## Features

- **AI-Powered Pet Classification**: Classifies pet breeds using a trained ResNet model.
- **Object Detection**: Identifies pets and other objects using YOLOv5.
- **Semantic Segmentation**: Generates pixel-level masks via DeepLabV3.
- **User Authentication**: Only registered users can analyze images.
- **Profile Management**: Upload and update user profile pictures.
- **Image Validation**: Ensures valid formats before processing.
- **Session Management**: Sessions expire when the browser closes.
- **Auto-Cleanup**: Removes uploaded analysis images after suitable period.
- **Light/Dark Mode**: UI adapts based on user preference.
- **Downloadable Reports**: Export analysis as a timestamped PDF report.

---

## Project Structure
pet_analyzer/  
│  
├── app.py  
├── model_utils.py  
├── user.py  
├── yolov5su.pt  
├── instance/  
│   └── users.db  
├── static/  
│   ├── background.jpg  
│   ├── background_1.png  
│   ├── background_2.png  
│   ├── background_reg_8.jpg  
│   ├── uploaded_images/   (auto-created)  
│   └── profile_pics/  
│  
├── templates/  
│   ├── home.html  
│   ├── analyze.html  
│   ├── features.html   
│   ├── about.html  
│   ├── register.html  
│   ├── login.html  
│   ├── profile.html  
│   └──logout.html  
│  
├── requirements.txt  
└── procfile  


---


## Technologies and Tools Used
1. **Backend:**
- Python 3.11 – Programming language.
- Flask – Web framework to handle routing, forms, and rendering templates.
- Flask-SQLAlchemy – ORM for managing the database and user models.
- Flask-Bcrypt – Password hashing for secure user authentication.
- UUID – To generate unique filenames for uploaded images.
- validate_email_address – To check that the inserted email is valid.


2. **Frontend:**
- HTML & CSS – Markup and styling.
- Bootstrap 5 – Responsive and modern UI components.
- JavaScript – Client-side interactivity.
- Jinja2 – Templating engine used with Flask to dynamically render HTML.
- For Emojis - https://emojipedia.org/


3. **AI Models:**
- PyTorch – Deep learning framework used for model inference.
- Torchvision – Image transformation utilities and pre-trained models.
- Ultralytics – Pet detection using YOLO model.


4. **Image Processing:**
- Pillow (PIL) – Image handling and conversion.
- base64 – Encoding segmentation masks for embedding in HTML.


5. **Deployment:**
- GitHub – Version control.
- Render – Cloud platform for Flask app deployment with Gunicorn.
- Procfile – Defines the web process for Render.
- requirements.txt – Lists only required dependencies for production.

  ## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HagerMelook/knights-lab-test-Pet-Analyzer.git
   cd knights-lab-test-Pet-Analyzer

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt

3. **Run the application**
   ```bash
   python app.py
