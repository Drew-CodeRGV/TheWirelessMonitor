# LinkedIn API Setup Guide - Complete Walkthrough

## Overview

Getting LinkedIn API access is more complex than X/Twitter. LinkedIn has strict requirements and a verification process. This guide walks you through the entire process.

## Important Notes Before You Start

⚠️ **LinkedIn API Access Requirements**:
- Must have a LinkedIn company page (personal profiles alone won't work)
- App must be associated with a verified company
- Need to apply for specific API products
- Approval process can take several days to weeks
- Some features require additional verification

⚠️ **API Limitations**:
- Free tier is very limited
- Most useful features require paid LinkedIn Marketing Developer Platform
- Rate limits are strict
- Cannot access personal feed without special permissions

## Step-by-Step Guide

### Step 1: Create a LinkedIn Company Page (If You Don't Have One)

1. Go to https://www.linkedin.com/company/setup/new/
2. Select company type (most choose "Company")
3. Fill in company details:
   - Company name
   - LinkedIn public URL
   - Website
   - Industry
   - Company size
   - Company type
4. Add company logo (required)
5. Click "Create page"

**Note**: You need to be a company page admin to create apps.

### Step 2: Access LinkedIn Developers Portal

1. Go to https://www.linkedin.com/developers/
2. Click "Create app" button (top right)
3. Sign in with your LinkedIn account if prompted

### Step 3: Create Your Application

Fill in the application form:

**App name**: 
- Example: "Wireless Monitor Dashboard"
- Must be unique

**LinkedIn Page**: 
- Select your company page from dropdown
- If you don't see your page, you're not an admin

**Privacy policy URL**:
- Required field
- Can use a simple page on your website
- Example: `https://yoursite.com/privacy`
- For development, you can use a placeholder

**App logo**:
- Upload a logo (required)
- Minimum 100x100 pixels
- Square format recommended

**Legal agreement**:
- Check the box to agree to LinkedIn API Terms of Use
- Click "Create app"

### Step 4: Get Your Credentials

After creating the app, you'll see the "Auth" tab:

1. Click on **"Auth"** tab
2. You'll see:
   - **Client ID**: Copy this
   - **Client Secret**: Click "Show" then copy
   - **Redirect URLs**: Add your callback URL

**Important**: Save these credentials securely!

```
Client ID: 86xxxxxxxxxx
Client Secret: aBcDeFgHiJkLmNoP
```

### Step 5: Configure OAuth 2.0 Settings

Still in the "Auth" tab:

1. **Redirect URLs**:
   - Add: `http://localhost:8080/auth/linkedin/callback`
   - For production: `https://yourdomain.com/auth/linkedin/callback`
   - Click "Add redirect URL"
   - Click "Update"

2. **OAuth 2.0 scopes**:
   - These determine what your app can access
   - Default scopes are very limited

### Step 6: Request API Products

This is the crucial step. LinkedIn requires you to apply for specific API products:

1. Go to **"Products"** tab
2. You'll see available products:

**Available Products** (as of 2026):

**Sign In with LinkedIn using OpenID Connect** (Usually auto-approved):
- Basic profile access
- Email address
- Good for authentication only

**Share on LinkedIn** (Usually auto-approved):
- Post content to LinkedIn
- Share articles
- Limited to posting only

**Marketing Developer Platform** (Requires application):
- Access to company pages
- Post analytics
- Advertising API
- **This is what you need for monitoring posts**

**Compliance API** (Enterprise only):
- For large organizations
- Requires special approval

3. Click **"Request access"** on the products you need
4. Fill out the application form:
   - Describe your use case
   - Explain how you'll use the API
   - Provide screenshots if possible
   - Be specific and professional

**Example Application Text**:
```
We are building a wireless technology news monitoring dashboard that 
aggregates content from multiple sources including LinkedIn. We need 
access to the Marketing Developer Platform to:

1. Monitor posts from our company page
2. Track engagement metrics on shared articles
3. Analyze which wireless technology topics resonate with our audience
4. Schedule and publish relevant industry news to our followers

Our application will help us better understand our audience and share 
more relevant wireless technology content.
```

### Step 7: Wait for Approval

- **Sign In with LinkedIn**: Usually instant
- **Share on LinkedIn**: Usually instant or within 24 hours
- **Marketing Developer Platform**: 1-4 weeks
- You'll receive email notifications about approval status

### Step 8: Verify Your Application

Once approved, verify your setup:

1. Go back to **"Auth"** tab
2. Check that your products show "Approved" status
3. Review your available OAuth scopes
4. Test the OAuth flow

### Step 9: Add Credentials to Your Application

Once you have Client ID and Client Secret:

1. Open your `.env` file
2. Add LinkedIn credentials:

```env
# LinkedIn API Credentials
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_REDIRECT_URI=http://localhost:8080/auth/linkedin/callback
```

3. Save the file
4. Restart your application

## OAuth 2.0 Flow for LinkedIn

LinkedIn uses OAuth 2.0, which is more complex than a simple API key:

### Authorization Flow:

1. **User Authorization**:
   - Redirect user to LinkedIn authorization URL
   - User logs in and grants permissions
   - LinkedIn redirects back with authorization code

2. **Token Exchange**:
   - Exchange authorization code for access token
   - Access token is valid for 60 days
   - Refresh token can be used to get new access token

3. **API Calls**:
   - Use access token in API requests
   - Token goes in Authorization header

### Example Authorization URL:

```
https://www.linkedin.com/oauth/v2/authorization?
  response_type=code&
  client_id=YOUR_CLIENT_ID&
  redirect_uri=YOUR_REDIRECT_URI&
  scope=r_liteprofile%20r_emailaddress%20w_member_social
```

## Available Scopes (Permissions)

Depending on approved products, you may have access to:

**Basic Scopes** (Sign In with LinkedIn):
- `r_liteprofile` - Basic profile info
- `r_emailaddress` - Email address

**Share Scopes** (Share on LinkedIn):
- `w_member_social` - Post on behalf of user

**Marketing Platform Scopes** (Marketing Developer Platform):
- `r_organization_social` - Read company posts
- `w_organization_social` - Write company posts
- `rw_organization_admin` - Manage company page
- `r_ads` - Read advertising data
- `r_ads_reporting` - Read ad analytics

## Implementation Notes

### For Your Wireless Monitor App:

The current implementation in `app/enhancements.py` has a `MockLinkedInClient` because:
1. LinkedIn API requires OAuth 2.0 flow (not simple API keys)
2. Need user to authorize the app
3. Requires web server to handle OAuth callback
4. Access tokens expire and need refresh

### To Implement Real LinkedIn Integration:

You'll need to:

1. **Add OAuth routes** to `app/main.py`:
   ```python
   @app.route('/auth/linkedin')
   def linkedin_auth():
       # Redirect to LinkedIn authorization
   
   @app.route('/auth/linkedin/callback')
   def linkedin_callback():
       # Handle OAuth callback
       # Exchange code for token
       # Store token in database
   ```

2. **Store access tokens** in database:
   ```sql
   ALTER TABLE social_config 
   ADD COLUMN access_token TEXT,
   ADD COLUMN refresh_token TEXT,
   ADD COLUMN token_expires_at TIMESTAMP;
   ```

3. **Implement token refresh**:
   - Check if token is expired before each API call
   - Use refresh token to get new access token
   - Update stored tokens

4. **Use LinkedIn API**:
   ```python
   import requests
   
   headers = {
       'Authorization': f'Bearer {access_token}',
       'Content-Type': 'application/json'
   }
   
   response = requests.get(
       'https://api.linkedin.com/v2/me',
       headers=headers
   )
   ```

## API Endpoints You'll Use

### Get User Profile:
```
GET https://api.linkedin.com/v2/me
```

### Get Company Posts (requires Marketing Platform):
```
GET https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List(urn:li:organization:{company_id})
```

### Share Content:
```
POST https://api.linkedin.com/v2/ugcPosts
```

### Get Post Analytics (requires Marketing Platform):
```
GET https://api.linkedin.com/v2/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{company_id}
```

## Rate Limits

LinkedIn has strict rate limits:

**Application-level limits**:
- 500 requests per user per day (default)
- 100 requests per user per hour (default)

**Endpoint-specific limits**:
- Vary by endpoint and product
- Marketing Platform has higher limits

**Best Practices**:
- Cache responses when possible
- Use webhooks instead of polling
- Implement exponential backoff
- Monitor rate limit headers

## Costs

**Free Tier**:
- Sign In with LinkedIn: Free
- Share on LinkedIn: Free
- Very limited functionality

**Marketing Developer Platform**:
- Requires LinkedIn Marketing Solutions subscription
- Pricing varies by company size
- Typically starts at $500-1000/month
- Includes API access + marketing tools

**Enterprise**:
- Custom pricing
- Dedicated support
- Higher rate limits

## Alternative: RSS Feeds

If you just want to monitor public LinkedIn posts without API access:

**LinkedIn Company Page RSS** (if available):
```
https://www.linkedin.com/company/{company-name}/posts/?feedView=all
```

**Note**: LinkedIn has been phasing out RSS feeds, so this may not work for all pages.

## Troubleshooting

### "Access Denied" Error
- Check that you're an admin of the company page
- Verify company page is complete and verified
- Ensure you've accepted LinkedIn's terms

### "Invalid Redirect URI"
- Must exactly match what you configured in app settings
- Include protocol (http:// or https://)
- No trailing slashes unless configured that way

### "Insufficient Permissions"
- Check which products are approved
- Verify OAuth scopes match your approved products
- Some features require Marketing Platform

### "Rate Limit Exceeded"
- Wait for rate limit window to reset
- Implement caching
- Reduce API call frequency

### Application Rejected
- Provide more detailed use case
- Add screenshots or mockups
- Explain business value
- Reapply with more information

## Recommended Approach for Your Project

Given the complexity and cost of LinkedIn API:

### Option 1: Use Mock Data (Current)
- Keep the `MockLinkedInClient`
- Shows realistic examples
- No API costs or approval needed
- Good for development and demo

### Option 2: Manual Curation
- Manually add LinkedIn posts to database
- Use admin interface to input content
- No API needed
- Full control over content

### Option 3: RSS/Web Scraping
- Monitor LinkedIn company page via web scraping
- Use tools like Selenium or Playwright
- Against LinkedIn ToS (use carefully)
- May break if LinkedIn changes layout

### Option 4: Full API Integration
- Apply for Marketing Developer Platform
- Implement OAuth 2.0 flow
- Handle token management
- Pay for LinkedIn Marketing Solutions
- Best for production use

## Summary

**Quick Start** (if you have a company page):
1. Go to https://www.linkedin.com/developers/
2. Create app
3. Get Client ID and Secret
4. Apply for Marketing Developer Platform
5. Wait for approval (1-4 weeks)
6. Implement OAuth flow
7. Start making API calls

**Reality Check**:
- LinkedIn API is expensive and complex
- Approval process is lengthy
- Free tier is very limited
- Consider if you really need it

**For Your Wireless Monitor**:
- Mock data works great for now
- Focus on other features first
- Revisit LinkedIn integration later if needed
- Consider manual curation as alternative

---

**Need Help?**
- LinkedIn Developer Docs: https://docs.microsoft.com/en-us/linkedin/
- LinkedIn Developer Support: https://www.linkedin.com/help/linkedin/answer/a1348614
- Community Forums: https://www.linkedin.com/groups/4973032/

**Questions?** Let me know if you need help with any specific step!
