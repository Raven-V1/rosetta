"""
Generate the Rosetta demo database — a comprehensive retail/e-commerce schema.
33 tables across 7 domains with realistic FK relationships and ~8,000+ rows.
Run once: python create_demo_db.py
Output: demo_data.db (committed to repo)
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta

DB_PATH = "demo_data.db"
random.seed(42)


def rdate(start="2020-01-01", end="2024-12-31"):
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    return (s + timedelta(days=random.randint(0, (e - s).days))).strftime("%Y-%m-%d")


def rdatetime(start="2020-01-01", end="2024-12-31"):
    return rdate(start, end) + f" {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}"


def create_schema(cur):
    cur.executescript("""
    PRAGMA foreign_keys = ON;

    -- ─── CUSTOMERS & ACCOUNTS ────────────────────────────────────────────────

    CREATE TABLE customer_segments (
        segment_id    INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        description   TEXT,
        discount_pct  REAL    NOT NULL DEFAULT 0
    );

    CREATE TABLE customers (
        customer_id   INTEGER PRIMARY KEY,
        first_name    TEXT    NOT NULL,
        last_name     TEXT    NOT NULL,
        email         TEXT    NOT NULL UNIQUE,
        phone         TEXT,
        date_of_birth TEXT,
        segment_id    INTEGER REFERENCES customer_segments(segment_id),
        is_active     INTEGER NOT NULL DEFAULT 1,
        created_at    TEXT    NOT NULL,
        updated_at    TEXT    NOT NULL
    );

    CREATE TABLE addresses (
        address_id    INTEGER PRIMARY KEY,
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        addr_type     TEXT    NOT NULL CHECK(addr_type IN ('billing','shipping')),
        street        TEXT    NOT NULL,
        city          TEXT    NOT NULL,
        state         TEXT    NOT NULL,
        zip           TEXT    NOT NULL,
        country       TEXT    NOT NULL DEFAULT 'US',
        is_default    INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE wishlist_items (
        wishlist_id   INTEGER PRIMARY KEY,
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        added_at      TEXT    NOT NULL
    );

    -- ─── STAFF ───────────────────────────────────────────────────────────────

    CREATE TABLE departments (
        department_id   INTEGER PRIMARY KEY,
        name            TEXT    NOT NULL UNIQUE,
        parent_dept_id  INTEGER REFERENCES departments(department_id),
        annual_budget   REAL
    );

    CREATE TABLE employees (
        employee_id   INTEGER PRIMARY KEY,
        first_name    TEXT    NOT NULL,
        last_name     TEXT    NOT NULL,
        email         TEXT    NOT NULL UNIQUE,
        department_id INTEGER REFERENCES departments(department_id),
        manager_id    INTEGER REFERENCES employees(employee_id),
        hire_date     TEXT    NOT NULL,
        salary        REAL    NOT NULL,
        is_active     INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE roles (
        role_id       INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        description   TEXT
    );

    CREATE TABLE employee_roles (
        employee_id   INTEGER NOT NULL REFERENCES employees(employee_id),
        role_id       INTEGER NOT NULL REFERENCES roles(role_id),
        assigned_at   TEXT    NOT NULL,
        PRIMARY KEY (employee_id, role_id)
    );

    -- ─── PRODUCT CATALOG ─────────────────────────────────────────────────────

    CREATE TABLE categories (
        category_id   INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        parent_id     INTEGER REFERENCES categories(category_id),
        description   TEXT
    );

    CREATE TABLE brands (
        brand_id      INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        country       TEXT,
        website       TEXT
    );

    CREATE TABLE products (
        product_id    INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL,
        sku           TEXT    NOT NULL UNIQUE,
        brand_id      INTEGER REFERENCES brands(brand_id),
        category_id   INTEGER REFERENCES categories(category_id),
        description   TEXT,
        base_price    REAL    NOT NULL,
        cost_price    REAL    NOT NULL,
        is_active     INTEGER NOT NULL DEFAULT 1,
        created_at    TEXT    NOT NULL
    );

    CREATE TABLE product_variants (
        variant_id    INTEGER PRIMARY KEY,
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        sku           TEXT    NOT NULL UNIQUE,
        color         TEXT,
        size          TEXT,
        weight_g      REAL,
        extra_price   REAL    NOT NULL DEFAULT 0
    );

    CREATE TABLE product_images (
        image_id      INTEGER PRIMARY KEY,
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        url           TEXT    NOT NULL,
        alt_text      TEXT,
        is_primary    INTEGER NOT NULL DEFAULT 0,
        sort_order    INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE product_attributes (
        attr_id       INTEGER PRIMARY KEY,
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        attr_name     TEXT    NOT NULL,
        attr_value    TEXT    NOT NULL
    );

    CREATE TABLE price_history (
        price_id      INTEGER PRIMARY KEY,
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        old_price     REAL    NOT NULL,
        new_price     REAL    NOT NULL,
        changed_at    TEXT    NOT NULL,
        changed_by    INTEGER REFERENCES employees(employee_id),
        reason        TEXT
    );

    CREATE TABLE tags (
        tag_id        INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        slug          TEXT    NOT NULL UNIQUE
    );

    CREATE TABLE product_tags (
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        tag_id        INTEGER NOT NULL REFERENCES tags(tag_id),
        PRIMARY KEY (product_id, tag_id)
    );

    -- ─── INVENTORY & SUPPLIERS ───────────────────────────────────────────────

    CREATE TABLE warehouses (
        warehouse_id  INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        city          TEXT    NOT NULL,
        state         TEXT    NOT NULL,
        country       TEXT    NOT NULL DEFAULT 'US',
        capacity      INTEGER
    );

    CREATE TABLE inventory (
        inventory_id  INTEGER PRIMARY KEY,
        variant_id    INTEGER NOT NULL REFERENCES product_variants(variant_id),
        warehouse_id  INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
        qty_on_hand   INTEGER NOT NULL DEFAULT 0,
        qty_reserved  INTEGER NOT NULL DEFAULT 0,
        reorder_point INTEGER NOT NULL DEFAULT 10,
        UNIQUE (variant_id, warehouse_id)
    );

    CREATE TABLE inventory_transactions (
        txn_id        INTEGER PRIMARY KEY,
        variant_id    INTEGER NOT NULL REFERENCES product_variants(variant_id),
        warehouse_id  INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
        txn_type      TEXT    NOT NULL CHECK(txn_type IN ('receipt','sale','adjustment','transfer','return')),
        qty           INTEGER NOT NULL,
        reason        TEXT,
        txn_date      TEXT    NOT NULL
    );

    CREATE TABLE suppliers (
        supplier_id   INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        contact_name  TEXT,
        email         TEXT,
        phone         TEXT,
        country       TEXT,
        lead_time_days INTEGER NOT NULL DEFAULT 7
    );

    CREATE TABLE supplier_products (
        supplier_id   INTEGER NOT NULL REFERENCES suppliers(supplier_id),
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        unit_cost     REAL    NOT NULL,
        min_order_qty INTEGER NOT NULL DEFAULT 1,
        PRIMARY KEY (supplier_id, product_id)
    );

    CREATE TABLE purchase_orders (
        po_id         INTEGER PRIMARY KEY,
        supplier_id   INTEGER NOT NULL REFERENCES suppliers(supplier_id),
        warehouse_id  INTEGER NOT NULL REFERENCES warehouses(warehouse_id),
        status        TEXT    NOT NULL CHECK(status IN ('draft','sent','confirmed','received','cancelled')),
        order_date    TEXT    NOT NULL,
        expected_date TEXT,
        total_amount  REAL    NOT NULL DEFAULT 0
    );

    CREATE TABLE purchase_order_items (
        po_item_id    INTEGER PRIMARY KEY,
        po_id         INTEGER NOT NULL REFERENCES purchase_orders(po_id),
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        qty_ordered   INTEGER NOT NULL,
        unit_cost     REAL    NOT NULL,
        qty_received  INTEGER NOT NULL DEFAULT 0
    );

    -- ─── ORDERS & PAYMENTS ───────────────────────────────────────────────────

    CREATE TABLE coupons (
        coupon_id     INTEGER PRIMARY KEY,
        code          TEXT    NOT NULL UNIQUE,
        coupon_type   TEXT    NOT NULL CHECK(coupon_type IN ('pct','fixed')),
        value         REAL    NOT NULL,
        min_order_amt REAL    NOT NULL DEFAULT 0,
        uses_limit    INTEGER,
        uses_count    INTEGER NOT NULL DEFAULT 0,
        expires_at    TEXT
    );

    CREATE TABLE orders (
        order_id         INTEGER PRIMARY KEY,
        customer_id      INTEGER NOT NULL REFERENCES customers(customer_id),
        status           TEXT    NOT NULL CHECK(status IN ('pending','confirmed','processing','shipped','delivered','cancelled','refunded')),
        order_date       TEXT    NOT NULL,
        shipping_addr_id INTEGER REFERENCES addresses(address_id),
        coupon_id        INTEGER REFERENCES coupons(coupon_id),
        subtotal         REAL    NOT NULL,
        discount_amt     REAL    NOT NULL DEFAULT 0,
        tax_amt          REAL    NOT NULL DEFAULT 0,
        shipping_cost    REAL    NOT NULL DEFAULT 0,
        total_amt        REAL    NOT NULL,
        notes            TEXT
    );

    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id      INTEGER NOT NULL REFERENCES orders(order_id),
        variant_id    INTEGER NOT NULL REFERENCES product_variants(variant_id),
        qty           INTEGER NOT NULL,
        unit_price    REAL    NOT NULL,
        discount_pct  REAL    NOT NULL DEFAULT 0
    );

    CREATE TABLE order_status_history (
        history_id    INTEGER PRIMARY KEY,
        order_id      INTEGER NOT NULL REFERENCES orders(order_id),
        old_status    TEXT,
        new_status    TEXT    NOT NULL,
        changed_at    TEXT    NOT NULL,
        changed_by    INTEGER REFERENCES employees(employee_id),
        note          TEXT
    );

    CREATE TABLE payment_methods (
        method_id     INTEGER PRIMARY KEY,
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        pmt_type      TEXT    NOT NULL CHECK(pmt_type IN ('credit_card','debit_card','paypal','bank_transfer')),
        last4         TEXT,
        expiry_month  INTEGER,
        expiry_year   INTEGER,
        is_default    INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE payments (
        payment_id    INTEGER PRIMARY KEY,
        order_id      INTEGER NOT NULL REFERENCES orders(order_id),
        method_id     INTEGER REFERENCES payment_methods(method_id),
        amount        REAL    NOT NULL,
        status        TEXT    NOT NULL CHECK(status IN ('pending','completed','failed','refunded')),
        processed_at  TEXT    NOT NULL,
        gateway_ref   TEXT
    );

    -- ─── SHIPPING ────────────────────────────────────────────────────────────

    CREATE TABLE carriers (
        carrier_id    INTEGER PRIMARY KEY,
        name          TEXT    NOT NULL UNIQUE,
        tracking_url  TEXT,
        avg_days      REAL
    );

    CREATE TABLE shipments (
        shipment_id   INTEGER PRIMARY KEY,
        order_id      INTEGER NOT NULL REFERENCES orders(order_id),
        carrier_id    INTEGER NOT NULL REFERENCES carriers(carrier_id),
        tracking_no   TEXT,
        shipped_at    TEXT,
        delivered_at  TEXT,
        status        TEXT    NOT NULL CHECK(status IN ('preparing','in_transit','out_for_delivery','delivered','exception'))
    );

    CREATE TABLE shipment_events (
        event_id      INTEGER PRIMARY KEY,
        shipment_id   INTEGER NOT NULL REFERENCES shipments(shipment_id),
        event_type    TEXT    NOT NULL,
        location      TEXT,
        event_time    TEXT    NOT NULL,
        description   TEXT
    );

    -- ─── REVIEWS & ENGAGEMENT ────────────────────────────────────────────────

    CREATE TABLE reviews (
        review_id     INTEGER PRIMARY KEY,
        product_id    INTEGER NOT NULL REFERENCES products(product_id),
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        rating        INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
        title         TEXT,
        body          TEXT,
        verified      INTEGER NOT NULL DEFAULT 0,
        created_at    TEXT    NOT NULL
    );

    CREATE TABLE review_votes (
        vote_id       INTEGER PRIMARY KEY,
        review_id     INTEGER NOT NULL REFERENCES reviews(review_id),
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        helpful       INTEGER NOT NULL CHECK(helpful IN (0,1)),
        voted_at      TEXT    NOT NULL,
        UNIQUE (review_id, customer_id)
    );

    -- ─── SYSTEM / AUDIT ──────────────────────────────────────────────────────

    CREATE TABLE audit_logs (
        log_id        INTEGER PRIMARY KEY,
        table_name    TEXT    NOT NULL,
        record_id     INTEGER NOT NULL,
        action        TEXT    NOT NULL CHECK(action IN ('INSERT','UPDATE','DELETE')),
        old_values    TEXT,
        new_values    TEXT,
        performed_by  INTEGER REFERENCES employees(employee_id),
        performed_at  TEXT    NOT NULL
    );

    CREATE TABLE notifications (
        notif_id      INTEGER PRIMARY KEY,
        customer_id   INTEGER NOT NULL REFERENCES customers(customer_id),
        notif_type    TEXT    NOT NULL CHECK(notif_type IN ('order_update','promotion','review_reply','restock')),
        title         TEXT    NOT NULL,
        message       TEXT    NOT NULL,
        read_at       TEXT,
        created_at    TEXT    NOT NULL
    );
    """)


def populate(cur):
    # ── customer_segments (5)
    segments = [
        (1, "Standard",  "Default tier",          0),
        (2, "Silver",    "100+ orders lifetime",  5),
        (3, "Gold",      "500+ orders lifetime",  10),
        (4, "Platinum",  "VIP high-value",        15),
        (5, "Wholesale", "Business buyers",       20),
    ]
    cur.executemany("INSERT INTO customer_segments VALUES (?,?,?,?)", segments)

    # ── departments (10)
    depts = [
        (1,  "Executive",       None, 2000000),
        (2,  "Engineering",     1,    1500000),
        (3,  "Product",         1,    800000),
        (4,  "Marketing",       1,    600000),
        (5,  "Sales",           1,    900000),
        (6,  "Customer Support",1,    400000),
        (7,  "Warehousing",     1,    700000),
        (8,  "Finance",         1,    500000),
        (9,  "HR",              1,    300000),
        (10, "IT",              2,    1200000),
    ]
    cur.executemany("INSERT INTO departments VALUES (?,?,?,?)", depts)

    # ── roles (6)
    roles = [
        (1, "admin",         "Full system access"),
        (2, "manager",       "Team management"),
        (3, "analyst",       "Read-only analytics"),
        (4, "support_agent", "Handle customer tickets"),
        (5, "warehouse_op",  "Inventory operations"),
        (6, "finance",       "Financial records"),
    ]
    cur.executemany("INSERT INTO roles VALUES (?,?,?)", roles)

    # ── employees (30)
    fnames = ["James","Maria","Robert","Patricia","John","Linda","Michael","Barbara",
              "William","Elizabeth","David","Susan","Richard","Jessica","Joseph","Sarah",
              "Thomas","Karen","Charles","Lisa","Daniel","Nancy","Matthew","Betty",
              "Anthony","Margaret","Mark","Sandra","Donald","Ashley"]
    lnames = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
              "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
              "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson","White",
              "Harris","Sanchez","Clark","Ramirez","Lewis","Robinson"]
    dept_map = {1:1,2:2,3:2,4:3,5:3,6:4,7:4,8:5,9:5,10:5,
                11:6,12:6,13:6,14:7,15:7,16:7,17:7,18:8,19:8,20:9,
                21:9,22:10,23:10,24:10,25:1,26:2,27:3,28:4,29:5,30:6}
    mgr_map = {1:None,2:1,3:1,4:1,5:1,6:1,7:1,8:1,9:1,10:1,
               11:6,12:6,13:6,14:7,15:7,16:7,17:7,18:8,19:8,20:9,
               21:9,22:2,23:2,24:2,25:1,26:2,27:3,28:4,29:5,30:6}
    salaries = [120000,95000,92000,88000,85000,80000,78000,75000,73000,110000,
                62000,60000,58000,68000,65000,63000,61000,90000,87000,70000,
                67000,105000,98000,96000,130000,93000,89000,82000,79000,64000]
    employees = []
    for i in range(1, 31):
        fn = fnames[i-1]; ln = lnames[i-1]
        employees.append((i, fn, ln, f"{fn.lower()}.{ln.lower()}@company.com",
                          dept_map[i], mgr_map[i], rdate("2015-01-01","2023-06-01"),
                          salaries[i-1], 1))
    cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?,?)", employees)

    # ── employee_roles
    emp_roles = []
    for eid in range(1, 31):
        r = 1 if eid == 1 else (2 if eid <= 10 else random.choice([3,4,5,6]))
        emp_roles.append((eid, r, rdate("2015-01-01","2023-01-01")))
    cur.executemany("INSERT INTO employee_roles VALUES (?,?,?)", emp_roles)

    # ── categories (20)
    categories = [
        (1,  "Electronics",    None, "Consumer electronics"),
        (2,  "Clothing",       None, "Apparel and fashion"),
        (3,  "Home & Garden",  None, "Home and garden supplies"),
        (4,  "Sports",         None, "Sporting goods"),
        (5,  "Books",          None, "Books and media"),
        (6,  "Toys",           None, "Toys and games"),
        (7,  "Automotive",     None, "Car parts and accessories"),
        (8,  "Food & Beverage",None, "Gourmet foods"),
        (9,  "Laptops",        1,    "Portable computers"),
        (10, "Smartphones",    1,    "Mobile phones"),
        (11, "Audio",          1,    "Headphones and speakers"),
        (12, "Cameras",        1,    "Cameras and photography"),
        (13, "Men's",          2,    "Men's clothing"),
        (14, "Women's",        2,    "Women's clothing"),
        (15, "Footwear",       2,    "Shoes and boots"),
        (16, "Furniture",      3,    "Indoor and outdoor furniture"),
        (17, "Fitness",        4,    "Fitness equipment"),
        (18, "Outdoor",        4,    "Outdoor and camping gear"),
        (19, "Action Figures", 6,    "Collectibles"),
        (20, "Board Games",    6,    "Family games"),
    ]
    cur.executemany("INSERT INTO categories VALUES (?,?,?,?)", categories)

    # ── brands (25)
    brands_data = [
        (1,"Apex Tech","US","https://apextech.com"),
        (2,"NovaSport","DE","https://novasport.de"),
        (3,"UrbanThread","US","https://urbanthread.com"),
        (4,"SkyGadget","CN","https://skygadget.cn"),
        (5,"GreenLeaf","CA","https://greenleaf.ca"),
        (6,"IronClad","US","https://ironclad.com"),
        (7,"PureSound","JP","https://puresound.jp"),
        (8,"VoltEdge","KR","https://voltedge.kr"),
        (9,"TerraPeak","AU","https://terrapeak.au"),
        (10,"LuxForm","IT","https://luxform.it"),
        (11,"DataCore","US","https://datacore.com"),
        (12,"EcoWear","NL","https://ecowear.nl"),
        (13,"SwiftRun","US","https://swiftrun.com"),
        (14,"ClearView","DE","https://clearview.de"),
        (15,"BoldMove","US","https://boldmove.com"),
        (16,"StellarHome","US","https://stellarhome.com"),
        (17,"PlayMaster","CN","https://playmaster.cn"),
        (18,"AutoPrime","US","https://autoprime.com"),
        (19,"NutriChoice","CA","https://nutrichoice.ca"),
        (20,"MegaByte","TW","https://megabyte.tw"),
        (21,"WildPath","US","https://wildpath.com"),
        (22,"SoftStitch","IN","https://softstitch.in"),
        (23,"ZenGarden","JP","https://zengarden.jp"),
        (24,"TurboGear","US","https://turbogear.com"),
        (25,"FreshBrew","BR","https://freshbrew.br"),
    ]
    cur.executemany("INSERT INTO brands VALUES (?,?,?,?)", brands_data)

    # ── products (120)
    product_names = [
        ("ProBook 15 Laptop","US-LPT-001",1,9,1299.99,780),
        ("ProBook 13 Laptop","US-LPT-002",1,9,999.99,600),
        ("AirBook Ultra","US-LPT-003",20,9,1599.99,960),
        ("BudgetBook 14","US-LPT-004",4,9,549.99,330),
        ("DevStation 17","US-LPT-005",11,9,1899.99,1140),
        ("X10 Smartphone","US-PHN-001",8,10,799.99,480),
        ("X10 Pro Smartphone","US-PHN-002",8,10,999.99,600),
        ("Z5 Smartphone","US-PHN-003",4,10,449.99,270),
        ("Pixel S Smartphone","US-PHN-004",1,10,699.99,420),
        ("Lumia 6","US-PHN-005",20,10,349.99,210),
        ("SoundWave Pro Headphones","US-AUD-001",7,11,299.99,120),
        ("SoundWave Lite Headphones","US-AUD-002",7,11,149.99,60),
        ("BassBoom Speaker","US-AUD-003",7,11,199.99,80),
        ("TrueEar Buds","US-AUD-004",8,11,129.99,52),
        ("StudioMix Headset","US-AUD-005",11,11,249.99,100),
        ("DSLR Pro 4K","US-CAM-001",14,12,1499.99,750),
        ("MirrorMax 50mm","US-CAM-002",14,12,899.99,450),
        ("ActionCam Xtreme","US-CAM-003",9,12,399.99,160),
        ("VlogCam Mini","US-CAM-004",4,12,249.99,100),
        ("Tripod Pro","US-CAM-005",14,12,89.99,36),
        ("TrailBlazer Jacket M","US-CLM-001",21,13,129.99,52),
        ("Classic Chino M","US-CLM-002",3,13,59.99,24),
        ("FlexFit Jogger M","US-CLM-003",13,13,49.99,20),
        ("Oxford Dress Shirt","US-CLM-004",3,13,69.99,28),
        ("Merino Sweater M","US-CLM-005",12,13,89.99,36),
        ("SummerDress W","US-CLW-001",22,14,79.99,32),
        ("YogaFlow Leggings","US-CLW-002",15,14,64.99,26),
        ("Wrap Blouse W","US-CLW-003",3,14,54.99,22),
        ("WinterCoat W","US-CLW-004",12,14,199.99,80),
        ("Floral Skirt","US-CLW-005",22,14,44.99,18),
        ("RunFast Sneakers M","US-FTW-001",13,15,109.99,44),
        ("TrailBoot M","US-FTW-002",6,15,149.99,60),
        ("CasualSlip W","US-FTW-003",13,15,79.99,32),
        ("HikePro Boot","US-FTW-004",21,15,179.99,72),
        ("Sandal Summer","US-FTW-005",10,15,39.99,16),
        ("ErgoDesk Standing","US-FUR-001",16,16,599.99,300),
        ("LuxChair Ergonomic","US-FUR-002",16,16,449.99,180),
        ("BedFrame Queen","US-FUR-003",16,16,699.99,280),
        ("NightstandSet","US-FUR-004",23,16,299.99,120),
        ("BookshelfWall 5-tier","US-FUR-005",16,16,249.99,100),
        ("TreadPro 3000 Treadmill","US-FIT-001",2,17,1299.99,520),
        ("PowerRack Home Gym","US-FIT-002",6,17,999.99,400),
        ("YogaMat Premium","US-FIT-003",15,17,49.99,20),
        ("Kettlebell Set 20kg","US-FIT-004",6,17,129.99,52),
        ("Resistance Bands Kit","US-FIT-005",15,17,34.99,14),
        ("4-Person Tent","US-OUT-001",9,18,249.99,100),
        ("SleepingBag -15C","US-OUT-002",21,18,149.99,60),
        ("HikerPack 65L","US-OUT-003",21,18,189.99,76),
        ("Headlamp Pro","US-OUT-004",9,18,49.99,20),
        ("CampStove Ultra","US-OUT-005",21,18,89.99,36),
        ("Python Programming Guide","US-BOK-001",5,5,49.99,10),
        ("Data Science Handbook","US-BOK-002",5,5,59.99,12),
        ("Leadership Mindset","US-BOK-003",5,5,29.99,6),
        ("SQL Mastery","US-BOK-004",5,5,44.99,9),
        ("Clean Code","US-BOK-005",5,5,39.99,8),
        ("HeroFigure Batman 12in","US-TOY-001",17,19,24.99,10),
        ("HeroFigure Iron Man 12in","US-TOY-002",17,19,24.99,10),
        ("MechBot Transformer","US-TOY-003",17,19,49.99,20),
        ("Catan Board Game","US-TOY-004",17,20,59.99,24),
        ("Chess Deluxe Set","US-TOY-005",17,20,79.99,32),
        ("Pandemic Board Game","US-TOY-006",17,20,49.99,20),
        ("OBD2 Scanner Pro","US-AUT-001",24,7,129.99,52),
        ("Car Dash Cam 4K","US-AUT-002",8,7,89.99,36),
        ("Seat Cover Set","US-AUT-003",18,7,79.99,32),
        ("Car Jump Starter","US-AUT-004",8,7,59.99,24),
        ("Tire Pressure Kit","US-AUT-005",24,7,29.99,12),
        ("Organic Coffee Blend","US-FDB-001",25,8,24.99,8),
        ("Green Tea Matcha 250g","US-FDB-002",19,8,19.99,6),
        ("Dark Chocolate 85% 12pk","US-FDB-003",19,8,29.99,9),
        ("Protein Powder Vanilla 2kg","US-FDB-004",19,8,54.99,22),
        ("Cold Brew Kit","US-FDB-005",25,8,34.99,14),
        ("USB-C Hub 7-Port","US-ELC-001",11,1,49.99,20),
        ("Wireless Charger 15W","US-ELC-002",8,1,29.99,12),
        ("Smart Plug 4-Pack","US-ELC-003",4,1,39.99,16),
        ("LED Desk Lamp","US-ELC-004",16,1,44.99,18),
        ("Mechanical Keyboard TKL","US-ELC-005",20,1,99.99,40),
        ("Gaming Mouse Pro","US-ELC-006",20,1,69.99,28),
        ("Monitor 27in 4K","US-ELC-007",1,1,449.99,180),
        ("Webcam 1080p","US-ELC-008",4,1,59.99,24),
        ("External SSD 1TB","US-ELC-009",20,1,109.99,44),
        ("Power Bank 20000mAh","US-ELC-010",8,1,49.99,20),
        ("SmartWatch Series 5","US-WTC-001",1,1,349.99,140),
        ("SmartWatch Sport","US-WTC-002",8,1,229.99,92),
        ("Fitness Tracker Band","US-WTC-003",15,1,79.99,32),
        ("Running Watch GPS","US-WTC-004",2,1,299.99,120),
        ("Kids SmartWatch","US-WTC-005",4,1,89.99,36),
        ("VR Headset Pro","US-VR-001",1,1,599.99,240),
        ("VR Controllers Pair","US-VR-002",1,1,129.99,52),
        ("Portable Projector","US-PRJ-001",4,1,299.99,120),
        ("Smart Home Hub","US-SHH-001",4,1,99.99,40),
        ("Smart Bulb 4-Pack","US-SHH-002",4,3,39.99,16),
        ("Robot Vacuum","US-RBT-001",4,3,399.99,160),
        ("Air Purifier HEPA","US-AIR-001",23,3,249.99,100),
        ("Electric Kettle 1.7L","US-KIT-001",5,3,49.99,20),
        ("Blender Pro 1000W","US-KIT-002",16,3,89.99,36),
        ("Drip Coffee Maker","US-KIT-003",25,3,69.99,28),
        ("Instant Pot 6qt","US-KIT-004",16,3,119.99,48),
        ("Cast Iron Skillet 12in","US-KIT-005",6,3,59.99,24),
        ("Knife Set 8-Piece","US-KIT-006",23,3,129.99,52),
        ("Cutting Board Bamboo","US-KIT-007",23,3,29.99,12),
        ("Storage Bins 6-Pack","US-ORG-001",5,3,44.99,18),
        ("Wall Organizer Shelf","US-ORG-002",16,3,79.99,32),
        ("Drawer Divider Set","US-ORG-003",5,3,24.99,10),
        ("Insulated Water Bottle","US-WTR-001",9,4,34.99,14),
        ("Hydration Pack 2L","US-WTR-002",21,4,49.99,20),
        ("Sports Towel Quick-Dry","US-SPT-001",2,4,24.99,10),
        ("Gym Gloves","US-SPT-002",6,4,19.99,8),
        ("Jump Rope Speed","US-SPT-003",15,4,14.99,6),
        ("Foam Roller 36in","US-SPT-004",15,4,39.99,16),
        ("Swimming Goggles","US-SPT-005",2,4,22.99,9),
        ("Soccer Ball Size 5","US-SPT-006",2,4,34.99,14),
        ("Basketball Outdoor","US-SPT-007",2,4,39.99,16),
        ("Tennis Racket Pro","US-SPT-008",2,4,89.99,36),
        ("Yoga Block Set","US-YGA-001",15,17,24.99,10),
        ("Meditation Cushion","US-YGA-002",23,17,44.99,18),
        ("Massage Gun Deep","US-RCV-001",2,4,149.99,60),
        ("Ice Bath Tub Portable","US-RCV-002",9,4,199.99,80),
        ("Compression Socks 3-Pack","US-RCV-003",12,4,29.99,12),
        ("First Aid Kit Pro","US-FAK-001",9,4,49.99,20),
        ("Sunscreen SPF 50 6pk","US-SKN-001",19,4,34.99,14),
    ]
    prod_rows = []
    for i, p in enumerate(product_names, 1):
        name, sku, brand_id, cat_id, price, cost = p
        prod_rows.append((i, name, sku, brand_id, cat_id,
                          f"High-quality {name.lower()} for everyday use.",
                          price, cost, 1, rdate("2020-01-01","2023-01-01")))
    cur.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?,?,?)", prod_rows)
    n_products = len(product_names)

    # ── product_variants (~300)
    colors = ["Black","White","Navy","Gray","Red","Blue","Green","Silver","Gold","Beige"]
    sizes  = ["XS","S","M","L","XL","XXL","One Size"]
    var_id = 1
    variants = []
    for pid in range(1, n_products + 1):
        cat_id = product_names[pid-1][3]
        for j in range(random.randint(2, 3)):
            color = random.choice(colors)
            size  = random.choice(sizes) if cat_id in (2,13,14,15,17) else "Standard"
            sku   = f"{product_names[pid-1][1]}-V{j+1:02d}"
            extra = round(random.choice([0,0,0,5,10,15,20]), 2)
            wt    = round(random.uniform(100, 5000), 1)
            variants.append((var_id, pid, sku, color, size, wt, extra))
            var_id += 1
    cur.executemany("INSERT INTO product_variants VALUES (?,?,?,?,?,?,?)", variants)
    total_variants = var_id - 1

    # ── product_images (~200)
    img_id = 1
    images = []
    for pid in range(1, n_products + 1):
        for j in range(random.randint(1, 2)):
            images.append((img_id, pid,
                           f"https://cdn.store.com/products/{pid}/img{j+1}.jpg",
                           f"Product {pid} image {j+1}",
                           1 if j == 0 else 0, j))
            img_id += 1
    cur.executemany("INSERT INTO product_images VALUES (?,?,?,?,?,?)", images)

    # ── product_attributes (~360)
    attr_templates = [
        ("Material",["Cotton","Polyester","Leather","Aluminum","Steel","Plastic","Wood","Rubber"]),
        ("Warranty",["1 year","2 years","6 months","Lifetime","No warranty"]),
        ("Origin",  ["USA","China","Germany","Japan","India","Taiwan","Mexico"]),
        ("Certif.", ["CE","FCC","RoHS","ISO 9001","None"]),
    ]
    attr_id = 1
    attrs = []
    for pid in range(1, n_products + 1):
        for aname, avals in random.sample(attr_templates, 3):
            attrs.append((attr_id, pid, aname, random.choice(avals)))
            attr_id += 1
    cur.executemany("INSERT INTO product_attributes VALUES (?,?,?,?)", attrs)

    # ── tags (30)
    tag_names = ["sale","new-arrival","bestseller","eco-friendly","premium","budget",
                 "limited-edition","clearance","bundle","gift-idea","top-rated",
                 "free-shipping","refurbished","handmade","organic","tech","outdoor",
                 "fitness","home-decor","fashion","gaming","audio","travel","wellness",
                 "professional","kids-friendly","sustainable","compact","wireless","smart"]
    cur.executemany("INSERT INTO tags VALUES (?,?,?)",
                    [(i+1, t, t) for i, t in enumerate(tag_names)])

    # ── product_tags (~360)
    pt_set = set()
    pt_rows = []
    for pid in range(1, n_products + 1):
        for tid in random.sample(range(1, 31), random.randint(2, 4)):
            if (pid, tid) not in pt_set:
                pt_set.add((pid, tid))
                pt_rows.append((pid, tid))
    cur.executemany("INSERT INTO product_tags VALUES (?,?)", pt_rows)

    # ── price_history (60)
    ph_rows = []
    for i in range(1, 61):
        pid   = random.randint(1, n_products)
        base  = product_names[pid-1][4]
        ph_rows.append((i, pid,
                        round(base * random.uniform(0.85, 1.15), 2),
                        round(base * random.uniform(0.85, 1.15), 2),
                        rdatetime("2021-01-01","2024-06-01"),
                        random.randint(1, 30),
                        random.choice(["seasonal promo","cost adjustment","competitor match",
                                       "clearance","price review"])))
    cur.executemany("INSERT INTO price_history VALUES (?,?,?,?,?,?,?)", ph_rows)

    # ── warehouses (6)
    warehouses = [
        (1,"Central Hub",   "Dallas",      "TX","US",50000),
        (2,"West Coast DC", "Los Angeles", "CA","US",35000),
        (3,"East Coast DC", "Newark",      "NJ","US",40000),
        (4,"Midwest Hub",   "Chicago",     "IL","US",30000),
        (5,"South Hub",     "Atlanta",     "GA","US",25000),
        (6,"Canada Hub",    "Toronto",     "ON","CA",20000),
    ]
    cur.executemany("INSERT INTO warehouses VALUES (?,?,?,?,?,?)", warehouses)

    # ── inventory (~600)
    inv_id = 1
    inv_rows = []
    inv_set = set()
    for vid in range(1, total_variants + 1):
        for wid in random.sample([1,2,3,4,5,6], random.randint(1, 2)):
            if (vid, wid) not in inv_set:
                inv_set.add((vid, wid))
                inv_rows.append((inv_id, vid, wid,
                                 random.randint(0, 500),
                                 random.randint(0, 50),
                                 random.randint(5, 30)))
                inv_id += 1
    cur.executemany("INSERT INTO inventory VALUES (?,?,?,?,?,?)", inv_rows)

    # ── inventory_transactions (400)
    inv_txns = []
    for i in range(1, 401):
        vid = random.randint(1, total_variants)
        wid = random.choice([1,2,3,4,5,6])
        t   = random.choice(["receipt","sale","adjustment","transfer","return"])
        qty = random.randint(1,100) if t == "receipt" else -random.randint(1,20)
        inv_txns.append((i, vid, wid, t, qty,
                         random.choice(["regular","return","damaged","audit",None]),
                         rdatetime("2021-01-01","2024-12-01")))
    cur.executemany("INSERT INTO inventory_transactions VALUES (?,?,?,?,?,?,?)", inv_txns)

    # ── suppliers (20)
    sup_names = ["GlobalTech Supply","Pacific Imports","Euro Parts Co","Asia Pacific Dist",
                 "NorthAm Wholesale","TechSource Direct","Prime Components","Allied Suppliers",
                 "Falcon Distribution","Vertex Manufacturing","Horizon Goods","BlueStar Logistics",
                 "RedRock Trading","OceanWave Imports","SkyHigh Supply","IronBridge Corp",
                 "SunValley Goods","ClearPath Dist","DeltaForce Supply","ProLink Trading"]
    countries = ["US","CN","DE","JP","KR","TW","IN","MX","CA","AU"]
    sup_rows = []
    for i, n in enumerate(sup_names, 1):
        sup_rows.append((i, n, f"Contact {i}",
                         f"contact{i}@supplier.com",
                         f"+1-555-{1000+i}",
                         random.choice(countries),
                         random.randint(3, 21)))
    cur.executemany("INSERT INTO suppliers VALUES (?,?,?,?,?,?,?)", sup_rows)

    # ── supplier_products (~80)
    sp_set = set()
    sp_rows = []
    for _ in range(80):
        sid = random.randint(1, 20)
        pid = random.randint(1, n_products)
        if (sid, pid) not in sp_set:
            sp_set.add((sid, pid))
            base_cost = product_names[pid-1][5]
            sp_rows.append((sid, pid, round(base_cost * random.uniform(0.8, 1.1), 2),
                            random.randint(5, 100)))
    cur.executemany("INSERT INTO supplier_products VALUES (?,?,?,?)", sp_rows)

    # ── purchase_orders (50)
    po_rows = []
    for i in range(1, 51):
        od = rdate("2022-01-01","2024-09-01")
        ed = (datetime.strptime(od, "%Y-%m-%d") + timedelta(days=random.randint(7,30))).strftime("%Y-%m-%d")
        po_rows.append((i, random.randint(1,20), random.randint(1,6),
                        random.choice(["draft","sent","confirmed","received","cancelled"]),
                        od, ed, round(random.uniform(500, 50000), 2)))
    cur.executemany("INSERT INTO purchase_orders VALUES (?,?,?,?,?,?,?)", po_rows)

    # ── purchase_order_items (120)
    poi_rows = []
    for i in range(1, 121):
        pid  = random.randint(1, n_products)
        cost = round(product_names[pid-1][5] * random.uniform(0.8, 1.0), 2)
        qty_o = random.randint(10, 200)
        poi_rows.append((i, random.randint(1,50), pid, qty_o, cost,
                         random.randint(0, qty_o)))
    cur.executemany("INSERT INTO purchase_order_items VALUES (?,?,?,?,?,?)", poi_rows)

    # ── customers (200)
    fn_pool = ["Emma","Liam","Olivia","Noah","Ava","Ethan","Sophia","Mason",
               "Isabella","William","Mia","James","Charlotte","Benjamin","Amelia",
               "Elijah","Harper","Lucas","Evelyn","Oliver","Abigail","Alexander",
               "Emily","Henry","Elizabeth","Sebastian","Mila","Jack","Ella","Owen",
               "Avery","Samuel","Sofia","Leo","Camila","Matthew","Aria","Ryan",
               "Scarlett","Nathan","Victoria","Daniel","Luna","Luke","Chloe","Andrew",
               "Penelope","Gabriel","Riley","Carter","Zoey","Isaiah","Nora","Michael",
               "Lily","Julian","Eleanor","Aaron","Hannah","Joshua","Lillian","Adam",
               "Aubrey","Charles","Addison","Thomas","Layla","Christopher","Ellie",
               "Jose","Stella","Hunter","Natalie","Austin","Zoe","Jonathan","Leah",
               "Wyatt","Hazel","Jordan","Violet","Brandon","Aurora","Angel","Savannah",
               "Kevin","Audrey","Isaiah","Brooklyn","Adrian","Bella","Robert","Claire",
               "Cameron","Skylar","Xavier","Lucy","Evan","Paisley","Ian","Everly"]
    ln_pool = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
               "Wilson","Anderson","Taylor","Thomas","Jackson","White","Harris","Martin",
               "Thompson","Young","Allen","King","Wright","Scott","Torres","Nguyen",
               "Hill","Flores","Green","Adams","Nelson","Baker","Hall","Rivera","Campbell",
               "Mitchell","Carter","Roberts","Walker","Cox","Phillips","Evans","Turner",
               "Parker","Collins","Edwards","Stewart","Morris","Murphy","Cook","Rogers",
               "Morgan","Peterson","Cooper","Reed","Bailey","Bell","Gomez","Kelly",
               "Howard","Ward","Diaz","Richardson","Wood","Watson","Brooks","Bennett",
               "Gray","James","Reyes","Cruz","Hughes","Price","Myers","Long","Foster",
               "Sanders","Ross","Morales","Powell","Sullivan","Russell","Ortiz","Jenkins",
               "Gutierrez","Perry","Butler","Barnes","Fisher","Henderson","Coleman",
               "Simmons","Patterson","Jordan","Reynolds","Hamilton","Graham","Kim",
               "Gonzalez","Alexander","Ramos","Lawson","Hanson"]
    domains = ["gmail","yahoo","outlook","icloud","hotmail"]
    cust_rows = []
    for i in range(1, 201):
        fn  = random.choice(fn_pool)
        ln  = random.choice(ln_pool)
        em  = f"{fn.lower()}{i}@{random.choice(domains)}.com"
        ph  = f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}"
        dob = rdate("1960-01-01","2002-12-31")
        seg = random.choices([1,2,3,4,5], weights=[50,25,12,8,5])[0]
        ca  = rdatetime("2019-01-01","2024-06-01")
        cust_rows.append((i, fn, ln, em, ph, dob, seg, 1, ca, ca))
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?)", cust_rows)

    # ── addresses (~320)
    streets = ["123 Main St","456 Oak Ave","789 Pine Rd","321 Elm Dr","654 Maple Ln",
               "987 Cedar Blvd","147 Birch Way","258 Willow Ct","369 Ash St","741 Poplar Ave"]
    city_states = [("New York","NY"),("Los Angeles","CA"),("Chicago","IL"),("Houston","TX"),
                   ("Phoenix","AZ"),("Philadelphia","PA"),("San Antonio","TX"),("San Diego","CA"),
                   ("Dallas","TX"),("San Jose","CA"),("Austin","TX"),("Jacksonville","FL"),
                   ("Seattle","WA"),("Denver","CO"),("Nashville","TN"),("Boston","MA"),
                   ("Portland","OR"),("Las Vegas","NV"),("Minneapolis","MN"),("Miami","FL")]
    addr_id = 1
    addr_rows = []
    for cid in range(1, 201):
        for j in range(random.randint(1, 2)):
            city, state = random.choice(city_states)
            addr_rows.append((addr_id, cid,
                              "billing" if j == 0 else "shipping",
                              random.choice(streets), city, state,
                              f"{random.randint(10000,99999)}", "US",
                              1 if j == 0 else 0))
            addr_id += 1
    cur.executemany("INSERT INTO addresses VALUES (?,?,?,?,?,?,?,?,?)", addr_rows)

    # ── coupons (25)
    coupon_rows = []
    for i in range(1, 26):
        ct  = random.choice(["pct","fixed"])
        val = round(random.choice([5,10,15,20,25,30,50]) if ct=="fixed"
                    else random.choice([5,10,15,20,25]), 2)
        coupon_rows.append((i, f"SAVE{i:03d}", ct, val,
                            round(random.choice([0,25,50,100]), 2),
                            random.choice([None,10,50,100,500]),
                            random.randint(0, 200),
                            rdate("2024-01-01","2025-12-31")))
    cur.executemany("INSERT INTO coupons VALUES (?,?,?,?,?,?,?,?)", coupon_rows)

    # ── payment_methods (~280)
    pm_types = ["credit_card","debit_card","paypal","bank_transfer"]
    pm_id = 1
    pm_rows = []
    for cid in range(1, 201):
        for j in range(random.randint(1, 2)):
            ptype = random.choice(pm_types)
            last4 = f"{random.randint(1000,9999)}" if ptype in ("credit_card","debit_card") else None
            pm_rows.append((pm_id, cid, ptype, last4,
                            random.randint(1,12), random.randint(2025,2030),
                            1 if j == 0 else 0))
            pm_id += 1
    cur.executemany("INSERT INTO payment_methods VALUES (?,?,?,?,?,?,?)", pm_rows)

    # ── orders (500)
    statuses = ["pending","confirmed","processing","shipped","delivered","cancelled","refunded"]
    order_rows = []
    for oid in range(1, 501):
        cid   = random.randint(1, 200)
        st    = random.choices(statuses, weights=[5,10,10,20,40,10,5])[0]
        od    = rdatetime("2021-01-01","2024-12-01")
        valid_addrs = [a[0] for a in addr_rows if a[1] == cid]
        sad   = random.choice(valid_addrs) if valid_addrs else None
        cpn   = random.choice([None]*8 + list(range(1,26)))
        sub   = round(random.uniform(20, 2500), 2)
        disc  = round(sub * random.choice([0,0,0,0.05,0.10,0.15]), 2)
        tax   = round((sub - disc) * 0.08, 2)
        ship  = round(random.choice([0,0,4.99,7.99,12.99,19.99]), 2)
        total = round(sub - disc + tax + ship, 2)
        order_rows.append((oid, cid, st, od, sad, cpn,
                           sub, disc, tax, ship, total,
                           random.choice([None,None,None,
                                          "Please leave at door",
                                          "Gift wrap requested",
                                          "Fragile items"])))
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", order_rows)

    # ── order_items (~1200)
    oi_id = 1
    oi_rows = []
    for oid in range(1, 501):
        used = set()
        for _ in range(random.randint(1, 4)):
            vid = random.randint(1, total_variants)
            if vid in used:
                continue
            used.add(vid)
            pid   = variants[vid-1][1]
            price = round(product_names[pid-1][4] + variants[vid-1][6], 2)
            oi_rows.append((oi_id, oid, vid, random.randint(1,5),
                            price, random.choice([0,0,0,5,10,15])))
            oi_id += 1
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?,?)", oi_rows)

    # ── order_status_history (~600)
    status_flow = {
        "pending":    ["confirmed","cancelled"],
        "confirmed":  ["processing","cancelled"],
        "processing": ["shipped"],
        "shipped":    ["delivered"],
        "delivered":  ["refunded"],
        "cancelled":  [],
        "refunded":   [],
    }
    osh_id = 1
    osh_rows = []
    for oid, order in enumerate(order_rows, 1):
        current = "pending"
        final   = order[2]
        ts      = order[3]
        while current != final:
            nexts = status_flow.get(current, [])
            if not nexts:
                break
            nxt = final if final in nexts else nexts[0]
            osh_rows.append((osh_id, oid, current, nxt, ts,
                             random.randint(1,30) if random.random() > 0.3 else None, None))
            osh_id += 1
            current = nxt
            ts = (datetime.strptime(ts[:10], "%Y-%m-%d") + timedelta(days=random.randint(1,3))).strftime("%Y-%m-%d %H:%M:%S")
    cur.executemany("INSERT INTO order_status_history VALUES (?,?,?,?,?,?,?)", osh_rows)

    # ── payments (500)
    pay_id = 1
    pay_rows = []
    for oid, order in enumerate(order_rows, 1):
        cid   = order[1]
        total = order[10]
        st    = order[2]
        valid_pm = [p[0] for p in pm_rows if p[1] == cid]
        mid = random.choice(valid_pm) if valid_pm else None
        pst = ("completed" if st in ("delivered","shipped","processing","confirmed")
               else "refunded" if st == "refunded"
               else "failed"   if st == "cancelled"
               else "pending")
        pay_rows.append((pay_id, oid, mid, total, pst, order[3], f"GW-{pay_id:08d}"))
        pay_id += 1
    cur.executemany("INSERT INTO payments VALUES (?,?,?,?,?,?,?)", pay_rows)

    # ── carriers (8)
    carriers = [
        (1,"FedEx",     "https://www.fedex.com/fedextrack/?trknbr={}",2.5),
        (2,"UPS",       "https://www.ups.com/track?tracknum={}",      3.0),
        (3,"USPS",      "https://tools.usps.com/go/TrackConfirmAction?qtc_tLabels1={}",4.0),
        (4,"DHL",       "https://www.dhl.com/en/express/tracking.html?AWB={}",5.0),
        (5,"Amazon Logistics","https://track.amazon.com/tracking/{}",1.5),
        (6,"OnTrac",    "https://www.ontrac.com/tracking/?number={}",2.0),
        (7,"LaserShip", "https://www.lasership.com/track/{}",         1.8),
        (8,"Freight Co","https://freight.co/track/{}",                7.0),
    ]
    cur.executemany("INSERT INTO carriers VALUES (?,?,?,?)", carriers)

    # ── shipments (~380)
    ship_id = 1
    ship_rows = []
    for oid, order in enumerate(order_rows, 1):
        if order[2] not in ("shipped","delivered"):
            continue
        od = order[3][:10]
        sa = (datetime.strptime(od, "%Y-%m-%d") + timedelta(days=random.randint(1,3))).strftime("%Y-%m-%d")
        da = ((datetime.strptime(sa, "%Y-%m-%d") + timedelta(days=random.randint(2,7))).strftime("%Y-%m-%d")
              if order[2] == "delivered" else None)
        st = "delivered" if order[2] == "delivered" else random.choice(["in_transit","out_for_delivery"])
        ship_rows.append((ship_id, oid, random.randint(1,8),
                          f"TRK{ship_id:010d}", sa, da, st))
        ship_id += 1
    cur.executemany("INSERT INTO shipments VALUES (?,?,?,?,?,?,?)", ship_rows)

    # ── shipment_events (~700)
    se_id = 1
    se_rows = []
    event_types = ["picked_up","in_transit","arrived_facility","out_for_delivery","delivered"]
    for shp in ship_rows:
        sid = shp[0]
        ts  = shp[4]
        loc = random.choice(city_states)
        for _ in range(random.randint(2, 5)):
            se_rows.append((se_id, sid, random.choice(event_types),
                            f"{loc[0]}, {loc[1]}",
                            f"{ts} {random.randint(6,22):02d}:{random.randint(0,59):02d}:00",
                            "Package status updated"))
            se_id += 1
            ts = (datetime.strptime(ts, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    cur.executemany("INSERT INTO shipment_events VALUES (?,?,?,?,?,?)", se_rows)

    # ── reviews (400)
    titles = ["Great product!","Exactly as described","Would buy again","Not what I expected",
              "Excellent quality","Fast shipping","Good value","Could be better",
              "Highly recommend","Average product","Outstanding!","Poor quality",
              "Perfect for my needs","Works as expected","Disappointed","Love it!"]
    bodies = [
        "This product exceeded my expectations. Very happy with the purchase.",
        "Good quality for the price. Would recommend to others.",
        "Arrived quickly and works perfectly.",
        "The product is okay but the packaging was damaged.",
        "Exactly what I needed. Great value for money.",
        "I've used this for a month and it's still working great.",
        "Not as durable as I hoped, but it does the job.",
        "Amazing product, my whole family loves it!",
        "The size was a bit off but overall good quality.",
        "Perfect gift! Arrived on time and looks great.",
    ]
    rev_rows = []
    used_rev = set()
    for i in range(1, 401):
        pid = random.randint(1, n_products)
        cid = random.randint(1, 200)
        if (pid, cid) in used_rev:
            pid = random.randint(1, n_products)
        used_rev.add((pid, cid))
        rev_rows.append((i, pid, cid,
                         random.choices([1,2,3,4,5], weights=[5,8,15,30,42])[0],
                         random.choice(titles), random.choice(bodies),
                         random.randint(0,1), rdatetime("2021-01-01","2024-12-01")))
    cur.executemany("INSERT INTO reviews VALUES (?,?,?,?,?,?,?,?)", rev_rows)

    # ── review_votes (300)
    rv_id = 1
    rv_rows = []
    rv_set = set()
    for _ in range(300):
        rid = random.randint(1, 400)
        cid = random.randint(1, 200)
        if (rid, cid) not in rv_set:
            rv_set.add((rid, cid))
            rv_rows.append((rv_id, rid, cid, random.randint(0,1),
                            rdatetime("2021-01-01","2024-12-01")))
            rv_id += 1
    cur.executemany("INSERT INTO review_votes VALUES (?,?,?,?,?)", rv_rows)

    # ── wishlist_items (200)
    wl_id = 1
    wl_set = set()
    wl_rows = []
    for _ in range(200):
        cid = random.randint(1, 200)
        pid = random.randint(1, n_products)
        if (cid, pid) not in wl_set:
            wl_set.add((cid, pid))
            wl_rows.append((wl_id, cid, pid, rdatetime("2022-01-01","2024-12-01")))
            wl_id += 1
    cur.executemany("INSERT INTO wishlist_items VALUES (?,?,?,?)", wl_rows)

    # ── audit_logs (150)
    al_tables = ["orders","products","customers","inventory","payments"]
    cur.executemany("INSERT INTO audit_logs VALUES (?,?,?,?,?,?,?,?)", [
        (i, random.choice(al_tables), random.randint(1,500),
         random.choice(["INSERT","UPDATE","DELETE"]),
         '{"status":"old"}', '{"status":"new"}',
         random.randint(1,30),
         rdatetime("2021-01-01","2024-12-01"))
        for i in range(1, 151)
    ])

    # ── notifications (300)
    ntypes = ["order_update","promotion","review_reply","restock"]
    cur.executemany("INSERT INTO notifications VALUES (?,?,?,?,?,?,?)", [
        (i, random.randint(1,200), random.choice(ntypes),
         f"Notification #{i}",
         f"Your notification is ready.",
         rdatetime("2022-01-01","2024-12-01") if random.random() > 0.4 else None,
         rdatetime("2021-01-01","2024-12-01"))
        for i in range(1, 301)
    ])


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("PRAGMA foreign_keys = OFF")

    print("Creating schema (33 tables)...")
    create_schema(cur)

    print("Populating data...")
    populate(cur)

    conn.commit()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [r[0] for r in cur.fetchall()]
    total_rows = 0
    print(f"\n{'Table':<35} {'Rows':>7}")
    print("-" * 43)
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        n = cur.fetchone()[0]
        total_rows += n
        print(f"  {t:<33} {n:>7,}")
    print("-" * 43)
    print(f"  {'TOTAL':<33} {total_rows:>7,}")
    print(f"\n{len(tables)} tables | {os.path.getsize(DB_PATH)/1024:.0f} KB")

    conn.close()


if __name__ == "__main__":
    main()
