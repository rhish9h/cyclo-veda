# POC (Proof of Concept)

**Goal:** Localhost → Cloud. Secure, hosted, demo-able to family.

> "Look, it connects to Strava and shows my rides!"

---

## Success Criteria

- [ ] Hosted on cycloveda.com with HTTPS
- [ ] You can register and log in
- [ ] You can connect your Strava account
- [ ] You can see your recent rides
- [ ] Family can click around and see something real

---

## Scope

### Infrastructure

| Feature | Description |
|---------|-------------|
| Cloud hosting | Frontend + backend deployed (e.g., Vercel + Railway/Fly.io) |
| PostgreSQL database | Persistent storage for users, tokens, rides |
| Domain | cycloveda.com connected and working |
| Docker | Containerized backend for consistent deployment |

### Security

| Feature | Description |
|---------|-------------|
| HTTPS | SSL certificate via Let's Encrypt or Cloudflare |
| Rate limiting | Protect auth endpoints from brute force |
| Secrets management | All sensitive keys in environment variables, not code |
| No frontend secrets | Strava client secret stays server-side only |

### Authentication

| Feature | Description |
|---------|-------------|
| User registration | Email/password signup |
| User login | Session or JWT-based authentication |
| Token storage | Auth tokens stored securely in database |

### Strava Integration

| Feature | Description |
|---------|-------------|
| OAuth connect | Connect Strava account (dev mode, your account only) |
| OAuth disconnect | Ability to unlink Strava |
| Token storage | Store access + refresh tokens in database |
| Token refresh | Handle expired tokens automatically |
| Fetch activities | Pull recent rides from Strava API |

### Dashboard

| Feature | Description |
|---------|-------------|
| Ride list | Display last 5-10 rides (date, distance, time, avg speed) |
| Weekly summary | Simple "You rode X km this week" stat |

---

## Out of Scope (Deferred to MVP)

- Multi-user Strava (production API access)
- AI/training plan generation
- Community features
- Social sharing
- Admin panel
- Advanced analytics
- Mobile responsiveness polish

---

## Technical Notes

- Strava API in dev mode allows only 1 athlete (you)
- Token refresh is critical — Strava access tokens expire in 6 hours
- PostgreSQL enables real user management and avoids migration pain later
