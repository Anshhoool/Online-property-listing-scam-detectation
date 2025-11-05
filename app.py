from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
DB_PATH = 'listings.db'

# ---------- DATABASE FUNCTIONS ----------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all_listings():
    conn = get_db_connection()
    listings = conn.execute('SELECT * FROM listings').fetchall()
    conn.close()
    return listings

def fetch_listing_by_id(listing_id):
    conn = get_db_connection()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone()
    conn.close()
    return listing

def add_listing(title, price, beds, baths, desc, img, email):
    conn = get_db_connection()
    conn.execute('INSERT INTO listings (title, price, beds, baths, description, image, contact_email) VALUES (?, ?, ?, ?, ?, ?, ?)',
                 (title, price, beds, baths, desc, img, email))
    conn.commit()
    conn.close()

# ---------- FLASK ROUTES ----------
@app.route('/')
def index():
    listings = fetch_all_listings()
    return render_template('index.html', listings=listings)

@app.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = fetch_listing_by_id(listing_id)
    if not listing:
        return "Listing not found", 404
    return render_template('listing.html', listing=listing)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        beds = request.form['beds']
        baths = request.form['baths']
        desc = request.form['description']
        email = f"honey-{title.lower().replace(' ', '')}@fake.ie"

        # ✅ Handle multiple image uploads
        image_files = request.files.getlist('images')
        saved_paths = []

        for image in image_files:
            if image and image.filename:
                filename = secure_filename(image.filename)
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                image.save(save_path)
                saved_paths.append('/' + save_path.replace('\\', '/'))

        image_gallery = ','.join(saved_paths)

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO listings (title, price, beds, baths, description, image, contact_email, image_gallery)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            title,
            price,
            beds,
            baths,
            desc,
            saved_paths[0] if saved_paths else '/static/images/default.jpg',
            email,
            image_gallery
        ))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('admin.html')


@app.route('/edit/<int:listing_id>', methods=['GET', 'POST'])
def edit_listing(listing_id):
    listing = fetch_listing_by_id(listing_id)
    if not listing:
        return "Listing not found", 404

    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        beds = request.form['beds']
        baths = request.form['baths']
        desc = request.form['description']

        # ✅ Handle image update
        image_files = request.files.getlist('images')
        saved_paths = []

        if image_files and any(img.filename for img in image_files):
            for image in image_files:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    save_path = os.path.join(UPLOAD_FOLDER, filename)
                    image.save(save_path)
                    saved_paths.append('/' + save_path.replace('\\', '/'))
            image_gallery = ','.join(saved_paths)
        else:
            image_gallery = listing['image_gallery']  # keep old gallery

        conn = get_db_connection()
        conn.execute('''
            UPDATE listings
            SET title = ?, price = ?, beds = ?, baths = ?, description = ?, image_gallery = ?
            WHERE id = ?
        ''', (title, price, beds, baths, desc, image_gallery, listing_id))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('edit.html', listing=listing)


@app.route('/delete/<int:listing_id>', methods=['POST'])
def delete_listing(listing_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


# ---------- MAIN ----------
if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print("⚠️ Database not found! Please run database_setup.py first.")
    app.run(debug=True, port=5050)



