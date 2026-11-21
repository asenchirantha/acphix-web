# Acphix Glass Edition — screenshot-matched visual upgrade (2026-11-22)

**Reference:** the two uploaded screenshots showing the rounded navigation, Acphix tagline hero, rotating layered glass cards, four-metric bar, and dotted map of client locations.

**Design contract:** preserve the prior website pages, forms, admin pricing controls, user authentication and content management. Upgrade public-page backgrounds to midnight-blue frosted glass with gold focal accents. Use the screenshots to guide visual rhythm; keep the content editable and never seed unverified client counts or countries.

**Interactions:** continuous ambient gradients; softly bobbing blue/violet/gold spheres; stacked glass panels with slow independent motion and cursor-responsive tilt; a subtle moving reflective sheen; context-specific floating UI widgets; counter animations on visibility and hover; hover spotlight on cards; map pins pulsing; hover zoom on actual portfolio concept images; reduced-motion and admin-off support.

**Admin content:** `stat_clients`, `stat_projects`, `stat_countries`, `stat_satisfaction`, and `client_regions` are editable. Rates remain editable via **Admin → Pricing** with visibility and featured toggles. The public map uses only verified regions and the logo remains unchanged.

**Files:** `public/reference-v3.css` is the non-destructive visual layer; `public/assets/world-dots.svg` is the generated dotted map; `public/app.js` has updated components and behavior; `server.py` includes safe default-copy and satisfaction-settings updates.

---

# ACPHIX 2.0 — Integrated Experience Brief

**Brand:** Acphix — Designing Innovation, Empowering Technology.  
**Location:** Sri Lanka, serving projects beyond its home market.  
**Design goal:** A premium, contemporary, futuristic digital studio that looks alive, stays easy to use, and allows the team to update real business information from the admin console.

## 1 — Visual direction and brand rules

Retain Acphix’s official palette: `#001751` (navy), `#08409C` (blue), `#2C2870` (violet), and `#FFC200` (gold). Use SF Pro when locally available, otherwise a system UI type stack. The interaction style combines softly frosted surfaces, ambient moving light, floating glass gadgets, high-contrast typography, and thoughtfully weighted gold highlights. Accent lighting remains restrained; avoid generic neon overload.

Use a Material Design 3-inspired rhythm, not an uncustomized Material UI skin. The spacing unit is **8 px** with common multiples of **16, 24, 32, 40**. Responsive layouts use grid-based cards, clear typography hierarchy, generous touch targets, consistent focus rings, contextual small labels, and surface-elevation cues. The public site’s motion must respect `prefers-reduced-motion` and the administrator’s site-wide motion toggle.

**Implementation choice:** The website retains its existing, tested dependency-free HTML/CSS/JavaScript frontend plus Python/SQLite backend. It has CSS design tokens and reusable JS rendering helpers rather than a high-maintenance, unnecessary full-stack rewrite. This preserves the working admin/client workflows. A future migration to React/Next.js and a larger managed database can be planned when hosting, integrations, and staffing justify it.

## 2 — Section-by-section public site

### Homepage hero

**Eyebrow:** INDEPENDENT CREATIVE & TECHNOLOGY STUDIO  
**Headline:** Make your next move impossible to ignore.  
**Description:** We build digital experiences, bold identities and smarter systems for ambitious brands. Strategy, creativity and technology, beautifully connected.  
**Primary action:** Start a project.  
**Secondary action:** Explore our work.

Retain the orbital geometric centerpiece and extend the scene with translucent UI chips, miniature signal bars, glass reflection and pointer-reactive depth. Use an always-active but gentle ambient gradient, grid, floating orbs, and cursor-following light. A stationary-page visitor should see life in the background without feeling distracted.

### Credibility metrics

Four interaction-ready metric tiles: **Clients served**, **Projects completed**, **Countries reached**, and **Creative capabilities**. Values come from admin-edited, verified figures; creative capabilities derives from the published service count. Missing client/project data displays a dash, never an invented number. The number rolls up when its tile enters the viewport and replays smoothly on hover. The reduced-motion mode displays final values without transitions.

### Services

Group the current services into Development, Creative, Growth and Intelligence. Keep the original service-copy structure and links to service enquiries. Apply a consistent three-column desktop / single-column mobile grid with a lightweight glass elevated treatment, animated border highlight, and stable icon sizing. Do not force all items into a public price list.

### Portfolio

Use an editorial, image-led grid: a wide featured case, a supporting paired case, and a panoramic third tile. Concept images must be explicitly labelled as concepts, not client commissions. Every tile links to its own detailed case study (overview, challenge, solution, year, discipline, tags and previous/next navigation). Let the admin provide a trusted HTTPS image URL or an existing local `/assets/` image path for future real work. Tiles feature subtle image zoom and glass actions on hover or focus.

### Global reach

**Headline:** Built in Sri Lanka. Made for everywhere.  
**Support copy:** Great ideas don't stop at borders. From our base in Sri Lanka, we collaborate through creativity, technology and imagination.

An illuminated world-map illustration indicates the studio’s Sri Lankan base. Client countries appear only when explicitly entered by the administrator as verified locations; the section otherwise states that the map is awaiting client-region data. No invented geographies or client numbers.

### Process

Discover → Define → Create → Evolve. Present as four premium glass panels against a dark high-contrast background. Each panel remains legible when animations are disabled.

### Pricing

The public homepage shows up to six **featured** pricing cards only. Default starting prices are sourced from the Acphix 2026 rate card. Each card is an indicative rate, not a final quotation. A service with a zero amount or disabled public-price flag displays **Custom quote**. Clients can start a request from every card.

### Footer and existing pages

Preserve Home, About, Services, Portfolio, Careers and Contact, plus client/admin login and request tracking. Use the contact details shown in the supplied Acphix 2026 rate card, with Facebook/Instagram/TikTok/Behance links controlled by admin settings; do not fabricate handles.

## 3 — Source-aligned starting prices (LKR)

These curated prices are initial defaults, editable in the admin panel:

| Website entry | Public starting price | Rate-card basis |
|---|---:|---|
| Websites & Web Applications | 100,000 | Web/mobile software development, page 4 |
| Graphic Design | 1,500 | Individual social creative, page 2 |
| Motion Graphics & Video | 2,500 | Short-form video, page 3 |
| Branding & Identity | 10,000 | Logo design/branding, pages 2 and 4 |
| Digital & Performance Marketing | 40,000 | Digital/social media marketing, page 4 |
| UI & UX Design | 40,000 | UI/UX full package, page 3 |
| Mobile App Development | 100,000 | Web/mobile software development, page 4 (not featured by default) |
| Social Media Management | 40,000 | Digital/social media marketing, page 4 (not featured by default) |
| Content Creation | Custom quote | Multiple content formats have different pricing |
| AI & Workflow Automation | Custom quote | Automation scope differs from the AI asset-generation services in the rate card |

These are suggested mappings to broader website service categories, not statements that the rate card lists all named offerings as separate bundles. Final quote varies with scope, deliverables, terms and revisions.

## 4 — Admin capabilities

The existing roles and workflows remain. A new **Pricing** tab introduces a bulk editor of all services. Fields are:

- Starting price in whole LKR; value cannot be negative.
- `Show price` flag: whether the numeric amount appears publicly.
- `Featured` flag: whether a service is included on the homepage pricing guide.

Click **Save all prices** to commit price changes in one validated transaction. For ordinary service editing, the service editor includes matching visibility and feature controls. Requests, portfolio, career listings, notifications, and existing content-management tools continue to operate. The API enforces admin-only authorization; no public endpoint allows changing price data.

In **Site content**, update the metrics, comma-separated verified client regions, studio base, contact details, social URLs and global ambient-animation setting. Never manufacture social proof: only publish verified numbers, actual client work, and real client countries.

## 5 — Component checklist and interaction spec

| Component | Behavior and visual language |
|---|---|
| Ambient field | Fixed behind the whole site, floating soft blue/violet/gold orbs, fine grid, three star points, pointer-following radial glow |
| Glass studio dock | A non-clickable miniature HUD element with a soft floating animation; suppressed in admin/client authentication views |
| Hero 3D orbit | Existing centerpiece retained, with transparent floating brand and signal widgets |
| Buttons | Gold primary CTA, navy alternatives, calm hover elevation and small moving sheen |
| Metric cards | Glass treatment, readable label and meaning, count on entry and hover, no fabricated values |
| Portfolio cards | Local concept covers or admin-provided images, proper cover crop, category and project classification, hover-to-explore pill |
| Global map | Dotted continent silhouette, HQ marker, optional verified country markers, explanatory labels |
| Service pricing | Six featured cards max; exact figure, selected visibility, custom-quote fallback, request link |
| Pricing admin | Inline LKR number inputs, show-price toggle, feature toggle, atomic save action |
| Motion controls | Browser reduced-motion preference + admin setting to turn ambient animation off |
| Responsive | 1440/1280 desktop, tablet, 390/375/320 mobile; no horizontal body overflow |

## 6 — Developer design prompt

> Continue the Acphix 2.0 digital studio without altering its brand palette, public navigation structure, request workflow, or role-based permissions. Keep the existing clean information architecture but elevate the frontend into a premium Material-structured glass experience. Use the Acphix navy/blue/violet/gold colors, SF Pro-compatible typography, 8px spacing system, soft glass panels, slow ambient floating elements, subtle cursor-depth effects, polished portfolio artwork, and accessible motion controls. Maintain clear contrast and avoid excessive neon, crowded backgrounds and gimmicky movement. Prioritize portfolio credibility, verified business metrics, client-country edits, and especially an admin-controlled service price catalogue. Price changes must be validated and saved on the server and immediately reflected in public-facing pages. Test desktop and mobile layouts and preserve reduced-motion accessibility. Treat all starter portfolio imagery as conceptual work and never invent customers or performance data.

## 7 — Test and launch guidance

This deliverable is a **locally runnable MVP**, not yet a hosted production release. The existing Python app handles authentication and database operations with role checks, CSRF protection and stored sessions. Before exposing it publicly, deploy behind HTTPS using a production web server, review privacy notices and content approval, add anti-spam and stronger request throttling, set up automated database backups, application monitoring, security review and validated off-site image hosting. For significant traffic, consider migrating the backend to a supported web framework and managed database while preserving this frontend design.
