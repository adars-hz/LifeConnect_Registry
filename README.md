# Life Connect Registry - Organ Donation Platform

A complete, professional, beginner-friendly Organ Donation Awareness & Management Website built with HTML, CSS, and JavaScript.

## 🎯 Project Overview

Life Connect Registry is a comprehensive organ donation platform that creates awareness about organ donation, allows donors and recipients to register, and provides a transparent verification system where users can track their request status and admins can manage and verify applications.

## ✨ Key Features

### 🏠 Home Page

- Hero section with emotional headline and CTAs
- Awareness section on organ donation impact
- Live statistics (Lives saved, Registered donors, Successful transplants)
- Step-by-step donation process
- Testimonials and inspirational quotes

### 📋 Registration System

- **Unique Registration ID System**: Auto-generated IDs (OD-DON-XXXXX, OD-REC-XXXXX)
- **Dual Registration**: Separate forms for donors and recipients
- **Document Upload**: Support for ID proofs, medical certificates, photos
- **Success Modal**: Displays unique ID after registration

### 🔐 Login System

- **Multiple Login Options**: Registration ID + Password OR Email + Password
- **User/Admin Login**: Separate interfaces for different user types
- **Forgot Password**: Email-based password reset

### 📊 User Dashboard

- **Profile Management**: View and edit personal information
- **Status Tracker**: Real-time application status (Pending, Approved, Rejected)
- **Organ Management**: View registered organs (donors) or required organ (recipients)
- **Messages**: System notifications and updates
- **Quick Actions**: Download certificates, update info, contact support

### 🛡️ Admin Dashboard

- **Statistics Overview**: Total donors, recipients, pending verifications
- **Verification Management**: Approve/reject applications with detailed views
- **Email Communication**: Direct email integration using mailto:
- **Activity Tracking**: Recent admin activities and system logs
- **Quick Actions**: Generate reports, manage hospitals, system settings

### 📞 Contact Page

- **Contact Form**: Subject-based inquiry system
- **Contact Information**: Complete office details, hours, emergency contacts
- **Map Integration**: Location display (placeholder for real implementation)
- **FAQ Preview**: Quick access to common questions

### ❓ FAQ Page

- **Accordion Interface**: Collapsible Q&A sections
- **Category Filtering**: Browse by topic (General, Registration, Medical, Legal)
- **Search Functionality**: Real-time FAQ search
- **Comprehensive Content**: 15+ detailed questions and answers

## 🎨 Design & Theme

- **Clean Modern UI**: Professional healthcare design
- **Color Palette**: Green & blue gradient theme
- **Responsive Design**: Mobile, tablet, desktop optimized
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation
- **Animations**: Smooth transitions and micro-interactions

## 🛠️ Technical Stack

### Frontend

- **HTML5**: Semantic markup, accessibility features
- **CSS3**: Modern styling, animations, responsive grid
- **JavaScript**: Vanilla JS, no frameworks required
- **Font Awesome**: Professional icons and graphics

### Backend Ready

- **Django Compatible**: Structured for Django integration
- **Database Ready**: MySQL/PostgreSQL compatible structure
- **Authentication**: Django auth system ready
- **File Upload**: Media handling prepared

## 📁 Project Structure

```
LifeConnect_Registry/
├── templates/           # HTML files
│   ├── index.html      # Home page
│   ├── about.html      # About organ donation
│   ├── register.html   # Registration forms
│   ├── login.html      # Login system
│   ├── user-dashboard.html  # User dashboard
│   ├── admin-dashboard.html # Admin interface
│   ├── contact.html    # Contact page
│   └── faq.html       # FAQ page
├── css/               # Stylesheets
│   └── style.css      # Complete styling
├── js/                # JavaScript files
│   └── script.js     # Interactive functionality
├── images/            # Image assets
└── README.md          # This file
```

## 🚀 Getting Started

### Prerequisites

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Local web server (optional but recommended)

### Installation

1. Clone or download the project
2. Navigate to the project directory
3. Open `templates/index.html` in your browser
4. Or use a local server:

   ```bash
   # Using Python
   python -m http.server 8000

   # Using Node.js
   npx serve .

   # Using PHP
   php -S localhost:8000
   ```

## 📱 Responsive Features

- **Mobile First**: Optimized for mobile devices
- **Touch Friendly**: Large tap targets, swipe gestures
- **Adaptive Layout**: Content reflows for different screen sizes
- **Performance**: Optimized images and CSS

## 🔧 Customization

### Colors

Edit the CSS variables in `css/style.css`:

```css
:root {
  --primary-green: #2ecc71;
  --primary-blue: #3498db;
  --accent-red: #e74c3c;
  --text-dark: #2c3e50;
  --text-light: #7f8c8d;
}
```

### Content

Update text content in HTML files:

- Company name and branding
- Contact information
- Statistics and numbers
- FAQ content

### Images

Replace placeholder images in `images/` folder:

- Logo and branding
- Hero section graphics
- Testimonial photos

## 🔐 Security Features

- **Input Validation**: Client-side form validation
- **XSS Prevention**: Sanitized user inputs
- **CSRF Ready**: Prepared for CSRF tokens
- **Secure Headers**: HTTPS ready structure

## 📊 Analytics Integration

Add tracking codes before `</head>` in HTML files:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_TRACKING_ID"></script>

<!-- Facebook Pixel -->
<script>
!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?...}
```

## 🌐 SEO Optimization

- **Meta Tags**: Complete SEO meta information
- **Structured Data**: Schema.org markup ready
- **Sitemap**: XML sitemap structure prepared
- **Open Graph**: Social media sharing ready

## 📧 Email Integration

The system includes email functionality using `mailto:`:

- Contact form submissions
- Admin-to-user communications
- Password reset emails
- Registration confirmations

## 🔄 Future Enhancements

### Backend Integration

- Django models and views
- Database schema implementation
- User authentication system
- File upload handling

### Advanced Features

- Real-time notifications
- Video consultation system
- Mobile app integration
- AI-powered matching algorithm

### Third-party Integrations

- Payment processing
- Hospital API integration
- SMS notifications
- Video conferencing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:

- **Email**: info@lifeconnect.org
- **Phone**: +1 234 567 8900
- **Website**: www.lifeconnect.org

## 🙏 Acknowledgments

- Font Awesome for icons
- Google Fonts for typography
- Modern CSS techniques and best practices
- Healthcare industry guidelines and standards

---

**Life Connect Registry** - Connecting Lives Through Organ Donation ❤️

_Built with passion for saving lives and making organ donation accessible to everyone._
