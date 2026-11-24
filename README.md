# Acphix — Creative × Technology Studio

**Designing Innovation, Empowering Technology.**

Acphix Glass Edition (3.0): a responsive, interactive, database-backed agency website and client/admin portal with premium always-on glass animation, image-led portfolio, live-styled global presence, editable business metrics and a dedicated admin pricing manager. This project uses the uploaded Acphix brand assets and guidelines.

## Quick start

Requires **Python 3.10+**. No third-party packages, build tools or cloud account required.

```bash
cd acphix-studio-v3
python server.py init-admin
python server.py
```
**You can get experience now!**
Vercel Link:https://acphix-web.vercel.app/

Open **http://127.0.0.1:8080**. If port 8080 is occupied, change it:

```bash
ACPHIX_PORT=8767 python server.py
```

Admin and client users sign in through **Client login** at `/#/login`. The server does **not** create a default admin password. The `init-admin` command prompts for a secure one. A returning admin can reset their password by rerunning `init-admin` with the same email.

## Included sections

| Public page | Features |
|---|---|
| Home | Navy/gold immersive hero, pointer-responsive layered glass sculpture, animated metrics, portfolio and client-region map, seamless client-logo marquee, asymmetric cover-first portfolio bento, services, process and three-at-a-time testimonial carousel |
| About | Studio positioning, manifesto, values, method and client testimonial carousel |
| Services | Categories: Development, Creative, Growth, Intelligence; prices; filtering; project CTA |
| Portfolio | Asymmetric image-led project mosaic, category filtering, individual case studies with cover images and galleries, concept/client labels |
| Careers | Published vacancies and general talent interest form |
| Contact | Brief intake for every service; optional budget/company/contact details |
| User portal | Client sign-up and login, personal requests and statuses, personal notifications |
| Admin studio | Dedicated bulk Pricing manager, request review and notes, service/pricing CRUD, portfolio CRUD with covers, logo marks, case-study metadata, and gallery URLs or uploads, career listing CRUD, applications, CMS content (up to 10 testimonials and 20 client logos with uploads), verified statistics, client countries, social links, notifications |

## Admin workflow

Image uploads for testimonials, client logos, and portfolio covers/gallery accept JPG, PNG, or WebP files up to 10 MB each. Images are resized and compressed in the browser before saving.

1. Run `python server.py init-admin` and set your preferred admin email and password.
2. Sign in from `/#/login` to open the **Admin Studio**.
3. Under **Site content**, change contact details, Facebook/Instagram/TikTok/Behance URLs, homepage and about text, pricing notice and CTAs.
4. Under **Site content → Client testimonials**, click **Add testimonial** to add up to 10 approved recommendations. Choose ratings and visibility, and optionally upload client photos. Published cards appear three at a time in the Home and About carousels.
5. Under **Site content → Client logos**, click **Add logo** to add up to 20 client names and upload PNG, JPG or WebP logos. Saved logos loop continuously in a slow, draggable strip after the homepage map; hover to pause and reveal their full color. The marquee respects reduced-motion preferences and the admin ambient-motion setting.
6. Under **Pricing**, edit service *starting prices* in LKR and choose whether each price appears publicly. Click **Save all prices**. Prices remain available on service pages; the homepage investment guide has been replaced by testimonials.
7. Under **Portfolio**, replace the three generated, labelled concept examples with approved commissioned projects. Add a cover and optional centered logo mark; enter the year, industry/client, introduction, challenge, approach, and optional live project URL. Add up to eight gallery images using trusted HTTPS or local `/assets/...` URLs and/or image uploads. Each entry has its own editorial case-study page and can be published/unpublished individually.
8. Under **Requests**, review enquiries, change their status and leave notes. Permanently delete a request only after confirming; deletion also clears its linked notifications and cannot be undone. Admin notifications can be deleted individually. Logged-in clients see status changes and in-app notifications.
9. Under **Careers**, publish real openings when recruiting. Review incoming career enquiries under Applications.

## Important before a public launch

- **Rate-card-based starting prices:** selected default rates were mapped from the uploaded Acphix 2026 rate card; broader service names and package scope may differ. Review and approve all displayed figures before launch. Unpriced services show Custom quote.
- **Portfolio placeholders:** the three initial portfolio pieces are **clearly labelled concept projects**, not genuine Acphix client projects. Replace with approved work before official launch.
- **Social and contact information:** the contact email and phone numbers in the uploaded Acphix 2026 rate card are used as defaults. Official Facebook, Instagram, TikTok and Behance URLs were not supplied, so these remain blank until entered in Admin Studio.
- **Notifications:** included as **in-app/database notifications**, not email/SMS/push. Outbound notifications require integration with a transactional email or messaging service.
- **No payment processing:** the site displays starting-price guidance and captures quote requests; it does not charge clients online.
- **AI automation is offered as an agency service**, not a public AI content-generation tool.
- **Security:** the included server is a functional MVP. Before operating it as a public production website, deploy behind HTTPS, set secure cookies, add bot/spam protection and request throttling, configure backups, uptime monitoring and logging, undertake a security review, and consider a production web server/database architecture for scale. Do not expose the built-in HTTP server directly to the public internet.
- **Hosting and domain:** the project runs locally; it is **not deployed** to your business domain. Deployment, official URLs, mail integrations and production hardening are separate launch steps.

## Environment variables

| Variable | Default | Meaning |
|---|---|---|
| `ACPHIX_HOST` | `127.0.0.1` | Bind address; use `0.0.0.0` inside Docker or behind a reverse proxy |
| `ACPHIX_PORT` | `8080` | Server port |
| `ACPHIX_DB_PATH` | `<project>/data/acphix.sqlite3` | Persistent SQLite database path |
| `ACPHIX_PUBLIC_ORIGIN` | Empty | Canonical HTTPS origin used in CSRF origin checks, e.g. `https://acphix.lk` |
| `ACPHIX_SECURE_COOKIE` | `0` | Set `1` when serving via HTTPS |

Data is stored in SQLite under `data/`. It contains account identities, hashed passwords, sessions and client enquiries. Back it up securely and **never publish the database** or commit it to a public repository.

## Security implemented in this MVP

- Roles are enforced **server-side**; unprivileged users cannot call admin APIs.
- PBKDF2-SHA256 salted password hashing and cryptographically random session tokens.
- HttpOnly, SameSite session cookies; secure cookie option for HTTPS.
- CSRF request tokens and same-origin checks; request validation and parameterized SQL.
- User-specific project data and notifications; logged-in users cannot access one another's requests.
- Restricted file serving, response security headers and basic login-attempt throttling.

## Design system

Official Acphix palette: `#001751` navy · `#08409C` blue · `#2C2870` violet · `#FFC200` gold. Material Design 3-inspired 8px spacing, glass components and a SF Pro-compatible font stack. Motion includes ambient gradient orbs, a floating studio dock, pointer effects, responsive glass gadgets and on-view/on-hover counters. Reduced-motion preference and an admin ambient-motion on/off setting are supported. Portfolio features three newly generated, clearly labelled *concept* images; the user-supplied logo, favicon and OG preview remain.

## Example directory

```text
acphix-studio-v3/
  server.py                 Backend and SQLite schema / APIs
  public/
    index.html              Accessible application shell
    styles.css              Base responsive design system
    reference-v3.css       Screenshot-matched floating glass design layer
    assets/world-dots.svg  Geographically grounded dotted world map
    app.js                  SPA routing and interactions
    assets/                 Logos, favicon, share preview
  data/                     Runtime database (created on first run)
  Dockerfile                Optional container image
  docker-compose.yml        Optional local container setup
  ACPHIX_2_0_DESIGN_AND_DEVELOPMENT_BRIEF.md
  README.md
```

## Brand & copyright

Acphix name, logo, tagline and brand colors are based on the materials supplied for this project. The site is intended to be reviewed, customized and published by the Acphix team.

## Acphix 2.0 — pricing and trust metrics

On first launch, prices default to selected entries from **Acphix-Rate Card 2026.pdf**. To change any price without writing code:

1. Sign in as admin and open **Pricing** in the sidebar.
2. Enter the new `Starting price (LKR)` on any service row.
3. Check or uncheck **Show price** (custom quote fallback).
4. Click **Save all prices**. Public service prices update immediately.

The price controls are stored persistently in SQLite. The API is role-checked; only administrators can save. Prices set to `0` display **Custom quote** even when Show price is checked.

To update the public counters or client map, navigate to **Site content → Studio statistics & global presence**. Enter only verified numbers and client countries. The site intentionally uses `—` when clients/projects/countries have not yet been verified. The number of published creative capabilities is computed automatically. You may also change **Ambient animation** between *Active ambient motion* and *Static background*.

For the full page-by-page design, motion, copy, component checklist and implementation prompt, read **`ACPHIX_2_0_DESIGN_AND_DEVELOPMENT_BRIEF.md`**.


## Acphix Glass Edition — design changes

This upgrade follows the two supplied November 22, 2026 reference screenshots. It retains the existing application, roles and prices while adding:

- A rounded, fixed glass navigation capsule with a gold **Login** action.
- The original Acphix brand tagline as the default hero headline. Admins can replace the text under **Site content**.
- Three layered, translucent glass panes animated above the brand-colored orbs, with mouse-responsive 3D tilt, moving highlights and floating mini-widgets.
- Four metrics in a single rounded glass panel: Happy clients, Projects completed, Countries served and Client satisfaction. Numbers animate when they enter the viewport and replay when a visitor hovers. **Never enter illustrative statistics as real figures.**
- A dotted world silhouette with Sri Lanka HQ marked and other markers populated only from the verified country names entered by admin.
- A cohesive night-blue glass theme across Home, Services, Portfolio, About, Careers and Contact, with the existing admin and portal layouts deliberately kept functional.
- An always-visible compact **Request a service** control on desktop, reduced to a small accessible icon on mobile.
- Respect for `prefers-reduced-motion` and the existing admin **Ambient animation** setting.

### Manage the new metrics

Sign in as admin → **Site content** → **Studio statistics & global presence**. Set `Clients served`, `Projects completed`, `Countries reached`, `Client satisfaction (verified %)` and `Verified client countries`. Leave unknown values blank; the website displays an em dash instead of invented figures. The verified satisfaction field accepts 0–100; positive values display with `%`.

### Manage pricing

Sign in as admin → **Pricing**. Every rate has its own editable LKR amount and `Show price` / `Feature on home` controls. This update does not replace the selected 2026 rate-card starting prices.

### Tech stack

The project intentionally preserves the working dependency-free **Python 3.10+ / SQLite / modern HTML5 + CSS + vanilla JavaScript** application. No new framework was added because replacing the backend could break logins, notifications and pricing management. The UI uses Material-inspired spacing, CSS compositing, SVG map geometry and browser-native interaction APIs. This local preview requires no third-party installation.


## Version 3.1 update

This final package adds:

- Dark-mode-first public UI
- Minimal sun/moon switch for light mode
- Improved pricing-card contrast and visibility
- Additional UX review fixes and polishing
- PDF user manual included as `Acphix_3.1_User_Manual.pdf`


## Version 3.2 update

This revision keeps the dark mode unchanged and refines the optional light mode with:

- cleaner minimal white-shell layout
- better contrast and readability
- softer surfaces and card styling
- improved compatibility with the overall Acphix layout
- updated user manual included as `Acphix_3.2_User_Manual.pdf`
