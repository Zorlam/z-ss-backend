# Z'ss - E-Commerce Platform (Backend)

A robust e-commerce backend API built with Flask, featuring AI-powered product recommendations, comprehensive admin controls, and secure user authentication.

 **Live API:** https://z-ss-backend-1.onrender.com/api  
 **Frontend Demo:** https://zss-frontend.onrender.com  
 **Frontend Repo:** https://github.com/Zorlam/zss-frontend

---

## Features

### Core Functionality
-  **Shopping Cart System** - Add, update, remove items with real-time persistence
-  **AI-Powered Recommendations** - Personalized product suggestions based on browsing history
-  **User Authentication** - Secure JWT-based authentication and authorization
-  **Order Management** - Complete order processing and history tracking
-  **Wishlist** - Save products for later
-  **Advanced Search** - Product search with category filtering

### Admin Dashboard
-  **Product Management** - Create, edit, delete products
-  **Order Tracking** - View and manage customer orders
-  **User Management** - Admin user controls
-  **Image Upload** - Product image handling with validation

### Security & Performance
-  **JWT Authentication** - Secure token-based auth
-  **SQL Injection Protection** - SQLAlchemy ORM with parameterized queries
-  **Rate Limiting** - Protect against abuse
-  **Password Hashing** - Bcrypt encryption
-  **Input Validation** - Marshmallow schemas

---

## Tech Stack

**Framework:** Flask 3.0  
**Database:** PostgreSQL (production) / SQLite (development)  
**ORM:** SQLAlchemy 2.0  
**Authentication:** Flask-JWT-Extended  
**Validation:** Marshmallow  
**Security:** Flask-Bcrypt, Flask-Limiter  
**Deployment:** Render  

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - User login (returns JWT)
- `GET /api/auth/me` - Get current user profile

### Products
- `GET /api/products/` - List all products (supports pagination, search, filters)
- `GET /api/products/:id` - Get single product details
- `POST /api/products/` - Create product (admin only)
- `PUT /api/products/:id` - Update product (admin only)
- `DELETE /api/products/:id` - Delete product (admin only)
- `POST /api/products/upload-image` - Upload product image

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/` - Add item to cart
- `PUT /api/cart/:id` - Update cart item quantity
- `DELETE /api/cart/:id` - Remove item from cart
- `DELETE /api/cart/clear` - Clear entire cart

### Orders
- `GET /api/orders/` - Get user's order history
- `GET /api/orders/:id` - Get order details
- `POST /api/orders/` - Create new order from cart

### Wishlist
- `GET /api/wishlist/` - Get user's wishlist
- `POST /api/wishlist/` - Add product to wishlist
- `DELETE /api/wishlist/:id` - Remove from wishlist
- `GET /api/wishlist/check/:id` - Check if product is in wishlist

### Recommendations
- `GET /api/recommendations/ai` - Get personalized product recommendations
- `POST /api/recommendations/track/:id` - Track product view for recommendations

### Search
- `GET /api/search/suggestions` - Get search suggestions
- `GET /api/search/ai` - AI-powered product search

---

## Database Schema

### Users
- `id` (Primary Key)
- `username`, `email` (Unique)
- `password_hash`
- `is_admin` (Boolean)

### Products
- `id` (Primary Key)
- `name`, `description`
- `price`, `stock`
- `image_url`, `sku`
- `category_id` (Foreign Key)
- `is_active` (Boolean)
- `sizes`, `material`, `color`, `care_instructions`

### Categories
- `id` (Primary Key)
- `name`, `slug` (Unique)

### Cart Items
- `id` (Primary Key)
- `user_id`, `product_id` (Foreign Keys)
- `quantity`

### Orders
- `id` (Primary Key)
- `user_id` (Foreign Key)
- `status`, `total_price`
- `shipping_address`, `notes`
- `created_at`

### Order Items
- `id` (Primary Key)
- `order_id`, `product_id` (Foreign Keys)
- `quantity`, `price_at_time`

### Wishlist
- `id` (Primary Key)
- `user_id`, `product_id` (Foreign Keys)

### Browsing History
- `id` (Primary Key)
- `user_id`, `product_id` (Foreign Keys)
- `viewed_at` (Timestamp)

---

## Local Setup

### Prerequisites
- Python 3.9+
- PostgreSQL (optional - defaults to SQLite)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Zorlam/z-ss-backend.git
cd z-ss-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set environment variables**
```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost/dbname  # Or leave blank for SQLite
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

5. **Initialize database**
```bash
python init_db.py
```

6. **Run the application**
```bash
python run.py
```

API will be available at `http://127.0.0.1:5000/api`

### Default Admin Account
- **Email:** admin@clothingai.com
- **Password:** Admin123!

---

## Deployment

Deployed on **Render** with:
- PostgreSQL database
- Automatic deployments from `main` branch
- Environment variables configured in Render dashboard

---

## Project Structure
