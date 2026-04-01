# Project: Personalized Wedding E-Invite Engine
## Tech Stack: FastHTML, Neon (Postgres), Tailwind CSS, Animate.css, Lucide Icons

### 1. Visual Identity (Modern & Stylistic)
- **Aesthetic:** High-end digital stationery. Minimalist but with "Motion-First" design.
- **Color Palette:** - Background: `bg-[#FAFAF9]` (Soft Stone) or `bg-[#0A0A0A]` (Deep Onyx for Dark Mode).
    - Accents: `text-[#D4AF37]` (Champagne Gold) or `text-rose-500` (Modern Romantic).
- **Typography:**

    - Serif: 'Playfair Display' (Headlines & Personalized Quotes).
    - Sans: 'Inter' or 'Montserrat' (Logistical details and UI).
- **Animations:** - Use `Animate.css` for entry (e.g., `animate__fadeInUp`).
    - Use staggered delays (`animate__delay-1s`, `2s`) to create a "unfolding" story feel.
    - Implement a subtle "glow" or "shimmer" on the RSVP button.

### 2. Database & Data Layer (Neon)
- **Provider:** Neon Serverless Postgres.
- **Connection:** Use `psycopg` (v3) with `ConnectionPool` for serverless efficiency.
- **Schema:** - Table: `guests` (id, slug, name, phone, category, plus_one, rsvp_status, opened_at).
- **Querying:** Prioritize parameterized SQL for security. Use the `slug` as the unique identifier for the public URL.

### 3. Personalization Logic
- **The Magic Link:** `@rt("/invite/{slug}")`. 
- **Segmented Messaging:** Content must dynamically shift based on `guest.category` (e.g., Barkada, Family, VIP, Work).
- **Dynamic RSVP:** The RSVP form should be pre-filled with the guest's name based on the `slug`.

### 4. Admin Dashboard Architecture
- **Functionality:** - List all guests with "RSVP Status" and "Last Opened" timestamp.
    - **One-Click Send:** A button that generates a WhatsApp deep link (`wa.me`) with a pre-written, personalized message and the unique URL.
- **Processing:** Use **Polars** for any bulk guest list uploads/modifications.

### 5. Coding Standards (FastHTML)
- **Inline Tailwind:** Apply styles directly via `cls` attributes in Python.
- **Component-Based:** Break UI into reusable functions (e.g., `InviteCard`, `RSVPForm`, `AdminRow`).
- **HTMX Integration:** Use `hx-post` for RSVP submissions to ensure the page doesn't refresh, maintaining the smooth animation flow.

### 6. Personal Context Integration
- **Project Tamaraw Influence:** Reuse the spreadsheet-to-dashboard logic for managing guest lists.
- **Eagleice Influence:** Use the real-time tracking mindset to monitor "Invite Opens" via the Neon database.