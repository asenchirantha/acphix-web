#!/usr/bin/env python3
"""Acphix Studio — dependency-free Python/SQLite application server.
Local MVP. Run behind HTTPS reverse proxy with backups, monitoring and anti-spam
before production. No hard-coded admin account or external mail service.
"""
import argparse, base64, datetime, getpass, hashlib, hmac, http.cookies, json, mimetypes
import os, re, secrets, sqlite3, sys, time, uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
DB_PATH = Path(os.environ.get('ACPHIX_DB_PATH', str(ROOT / 'data' / 'acphix.sqlite3')))
MAX_BODY = 128 * 1024
HOST = os.environ.get('ACPHIX_HOST', '127.0.0.1')
PORT = int(os.environ.get('ACPHIX_PORT', '8080'))
SITE_ORIGIN = os.environ.get('ACPHIX_PUBLIC_ORIGIN', '').rstrip('/')
SECURE_COOKIE = os.environ.get('ACPHIX_SECURE_COOKIE', '0') == '1'

SERVICES = [
 ('web-development','Websites & Web Applications','Development','Fast, expressive sites and robust digital platforms built around your goals.','Responsive websites, dashboards, e-commerce and custom business systems.','browser',100000,1),
 ('mobile-apps','Mobile App Development','Development','Thoughtful mobile experiences that make everyday interactions effortless.','Product design, cross-platform app development and API integration.','smartphone',100000,2),
 ('graphic-design','Graphic Design','Creative','Distinctive visuals that turn a good message into a memorable one.','Social media creatives, print artwork, presentations and campaign assets.','pen-tool',1500,3),
 ('motion-graphics','Motion Graphics & Video','Creative','Stories with movement, energy and purpose.','Brand animations, launch videos, explainers and motion-led campaigns.','clapperboard',2500,4),
 ('brand-identity','Branding & Identity','Creative','A consistent visual and verbal world for your next chapter.','Logo systems, brand guidelines, art direction and brand refreshes.','sparkles',10000,5),
 ('digital-marketing','Digital & Performance Marketing','Growth','Creative strategy meets measurable campaigns.','Campaign strategy, paid media creatives, conversion improvement and reporting.','chart-no-axes-combined',40000,6),
 ('social-media','Social Media Management','Growth','A brand presence built for connection, not just impressions.','Channel strategy, content calendars, publishing support and community workflows.','users',40000,7),
 ('content-creation','Content Creation','Growth','Content with a clear point of view across formats.','Copywriting, photo/video concepts, campaign content and messaging.','video',0,8),
 ('ai-automation','AI & Workflow Automation','Intelligence','Less repetitive work. More room for your next big idea.','Practical automations, data workflows, assistants and system integrations.','workflow',0,9),
 ('ui-ux-design','UI & UX Design','Creative','Interfaces that feel effortless and make an impact.','User journeys, wireframes, prototypes, design systems and usability testing.','browser',40000,10),
]

PORTFOLIO = [
 ('nova-digital','NOVA / Digital Experience','Web & Software','A dynamic product-first website concept exploring bold navigation and seamless interaction.','From first impression to meaningful interaction, the experience was designed to feel unmistakably alive.','A distinctive digital presence for an evolving technology story.','A design system that combines a cinematic first impression with clear paths to action.','2026','Web design, UI/UX, Concept', 'electric'),
 ('form-and-feeling','FORM & FEELING','Brand Identity','An expressive identity concept, built from precision, contrast and human warmth.','A flexible visual system that moves with the brand.','Create a recognisable identity across physical and digital touchpoints.','A refined typographic language, confident palette and modular assets.','2026','Brand identity, Design system, Concept','rose'),
 ('signal-in-motion','SIGNAL / In Motion','Motion & Content','An editorial motion concept where purposeful movement gives every idea space to land.','Visual storytelling that rewards attention.','Bring a message to life without overwhelming the audience.','A motion language based on crisp transitions and a strong visual rhythm.','2026','Motion graphics, Content, Concept','amber'),
]

DEFAULT_SETTINGS = {
 'hero_eyebrow':'INDEPENDENT CREATIVE & TECHNOLOGY STUDIO',
 'hero_title':'Designing Innovation, Empowering Technology.',
 'hero_subtitle':'Acphix is a Sri Lankan studio for software, design and marketing. We build the products, brands and campaigns that move your business forward.',
 'about_title':'The magic happens between disciplines.',
 'about_body':'Acphix is a Sri Lanka-based creative and technology studio connecting imaginative design with thoughtful engineering. We help emerging and established brands shape what comes next, from their first visual identity to the products and campaigns people use every day.',
 'cta_title':'Have something ambitious in mind?',
 'cta_subtitle':'Tell us the beginning. We’ll help shape what comes next.',
 'contact_email':'acphix@gmail.com', 'phone':'072 207 0480', 'phone_secondary':'076 207 0480', 'location':'Sri Lanka · Working worldwide',
 'facebook':'', 'instagram':'', 'tiktok':'', 'behance':'',
 'pricing_notice':'Indicative starting prices in LKR. Final pricing is confirmed after a project brief and scope review.',
 'announcement':'Independent thinking. Connected execution.',
 'testimonial_1_name':'','testimonial_1_role':'','testimonial_1_message':'','testimonial_1_image':'','testimonial_1_rating':'5','testimonial_1_visible':'on',
 'testimonial_2_name':'','testimonial_2_role':'','testimonial_2_message':'','testimonial_2_image':'','testimonial_2_rating':'5','testimonial_2_visible':'on',
 'testimonial_3_name':'','testimonial_3_role':'','testimonial_3_message':'','testimonial_3_image':'','testimonial_3_rating':'5','testimonial_3_visible':'on',
 'stat_clients':'', 'stat_projects':'', 'stat_countries':'', 'stat_satisfaction':'', 'stat_years':'',
 'client_regions':'', 'studio_base':'Sri Lanka',
 'ambient_motion':'on',
}

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
def db():
 DB_PATH.parent.mkdir(parents=True, exist_ok=True)
 con=sqlite3.connect(str(DB_PATH), timeout=10)
 con.row_factory=sqlite3.Row
 con.execute('PRAGMA foreign_keys=ON')
 con.execute('PRAGMA journal_mode=WAL')
 return con

def init_db():
 with db() as c:
  c.executescript('''
  CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL UNIQUE,password_hash TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('admin','user')),created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,csrf TEXT NOT NULL,expires_at INTEGER NOT NULL);
  CREATE TABLE IF NOT EXISTS services (id TEXT PRIMARY KEY,slug TEXT NOT NULL UNIQUE,name TEXT NOT NULL,category TEXT NOT NULL,summary TEXT NOT NULL,description TEXT NOT NULL,icon TEXT NOT NULL,starting_price INTEGER NOT NULL DEFAULT 0,published INTEGER NOT NULL DEFAULT 1,sort_order INTEGER NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS portfolio (id TEXT PRIMARY KEY,slug TEXT NOT NULL UNIQUE,title TEXT NOT NULL,category TEXT NOT NULL,summary TEXT NOT NULL,description TEXT NOT NULL,challenge TEXT NOT NULL,solution TEXT NOT NULL,project_year TEXT NOT NULL,tags TEXT NOT NULL,visual TEXT NOT NULL,project_type TEXT NOT NULL DEFAULT 'concept',published INTEGER NOT NULL DEFAULT 1,sort_order INTEGER NOT NULL DEFAULT 0);
  CREATE TABLE IF NOT EXISTS site_settings (key TEXT PRIMARY KEY,value TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id) ON DELETE SET NULL,name TEXT NOT NULL,email TEXT NOT NULL,company TEXT NOT NULL,phone TEXT NOT NULL,service_id TEXT, budget TEXT NOT NULL,details TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'New',admin_note TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS notifications (id TEXT PRIMARY KEY,target_role TEXT NOT NULL,target_user TEXT,kind TEXT NOT NULL,title TEXT NOT NULL,message TEXT NOT NULL,related_id TEXT,created_at TEXT NOT NULL,read_at TEXT);
  CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY,title TEXT NOT NULL,type TEXT NOT NULL,location TEXT NOT NULL,description TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 0,created_at TEXT NOT NULL);
  CREATE TABLE IF NOT EXISTS applications (id TEXT PRIMARY KEY,user_id TEXT REFERENCES users(id) ON DELETE SET NULL,job_id TEXT,name TEXT NOT NULL,email TEXT NOT NULL,portfolio_url TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'New');
  CREATE TABLE IF NOT EXISTS login_attempts (ip TEXT NOT NULL,at INTEGER NOT NULL);
  CREATE INDEX IF NOT EXISTS idx_req_user ON requests(user_id);
  CREATE INDEX IF NOT EXISTS idx_notifications_role ON notifications(target_role,target_user,created_at);
  ''')
  # Non-destructive schema migrations; preserve prices and published user content.
  cols={r['name'] for r in c.execute('PRAGMA table_info(services)')}
  migrated='featured_price' not in cols
  if 'featured_price' not in cols:c.execute('ALTER TABLE services ADD COLUMN featured_price INTEGER NOT NULL DEFAULT 0')
  if 'price_visible' not in cols:c.execute('ALTER TABLE services ADD COLUMN price_visible INTEGER NOT NULL DEFAULT 1')
  portfolio_cols={r['name'] for r in c.execute('PRAGMA table_info(portfolio)')}
  if 'image_url' not in portfolio_cols:c.execute("ALTER TABLE portfolio ADD COLUMN image_url TEXT NOT NULL DEFAULT ''")
  if migrated:
   for slug in ('web-development','graphic-design','motion-graphics','brand-identity','digital-marketing','ui-ux-design'):
    c.execute('UPDATE services SET featured_price=1 WHERE slug=?',(slug,))
  c.execute("UPDATE site_settings SET value='Designing Innovation, Empowering Technology.' WHERE key='hero_title' AND value='Make your next move impossible to ignore.'")
  if c.execute('SELECT COUNT(*) FROM services').fetchone()[0]>0 and not c.execute("SELECT 1 FROM services WHERE slug='ui-ux-design'").fetchone():
   row=next((x for x in SERVICES if x[0]=='ui-ux-design'),None)
   if row:c.execute('INSERT INTO services (id,slug,name,category,summary,description,icon,starting_price,sort_order,featured_price) VALUES (?,?,?,?,?,?,?,?,?,1)',(str(uuid.uuid4()),)+row)
  if c.execute('SELECT COUNT(*) FROM services').fetchone()[0]==0:
   c.executemany('INSERT INTO services (id,slug,name,category,summary,description,icon,starting_price,sort_order) VALUES (?,?,?,?,?,?,?,?,?)',[(str(uuid.uuid4()),)+s for s in SERVICES])
  if migrated:
   for slug in ('web-development','graphic-design','motion-graphics','brand-identity','digital-marketing','ui-ux-design'):
    c.execute('UPDATE services SET featured_price=1 WHERE slug=?',(slug,))
  if c.execute('SELECT COUNT(*) FROM portfolio').fetchone()[0]==0:
   for i,p in enumerate(PORTFOLIO):
    c.execute('INSERT INTO portfolio (id,slug,title,category,summary,description,challenge,solution,project_year,tags,visual,sort_order) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),)+p+(i,))
  for k,v in DEFAULT_SETTINGS.items(): c.execute('INSERT OR IGNORE INTO site_settings (key,value) VALUES (?,?)',(k,v))

def hash_password(pwd):
 salt=secrets.token_bytes(16)
 k=hashlib.pbkdf2_hmac('sha256',pwd.encode(),salt,320_000)
 return 'pbkdf2_sha256$320000$'+base64.urlsafe_b64encode(salt).decode()+'$'+base64.urlsafe_b64encode(k).decode()
def verify_password(pwd,h):
 try:
  mode,rounds,salt,expected=h.split('$')
  if mode!='pbkdf2_sha256':return False
  got=hashlib.pbkdf2_hmac('sha256',pwd.encode(),base64.urlsafe_b64decode(salt),int(rounds))
  return hmac.compare_digest(got,base64.urlsafe_b64decode(expected))
 except Exception:return False

def create_admin(email=None):
 init_db()
 email=email or input('Admin email: ').strip().lower()
 name=input('Admin name: ').strip() or 'Acphix Admin'
 password=getpass.getpass('Admin password (12+ characters): ')
 if len(password)<12: raise SystemExit('Choose a password of 12+ characters')
 with db() as c:
  existing=c.execute('SELECT id FROM users WHERE email=?',(email,)).fetchone()
  if existing: c.execute('UPDATE users SET role=?,password_hash=? WHERE id=?',('admin',hash_password(password),existing['id']))
  else: c.execute('INSERT INTO users VALUES (?,?,?,?,?,?)',(str(uuid.uuid4()),name,email,hash_password(password),'admin',now()))
 print('Admin created. Sign in at /#/login')

def item(row):return dict(row)
def safe_slug(v):return re.sub('[^a-z0-9-]','',str(v).lower().strip().replace(' ','-'))[:90]
def clean_str(data,key,limit=500,required=False):
 s=str(data.get(key,'')).strip()
 if len(s)>limit or (required and not s):raise ValueError(f'{key} is invalid')
 return s

def notify(c,role,title,message,kind='general',related_id=None,target_user=None):
 c.execute('INSERT INTO notifications VALUES (?,?,?,?,?,?,?,?,?)',(str(uuid.uuid4()),role,target_user,kind,title,message,related_id,now(),None))

class Handler(BaseHTTPRequestHandler):
 server_version='Acphix/1.0'
 def log_message(self,fmt,*args): sys.stderr.write('%s %s\n'%(self.address_string(),fmt%args))
 def security_headers(self,typ='application/json; charset=utf-8'):
  self.send_header('Content-Type',typ)
  self.send_header('X-Content-Type-Options','nosniff')
  self.send_header('Referrer-Policy','strict-origin-when-cross-origin')
  self.send_header('X-Frame-Options','DENY')
  self.send_header('Permissions-Policy','camera=(), microphone=(), geolocation=()')
  self.send_header('Cache-Control','no-store' if typ.startswith('application/json') else 'public, max-age=900')
  self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: https:; script-src 'self'; style-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'")
  if SECURE_COOKIE:self.send_header('Strict-Transport-Security','max-age=31536000; includeSubDomains')
 def send_json(self,obj,status=200,cookie=None):
  # Commit mutations before the HTTP response is visible to the client.
  # This avoids a read-after-write race in concurrent requests.
  con=getattr(self,'_mut_con',None)
  if con is not None:
   if status>=400:con.rollback()
   else:con.commit()
   self._mut_con=None
  blob=json.dumps(obj,ensure_ascii=False).encode()
  self.send_response(status);self.security_headers();self.send_header('Content-Length',str(len(blob)))
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(blob)
 def error(self,msg,status=400):self.send_json({'error':msg},status)
 def read_json(self):
  try:l=int(self.headers.get('Content-Length','0'))
  except Exception:raise ValueError('Invalid content length')
  if l<1 or l>MAX_BODY:raise ValueError('Request size is invalid')
  try:
   v=json.loads(self.rfile.read(l));assert isinstance(v,dict)
   return v
  except Exception:raise ValueError('Invalid JSON')
 def session(self,c):
  cookie=http.cookies.SimpleCookie()
  try:cookie.load(self.headers.get('Cookie',''))
  except Exception:return None
  if 'acphix_session' not in cookie:return None
  token=cookie['acphix_session'].value
  if not token or len(token)>180:return None
  rec=c.execute('''SELECT u.id,u.name,u.email,u.role,s.csrf,s.expires_at,s.token_hash FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token_hash=?''',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
  if rec and rec['expires_at']>int(time.time()):return item(rec)
  return None
 def same_origin(self):
  origin=self.headers.get('Origin','')
  if origin:
   target=SITE_ORIGIN or ('https://' if SECURE_COOKIE else 'http://')+self.headers.get('Host','')
   return origin==target
  referer=self.headers.get('Referer','')
  return not referer or urlparse(referer).netloc==self.headers.get('Host','')
 def guard(self,session,role=None):
  if not session:self.error('Please sign in to continue.',401);return False
  if role and session['role']!=role:self.error('Access denied.',403);return False
  if self.headers.get('X-CSRF-Token')!=session['csrf']:
   self.error('Your session security token is missing. Refresh and try again.',403);return False
  return True
 def cookie_header(self,t='',max_age=604800):
  value=f'acphix_session={t}; Path=/; HttpOnly; SameSite=Lax; Max-Age={max_age}'
  if SECURE_COOKIE:value+='; Secure'
  return value
 def serve_file(self,path):
  target=PUBLIC/'index.html' if path=='/' else (PUBLIC/path.lstrip('/'))
  target=target.resolve()
  if not target.is_relative_to(PUBLIC.resolve()) or not target.is_file():return self.error('Not found',404)
  content=target.read_bytes();typ=mimetypes.guess_type(target)[0] or 'application/octet-stream'
  if typ.startswith('text/') or typ in ('application/javascript','application/json'):typ+='; charset=utf-8'
  self.send_response(200);self.security_headers(typ);self.send_header('Content-Length',str(len(content)));self.end_headers();self.wfile.write(content)
 def do_GET(self):
  path=urlparse(self.path).path
  if not path.startswith('/api/'):return self.serve_file(path)
  with db() as c:
   session=self.session(c)
   if path=='/api/bootstrap':
    s={r['key']:r['value'] for r in c.execute('SELECT * FROM site_settings')}
    services=[item(r) for r in c.execute('SELECT * FROM services WHERE published=1 ORDER BY sort_order,name')]
    works=[item(r) for r in c.execute('SELECT * FROM portfolio WHERE published=1 ORDER BY sort_order,title')]
    jobs=[item(r) for r in c.execute('SELECT * FROM jobs WHERE active=1 ORDER BY created_at DESC')]
    return self.send_json({'settings':s,'services':services,'portfolio':works,'jobs':jobs})
   if path=='/api/session':
    if not session:return self.send_json({'user':None})
    unread=c.execute('SELECT COUNT(*) FROM notifications WHERE (target_role=? OR target_user=?) AND read_at IS NULL',(session['role'],session['id'])).fetchone()[0]
    return self.send_json({'user':{k:session[k] for k in ('id','name','email','role')},'csrf':session['csrf'],'unread':unread})
   if path=='/api/portal':
    if not session:return self.error('Please sign in',401)
    q='SELECT * FROM requests WHERE user_id=? ORDER BY created_at DESC'
    requests=[item(r) for r in c.execute(q,(session['id'],))]
    notes=[item(r) for r in c.execute('SELECT * FROM notifications WHERE target_user=? OR target_role=? ORDER BY created_at DESC LIMIT 80',(session['id'],session['role']))]
    return self.send_json({'requests':requests,'notifications':notes})
   if path=='/api/admin/record':
    if not session or session['role']!='admin':return self.error('Access denied.',403)
    qs=parse_qs(urlparse(self.path).query)
    kind=(qs.get('kind') or [''])[0]
    rid=(qs.get('id') or [''])[0]
    if kind not in ('services','portfolio','jobs','requests','applications') or not rid:return self.error('Invalid record',400)
    row=c.execute('SELECT * FROM '+kind+' WHERE id=?',(rid,),).fetchone()
    if not row:return self.error('Record not found',404)
    return self.send_json({'record':item(row)})
   if path=='/api/admin':
    if not session or session['role']!='admin':return self.error('Access denied.',403)
    tables={}
    for name in ('services','portfolio','requests','jobs','applications'):
     tables[name]=[item(r) for r in c.execute('SELECT * FROM '+name+' ORDER BY rowid DESC LIMIT 300')]
    tables['settings']={r['key']:r['value'] for r in c.execute('SELECT * FROM site_settings')}
    tables['notifications']=[item(r) for r in c.execute('SELECT * FROM notifications WHERE target_role=? ORDER BY created_at DESC LIMIT 100',('admin',))]
    tables['users_count']=c.execute("SELECT COUNT(*) FROM users WHERE role='user'").fetchone()[0]
    return self.send_json(tables)
   return self.error('API route not found',404)
 def do_POST(self):self.handle_mutation('POST')
 def do_PATCH(self):self.handle_mutation('PATCH')
 def do_DELETE(self):self.handle_mutation('DELETE')
 def handle_mutation(self,method):
  path=urlparse(self.path).path
  if not path.startswith('/api/'):return self.error('Route not found',404)
  if not self.same_origin():return self.error('Invalid origin',403)
  try:
   body={} if method=='DELETE' else self.read_json()
   with db() as c:
    self._mut_con=c
    session=self.session(c)
    if path=='/api/register' and method=='POST':
     name=clean_str(body,'name',90,True)
     email=clean_str(body,'email',190,True).lower()
     pwd=clean_str(body,'password',200,True)
     if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise ValueError('Enter a valid email address.')
     if len(pwd)<10:raise ValueError('Password must be at least 10 characters.')
     if c.execute('SELECT 1 FROM users WHERE email=?',(email,)).fetchone():return self.error('An account already uses this email.',409)
     uid=str(uuid.uuid4());c.execute('INSERT INTO users VALUES (?,?,?,?,?,?)',(uid,name,email,hash_password(pwd),'user',now()))
     return self.login_finish(c,uid)
    if path=='/api/login' and method=='POST':
     email=clean_str(body,'email',190,True).lower();pwd=clean_str(body,'password',200,True)
     ip=self.client_address[0];recent=int(time.time())-3600
     c.execute('DELETE FROM login_attempts WHERE at<?',(recent,))
     failures=c.execute('SELECT COUNT(*) FROM login_attempts WHERE ip=?',(ip,)).fetchone()[0]
     if failures>=20:return self.error('Too many login attempts. Please try later.',429)
     person=c.execute('SELECT id,password_hash FROM users WHERE email=?',(email,)).fetchone()
     if not person or not verify_password(pwd,person['password_hash']):
      c.execute('INSERT INTO login_attempts VALUES (?,?)',(ip,int(time.time())))
      return self.error('Incorrect email or password.',401)
     c.execute('DELETE FROM login_attempts WHERE ip=?',(ip,))
     return self.login_finish(c,person['id'])
    if path=='/api/logout' and method=='POST':
     if not self.guard(session):return
     c.execute('DELETE FROM sessions WHERE token_hash=?',(session['token_hash'],))
     return self.send_json({'ok':True},cookie=self.cookie_header('',0))
    if path=='/api/request' and method=='POST':
     name=clean_str(body,'name',110,True);email=clean_str(body,'email',190,True).lower()
     company=clean_str(body,'company',130);phone=clean_str(body,'phone',45)
     service_id=clean_str(body,'service_id',80);budget=clean_str(body,'budget',80)
     details=clean_str(body,'details',6000,True)
     if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise ValueError('Enter a valid email address.')
     if len(details)<12:raise ValueError('Please describe your project in a little more detail.')
     if service_id and not c.execute('SELECT 1 FROM services WHERE id=? AND published=1',(service_id,)).fetchone():raise ValueError('Invalid service')
     rid=str(uuid.uuid4());dt=now()
     c.execute('INSERT INTO requests VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',(rid,session['id'] if session else None,name,email,company,phone,service_id,budget,details,'New','',dt,dt))
     notify(c,'admin','New project enquiry',f'{name} sent a new request.', 'request',rid)
     if session:notify(c,'user','Request received','Your enquiry reached Acphix. You can follow its status from your portal.','request',rid,session['id'])
     return self.send_json({'ok':True,'id':rid,'message':'Your request has been recorded. The Acphix team can review it from the admin dashboard.'},201)
    if path=='/api/apply' and method=='POST':
     name=clean_str(body,'name',110,True);email=clean_str(body,'email',190,True).lower()
     url=clean_str(body,'portfolio_url',500);message=clean_str(body,'message',3000,True)
     job_id=clean_str(body,'job_id',80)
     if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):raise ValueError('Invalid email')
     if url and not url.startswith(('https://','http://')):raise ValueError('Use a complete http(s) portfolio link')
     aid=str(uuid.uuid4());c.execute('INSERT INTO applications VALUES (?,?,?,?,?,?,?,?,?)',(aid,session['id'] if session else None,job_id,name,email,url,message,now(),'New'))
     notify(c,'admin','New career interest',f'{name} submitted a career enquiry.','career',aid)
     return self.send_json({'ok':True},201)
    if path=='/api/notifications/read' and method=='POST':
     if not self.guard(session):return
     nid=clean_str(body,'id',80,True)
     c.execute('UPDATE notifications SET read_at=? WHERE id=? AND (target_role=? OR target_user=?)',(now(),nid,session['role'],session['id']))
     return self.send_json({'ok':True})
    if path=='/api/admin' and method in ('POST','PATCH','DELETE'):
     if not self.guard(session,'admin'):return
     action=body.get('action','')
     if action=='read-notification':
      nid=clean_str(body,'id',80,True)
      c.execute('UPDATE notifications SET read_at=? WHERE id=? AND (target_role=? OR target_user=?)',(now(),nid,session['role'],session['id']))
      return self.send_json({'ok':True})
     if action=='entity':
      kind=body.pop('kind','');rid=body.pop('id','')
      if kind not in ('services','portfolio','jobs'):raise ValueError('Invalid entity')
      if method=='DELETE':
       if not rid:raise ValueError('Missing id')
       c.execute('DELETE FROM '+kind+' WHERE id=?',(rid,));return self.send_json({'ok':True})
      if method=='POST':return self.admin_save(c,kind,body,False)
      if method=='PATCH':return self.admin_save(c,kind,body,True)
     if action=='settings' and method=='PATCH':
      updates=body.get('settings')
      if not isinstance(updates,dict):raise ValueError('Invalid settings')
      for k,v in updates.items():
       limit=300000 if k.endswith('_image') else 4500
       if k not in DEFAULT_SETTINGS or not isinstance(v,str) or len(v)>limit:raise ValueError('Invalid setting '+str(k))
       if k.endswith('_visible') and v not in ('on','off'):raise ValueError('Testimonial visibility must be on or off')
       if k.endswith('_rating') and (not v.isdecimal() or not 1<=int(v)<=5):raise ValueError('Testimonial rating must be 1–5')
       if k.endswith('_image') and v:
        valid_asset=v.startswith('/assets/') and '..' not in v and not any(c.isspace() for c in v)
        valid_https=v.startswith('https://') and len(v)>9 and not any(c.isspace() for c in v)
        valid_upload=re.match(r'^data:image/(jpeg|png|webp);base64,[A-Za-z0-9+/=]+$',v) is not None
        if not (valid_asset or valid_https or valid_upload):raise ValueError('Use a trusted testimonial image URL or uploaded image')
       c.execute
      return self.send_json({'ok':True})
     if action=='prices' and method=='PATCH':
      updates=body.get('prices')
      if not isinstance(updates,list):raise ValueError('Invalid price updates')
      for row in updates:c.execute('UPDATE services SET starting_price=?,price_visible=?,featured_price=? WHERE id=?',(int(row['starting_price']),int(row['price_visible']),int(row['featured_price']),row['id']))
      return self.send_json({'ok':True,'count':len(updates)})
     if action=='request' and method=='PATCH':
      rid=clean_str(body,'id',80,True);status=clean_str(body,'status',40,True);note=clean_str(body,'admin_note',2000)
      if status not in ('New','Reviewing','Quoted','In Progress','Completed','Closed'):raise ValueError('Invalid status')
      record=c.execute('SELECT user_id,status FROM requests WHERE id=?',(rid,)).fetchone()
      if not record:return self.error('Request not found',404)
      c.execute('UPDATE requests SET status=?,admin_note=?,updated_at=? WHERE id=?',(status,note,now(),rid))
      if record['user_id'] and status!=record['status']:notify(c,'user','Your project request was updated',f'Your request is now {status}.','request',rid,record['user_id'])
      return self.send_json({'ok':True})
     if action=='application' and method=='PATCH':
      rid=clean_str(body,'id',80,True);status=clean_str(body,'status',40,True)
      if status not in ('New','Reviewed','Contacted','Archived'):raise ValueError('Invalid status')
      c.execute('UPDATE applications SET status=? WHERE id=?',(status,rid));return self.send_json({'ok':True})
     raise ValueError('Unknown admin action')
    if path.startswith('/api/admin/'):
     if not self.guard(session,'admin'):return
     route=path.removeprefix('/api/admin/')
     if route=='prices' and method=='PATCH':
      updates=body.get('prices')
      if not isinstance(updates,list) or len(updates)>150:raise ValueError('Invalid price updates')
      for row in updates:
       if not isinstance(row,dict):raise ValueError('Invalid price row')
       rid=row.get('id');amount=row.get('starting_price')
       if not isinstance(rid,str) or len(rid)>80:raise ValueError('Invalid service id')
       if isinstance(amount,bool) or not isinstance(amount,int) or not 0<=amount<=100000000:raise ValueError('Price must be a positive integer in LKR')
       if row.get('price_visible') not in (0,1) or row.get('featured_price') not in (0,1):raise ValueError('Invalid price visibility')
       cur=c.execute('UPDATE services SET starting_price=?,price_visible=?,featured_price=? WHERE id=?',
        (amount,int(row['price_visible']),int(row['featured_price']),rid))
       if cur.rowcount!=1:raise ValueError('Service no longer exists; refresh and try again')
      return self.send_json({'ok':True,'count':len(updates)})
     if route=='settings' and method=='PATCH':
      updates=body.get('settings')
      if not isinstance(updates,dict):raise ValueError('Invalid settings')
      allowed=set(DEFAULT_SETTINGS)
      for k,v in updates.items():
       limit=300000 if k.endswith('_image') else 4500
       if k not in allowed or not isinstance(v,str) or len(v)>limit:raise ValueError('Invalid setting '+str(k))
       if k in ('facebook','instagram','tiktok','behance') and v and not re.match(r'^https://[^\s]+$',v):raise ValueError('Social links must begin with https://')
       if k in ('stat_clients','stat_projects','stat_countries','stat_years','stat_satisfaction') and v and (not v.isdecimal() or int(v)>100000000):raise ValueError('Studio metrics must be non-negative whole numbers')
       if k=='ambient_motion' and v not in ('on','off'):raise ValueError('Animation setting must be on or off')
       if k=='stat_satisfaction' and v and int(v)>100:raise ValueError('Client satisfaction must be 1–100%')
       if k=='client_regions' and len(v)>1000:raise ValueError('Too many client regions')

       c.execute('INSERT INTO site_settings (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',(k,v))
      return self.send_json({'ok':True})
     if route in ('services','portfolio','jobs') and method=='POST':
      return self.admin_save(c,route,body,False)
     if route in ('services','portfolio','jobs') and method=='PATCH':
      return self.admin_save(c,route,body,True)
     if route in ('services','portfolio','jobs') and method=='DELETE':
      qs=parse_qs(urlparse(self.path).query);rid=(qs.get('id') or [''])[0]
      if not rid:return self.error('Missing id',400)
      c.execute('DELETE FROM '+route+' WHERE id=?',(rid,))
      return self.send_json({'ok':True})
     if route=='requests' and method=='PATCH':
      rid=clean_str(body,'id',80,True);status=clean_str(body,'status',40,True)
      note=clean_str(body,'admin_note',2000)
      if status not in ('New','Reviewing','Quoted','In Progress','Completed','Closed'):raise ValueError('Invalid status')
      record=c.execute('SELECT user_id,status FROM requests WHERE id=?',(rid,)).fetchone()
      if not record:return self.error('Request not found',404)
      c.execute('UPDATE requests SET status=?,admin_note=?,updated_at=? WHERE id=?',(status,note,now(),rid))
      if record['user_id'] and status!=record['status']:notify(c,'user','Your project request was updated',f'Your request is now {status}.','request',rid,record['user_id'])
      return self.send_json({'ok':True})
     if route=='applications' and method=='PATCH':
      rid=clean_str(body,'id',80,True);status=clean_str(body,'status',40,True)
      if status not in ('New','Reviewed','Contacted','Archived'):raise ValueError('Invalid status')
      c.execute('UPDATE applications SET status=? WHERE id=?',(status,rid))
      return self.send_json({'ok':True})
    return self.error('API route not found',404)
  except (ValueError,sqlite3.IntegrityError) as exc:return self.error(str(exc),400)
  except Exception as exc:
   self.log_error('API error: %s',str(exc))
   return self.error('Unexpected server error.',500)
 def login_finish(self,c,uid):
  token=secrets.token_urlsafe(48);csrf=secrets.token_urlsafe(30)
  user=c.execute('SELECT id,name,email,role FROM users WHERE id=?',(uid,)).fetchone()
  c.execute('INSERT INTO sessions VALUES (?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,csrf,int(time.time())+7*86400))
  return self.send_json({'ok':True,'user':item(user),'csrf':csrf},cookie=self.cookie_header(token))
 def admin_save(self,c,table,body,update):
  allowed={
   'services':{'slug':90,'name':140,'category':70,'summary':380,'description':1600,'icon':45,'starting_price':0,'price_visible':0,'featured_price':0,'published':0,'sort_order':0},
   'portfolio':{'slug':90,'title':160,'category':100,'summary':450,'description':1900,'challenge':1600,'solution':1600,'project_year':12,'tags':300,'visual':30,'image_url':750,'project_type':40,'published':0,'sort_order':0},
   'jobs':{'title':160,'type':90,'location':160,'description':4500,'active':0},
  }[table]
  vals={}
  for k,limit in allowed.items():
   v=body.get(k,0 if limit==0 else '')
   if limit==0:
    try:v=int(v)
    except Exception:raise ValueError(f'Invalid {k}')
    if abs(v)>100000000:raise ValueError(f'Invalid {k}')
   else:
    if not isinstance(v,str) or len(v)>limit:raise ValueError(f'Invalid {k}')
    v=v.strip()
   vals[k]=v
  if 'slug' in vals:vals['slug']=safe_slug(vals['slug'] or vals.get('name') or vals.get('title'))
  if table=='portfolio' and vals['project_type'] not in ('concept','client'):raise ValueError('Project type must be concept or client')
  if table=='services' and vals['starting_price']<0:raise ValueError('Price must be positive')
  if table=='services' and any(vals[k] not in (0,1) for k in ('price_visible','featured_price','published')):raise ValueError('Visibility must be on or off')
  if table=='portfolio' and vals.get('image_url'):
   url=vals['image_url']
   if not ((url.startswith('https://') and len(url)>9 and not any(c.isspace() for c in url)) or (url.startswith('/assets/') and '..' not in url and not any(c.isspace() for c in url))):
    raise ValueError('Portfolio image must be a trusted HTTPS URL or /assets/...')

  if update:
   rid=clean_str(body,'id',80,True)
   if not c.execute('SELECT 1 FROM '+table+' WHERE id=?',(rid,)).fetchone():return self.error('Record not found',404)
   sql='UPDATE '+table+' SET '+','.join(k+'=?' for k in vals)+' WHERE id=?'
   c.execute(sql,(*vals.values(),rid))
  else:
   rid=str(uuid.uuid4())
   if table=='jobs':vals['created_at']=now()
   sql='INSERT INTO '+table+' (id,'+','.join(vals)+') VALUES ('+','.join('?' for _ in range(len(vals)+1))+')'
   c.execute(sql,(rid,*vals.values()))
  return self.send_json({'ok':True,'id':rid})

if __name__=='__main__':
 ap=argparse.ArgumentParser()
 ap.add_argument('command',nargs='?',default='serve',choices=['serve','init-admin'])
 ap.add_argument('--email',default='')
 args=ap.parse_args()
 if args.command=='init-admin':create_admin(args.email)
 else:
  init_db();print(f'Acphix local application: http://{HOST}:{PORT}',flush=True)
  print('First time? Run: python server.py init-admin',flush=True)
  ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
