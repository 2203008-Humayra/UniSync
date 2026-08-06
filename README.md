# UniSync

## Anonymous Student Feedback & Complaint Management System

UniSync is a Flask-based web application that enables students to anonymously submit complaints, suggestions and appreciation to the Director of Student Welfare (DSW). Students can track their complaints using a unique tracking ID while maintaining anonymity.

---

# Project Structure

```
UniSync/
│
├── app.py
│
├── database/
│   └── unisync.sql
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
└── templates/
    ├── base.html
    ├── home.html
    ├── verify.html
    ├── complaint_form.html
    ├── complaint_success.html
    ├── track.html
    ├── dsw_portal.html
    ├── dsw_dashboard.html
    ├── suggestion.html
    ├── appreciation.html
    ├── about.html
    ├── faq.html
    └── contact.html
```

---

# File Responsibilities

### app.py
- Flask application
- URL routing
- Backend logic
- Database connection

### database/unisync.sql
- Database schema
- Tables and relationships

### base.html
- Shared layout
- Navigation bar
- Footer
- Common resources

### home.html
- Homepage
- Hero section
- Announcements
- Quick actions
- Categories
- Statistics

### verify.html
- Student verification

### complaint_form.html
- Complaint submission form

### complaint_success.html
- Complaint submission confirmation
- Tracking ID display

### track.html
- Complaint tracking page

### dsw_portal.html
- DSW login page

### dsw_dashboard.html
- DSW dashboard
- Complaint management
- Investigation
- Status updates

### suggestion.html
- Suggestion submission UI

### appreciation.html
- Appreciation submission UI

### about.html
- About UniSync

### faq.html
- Frequently Asked Questions

### contact.html
- Contact information

---

# Static Folder

## css/
Contains page-specific stylesheets.

## js/
Contains JavaScript files.

## images/
Stores project images and assets.

---

# Team Task Distribution

## 2203008 (Project Lead) 

### Files
- app.py
- database/unisync.sql
- templates/base.html
- templates/home.html
- templates/verify.html
- templates/complaint_form.html
- templates/complaint_success.html
- templates/track.html
- templates/dsw_dashboard.html

### CSS
- home.css
- verify.css
- complaint_form.css
- complaint_success.css
- track.css
- dsw_dashboard.css

### Responsibilities
- Project architecture
- Flask backend
- Database
- Student verification
- Complaint submission
- Complaint tracking
- DSW Dashboard
- Investigation workflow
- Evidence request feature
- Statistics
- Final integration
- Git & GitHub management

---

## 2203049

### Files
- templates/dsw_portal.html

### CSS
- dsw_portal.css

### JS
- dsw_portal.js (if required)

### Responsibilities
- DSW login UI
- Login authentication
- Session management
- Logout functionality
- Homepage announcement management

---

## 2203051

### Files
- templates/about.html
- templates/faq.html
- templates/contact.html
- templates/suggestion.html
- templates/appreciation.html

### CSS
- about.css
- faq.css
- contact.css
- suggestion.css
- appreciation.css

### Responsibilities
- About page
- FAQ page
- Contact page
- Suggestion UI
- Appreciation UI
- Responsive styling

---

# Technologies Used

- Python
- Flask
- HTML5
- CSS3
- JavaScript
- MySQL
- Git
- GitHub

---

# Project Status

🚧 Currently Under Development