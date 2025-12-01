# MVP (Minimum Viable Product)

**Goal:** Shareable, social, Strava-compliant. Friends can sign up and use it.

> "Sign up, connect Strava, get your cycling wisdom, train with friends."

---

## Success Criteria

- [ ] Anyone can register and connect their Strava
- [ ] Users receive AI-generated training plans
- [ ] Users can share plans and train with friends
- [ ] Shareable on social media (Strava, Instagram, etc.)
- [ ] Consistent, professional look across product and marketing

---

## Scope

### Pillar 1: AI-Generated Training Plans

| Feature | Description |
|---------|-------------|
| Weekly training plan | AI generates personalized plan based on ride history |
| Coaching insights | "You're improving...", "Consider recovery this week" |
| Plan adjustments | Regenerate or tweak plans based on feedback |

### Pillar 2: Community & Sharing

| Feature | Description |
|---------|-------------|
| Share training plan | Send plan link to friends |
| Group training plans | Create shared plans for multiple people |
| View friends' progress | See how friends are doing on shared plans |
| Social sharing | Export summary image for Strava/Instagram |

### Strava Integration

| Feature | Description |
|---------|-------------|
| Production API access | Apply for Strava approval (multi-user) |
| Background ride sync | Periodic or webhook-based activity sync |
| Full ride history | Access to historical activities |

### Analytics Dashboard

| Feature | Description |
|---------|-------------|
| Ride history | Full list of past activities |
| Weekly/monthly summaries | Visual progress over time |
| Training load | Simple volume/intensity tracking |

### Design System

| Feature | Description |
|---------|-------------|
| Brand guidelines | Colors, typography, logo usage |
| Component library | Reusable UI components (buttons, cards, forms) |
| Spacing & layout | Consistent grid and spacing rules |
| Icon set | Unified iconography |
| Marketing templates | Templates for social posts, blog headers, diagrams |
| Documentation styling | Consistent look for public-facing docs |

### Legal & Compliance

| Feature | Description |
|---------|-------------|
| Privacy policy | Required for Strava approval |
| Terms of service | User agreement |
| Data retention policy | How long ride data is stored |

### Infrastructure

| Feature | Description |
|---------|-------------|
| Monitoring | Error tracking (Sentry or similar) |
| Logging | Structured logs for debugging |
| Database migrations | Schema versioning for safe updates |
| CI/CD | Automated testing and deployment |

---

## Out of Scope (Deferred to v1.1+)

- Payments / Stripe integration
- Public user profiles
- Leaderboards
- Badges and streaks
- Dark mode
- Mobile app

---

## Strava Production Access

**Required before MVP launch.** Application process:

1. Working demo (POC is sufficient)
2. Privacy policy URL
3. Product description (1-2 pages)
4. Redirect URLs for OAuth
5. Data usage explanation

Typical approval time: 1-2 weeks.

---

## Technical Notes

- AI training plans can start rule-based, evolve to LLM-powered
- Group plans require shared state — consider plan ownership model
- Design system investment pays off for marketing velocity
- Social sharing images can be server-rendered (e.g., Satori, Puppeteer)
