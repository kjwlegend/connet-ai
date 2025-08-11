# Waitlist Setup Guide

## Overview
The waitlist functionality is now fully implemented using:
- **Frontend**: Next.js with TypeScript
- **Database**: Supabase (PostgreSQL)  
- **Email**: Resend.com
- **Architecture**: Direct frontend-to-database (no BFF required)

## Setup Instructions

### 1. Environment Configuration

Copy `.env.example` to `.env.local` and configure these required variables:

```bash
# Waitlist Configuration (Required)
RESEND_API_KEY="re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
NEXT_PUBLIC_SUPABASE_URL="https://your-project.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
NEXT_PUBLIC_APP_URL="http://localhost:3000"
```

### 2. Resend Setup

1. Visit [resend.com](https://resend.com)
2. Create account and verify domain (or use resend.dev for testing)
3. Generate API key from Dashboard → API Keys
4. Add key to `.env.local` as `RESEND_API_KEY`

### 3. Supabase Setup

1. Create project at [supabase.com](https://supabase.com)
2. Go to Settings → API to get URL and anon key
3. Run the database migration:

```sql
-- Execute in Supabase SQL Editor
-- Copy content from: supabase/migrations/001_create_waitlist_table.sql
```

### 4. Database Schema

The waitlist table includes:
- Email validation and uniqueness
- Position tracking (auto-increment)
- UTM/referral parameter capture
- Status management (pending/confirmed/unsubscribed)
- Referral system with unique codes
- Geographic and source tracking

### 5. API Endpoints

The following API routes are now available:

- `POST /api/waitlist/join` - Join waitlist
- `GET /api/waitlist/check/[email]` - Check if email exists
- `GET /api/waitlist/position/[email]` - Get position in line
- `GET /api/waitlist/stats` - Public statistics
- `POST /api/waitlist/referral` - Generate referral link
- `GET /api/waitlist/referral/[email]/stats` - Get referral stats
- `POST /api/waitlist/unsubscribe` - Unsubscribe from waitlist

### 6. Features

✅ **Email Collection & Validation**
✅ **Position Tracking** - Real-time queue position
✅ **Referral System** - Unique codes with bonus positions
✅ **Email Notifications** - Welcome emails with referral links
✅ **Analytics Tracking** - UTM parameters, source tracking
✅ **Unsubscribe Flow** - One-click unsubscribe with confirmation
✅ **Public Statistics** - Growth metrics and geographic data
✅ **Mobile Responsive** - Works on all devices
✅ **i18n Ready** - English/Chinese support

### 7. Testing

1. Start development server: `pnpm dev`
2. Visit homepage at `http://localhost:3000/homepage/version1`
3. Test email signup flow
4. Check Supabase dashboard for database entries
5. Verify welcome emails in Resend dashboard

### 8. Production Deployment

1. Set production environment variables
2. Update `NEXT_PUBLIC_APP_URL` to your domain
3. Configure custom domain in Resend for better deliverability
4. Run database migration in production Supabase
5. Test complete flow in production environment

## Email Templates

Welcome emails are HTML-formatted with:
- Modern responsive design
- Position display (#X in line)
- Referral link for sharing
- Unsubscribe link
- Brand-consistent styling

## Security

- Row Level Security (RLS) enabled on Supabase
- No direct table access for anonymous users
- Email validation on both client and server
- Rate limiting through Supabase built-ins
- Secure referral code generation

## Analytics Integration

The system includes hooks for:
- Google Analytics 4
- Facebook Pixel  
- PostHog
- Custom analytics platforms

## Next Steps

1. Set up your environment variables
2. Run the database migration
3. Test the complete flow
4. Deploy to production
5. Monitor email deliverability
6. Track growth metrics

For questions or issues, refer to the API route implementations in `src/app/api/waitlist/`.