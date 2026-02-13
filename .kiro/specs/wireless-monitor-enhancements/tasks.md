# Implementation Plan: Wireless Monitor Enhancements

## Overview

This implementation plan adds four major enhancements to the existing Wireless Monitor System: enhanced image scraping with multi-strategy extraction, social media account monitoring and content integration, automated Wild Wi-Fi story curation, and social media event discovery. The implementation is structured to build incrementally, starting with database schema extensions, then implementing each enhancement feature, and finally integrating everything with comprehensive testing.

## Tasks

- [ ] 1. Database Schema Extensions
  - [ ] 1.1 Create new database tables for social media features
    - Create social_accounts table with platform, username, active status
    - Create social_posts table with post content and engagement metrics
    - Create social_article_shares table linking articles to social posts
    - Create network_contacts table for user network configuration
    - Create event_social_mentions table linking events to social posts
    - Create image_metadata table for detailed image information
    - Create rate_limit_state table for API rate limit tracking
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_
  
  - [ ] 1.2 Extend existing tables with new columns
    - Add social_source, social_relevance_score, share_count to articles table
    - Add quality_score, auto_discovered, source_article_id, view_count, featured_duration to wild_wifi_stories table
    - Add confidence_score, discovered_from_social, social_mention_count to industry_events table
    - Add access_token_secret, bearer_token to social_config table
    - _Requirements: 15.8, 15.9_
  
  - [ ] 1.3 Create database indexes for performance
    - Create index on social_posts(account_id, created_at)
    - Create index on social_article_shares(article_id)
    - Create index on image_metadata(article_id)
    - Create index on articles(social_source, relevance_score)
    - Create index on wild_wifi_stories(quality_score, featured)
    - _Requirements: 15.11_
  
  - [ ]* 1.4 Write property test for foreign key integrity
    - **Property 18: Foreign Key Integrity**
    - **Validates: Requirements 15.10**


- [ ] 2. API Client Infrastructure
  - [ ] 2.1 Implement Base API Client abstract class
    - Create BaseAPIClient with abstract methods for platform integration
    - Implement get_platform_name, fetch_user_posts, validate_credentials methods
    - Implement normalize_post and extract_urls helper methods
    - _Requirements: 12.1, 12.4_
  
  - [ ] 2.2 Implement Rate Limiter component
    - Create RateLimiter class with platform-specific limits
    - Implement load_state and save_state for persistent rate limit tracking
    - Implement acquire method with blocking and exponential backoff
    - Implement get_status method for rate limit monitoring
    - Configure Twitter limits (900 requests per 15 minutes)
    - Configure LinkedIn limits (100 requests per day)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7_
  
  - [ ]* 2.3 Write property test for rate limit enforcement
    - **Property 11: Rate Limit Enforcement**
    - **Validates: Requirements 5.2, 5.3**
  
  - [ ] 2.4 Implement Twitter API Client
    - Create TwitterAPIClient extending BaseAPIClient
    - Implement authentication using tweepy with OAuth credentials
    - Implement fetch_user_posts using Twitter API v2
    - Implement normalize_post to convert tweets to common format
    - Handle Twitter-specific errors and rate limits
    - _Requirements: 12.2, 12.5, 12.6_
  
  - [ ] 2.5 Implement LinkedIn API Client
    - Create LinkedInAPIClient extending BaseAPIClient
    - Implement authentication using linkedin-api library
    - Implement fetch_user_posts for LinkedIn profiles
    - Implement normalize_post to convert LinkedIn posts to common format
    - Handle LinkedIn-specific errors and rate limits
    - _Requirements: 12.3, 12.5, 12.6_
  
  - [ ]* 2.6 Write unit tests for API clients
    - Test Twitter client with mocked API responses
    - Test LinkedIn client with mocked API responses
    - Test error handling for authentication failures
    - Test error handling for network timeouts
    - _Requirements: 12.8, 17.2, 17.4_

- [ ] 3. Checkpoint - Verify API infrastructure
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Enhanced Image Scraper
  - [ ] 4.1 Implement EnhancedImageScraper class with async support
    - Create EnhancedImageScraper with aiohttp session
    - Implement cache with TTL (24 hours)
    - Implement scrape_article_image main method
    - _Requirements: 1.1, 1.12_
  
  - [ ] 4.2 Implement image extraction strategies
    - Implement extract_opengraph_image method
    - Implement extract_twitter_card_image method
    - Implement extract_jsonld_image method
    - Implement analyze_content_images with scoring algorithm
    - Ensure strategies are tried in priority order
    - _Requirements: 1.3, 1.4, 1.5, 1.6, 1.7_
  
  - [ ]* 4.3 Write property test for multi-strategy extraction
    - **Property 1: Multi-Strategy Image Extraction**
    - **Validates: Requirements 1.1, 1.2**
  
  - [ ] 4.4 Implement image quality validation
    - Implement validate_image_quality method
    - Check dimensions >= 400x300 pixels
    - Check file size >= 10KB
    - Check for tracking/pixel/icon/logo keywords in URL
    - Use HTTP HEAD requests for efficiency
    - _Requirements: 1.8, 1.9, 1.10, 18.2_
  
  - [ ]* 4.5 Write property test for image quality validation
    - **Property 2: Image Quality Validation**
    - **Validates: Requirements 1.8, 1.9, 1.10**
  
  - [ ] 4.6 Implement image scoring algorithm
    - Implement score_image method
    - Score based on dimensions (max 30 points)
    - Score based on file size (max 20 points)
    - Score based on position in DOM (max 15 points)
    - Score based on context relevance (max 20 points)
    - Score based on aspect ratio (max 15 points)
    - _Requirements: 1.7_
  
  - [ ] 4.7 Implement caching and timeout mechanisms
    - Implement cache hit/miss logic
    - Implement 10-second timeout per article
    - Implement cache persistence across restarts
    - _Requirements: 1.12, 18.1, 18.3_
  
  - [ ]* 4.8 Write property tests for caching and timeout
    - **Property 3: Image Scraping Cache Consistency**
    - **Property 4: Image Extraction Timeout**
    - **Validates: Requirements 1.12, 18.1, 18.3**
  
  - [ ] 4.9 Integrate enhanced scraper with existing feed manager
    - Replace existing image scraper calls with EnhancedImageScraper
    - Store image metadata in image_metadata table
    - Track extraction strategy used
    - Maintain fallback to existing image generation
    - _Requirements: 1.13, 13.1, 13.2, 13.3, 13.4, 13.5_
  
  - [ ]* 4.10 Write unit tests for image scraper integration
    - Test with various news site HTML structures
    - Test fallback to generation when all strategies fail
    - Test metadata storage
    - _Requirements: 1.11, 13.6, 13.7_

- [ ] 5. Checkpoint - Verify enhanced image scraping
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 6. Social Media Monitor
  - [ ] 6.1 Implement credential encryption/decryption
    - Use cryptography library for AES encryption
    - Store encryption key in environment variable
    - Implement encrypt and decrypt methods
    - _Requirements: 23.1, 23.2_
  
  - [ ] 6.2 Implement SocialMediaMonitor class
    - Create SocialMediaMonitor with database and rate limiter
    - Implement initialize_clients to load API clients
    - Implement decrypt method for credentials
    - _Requirements: 3.2, 12.7_
  
  - [ ] 6.3 Implement social media account fetching
    - Implement fetch_all_accounts method
    - Query active accounts from database
    - Fetch posts for each account using appropriate API client
    - Handle errors per account without stopping entire process
    - Update last_fetched timestamp after successful fetch
    - _Requirements: 3.1, 3.10, 17.1_
  
  - [ ]* 6.4 Write property tests for social media monitoring
    - **Property 6: Social Media Error Isolation**
    - **Property 7: Account Fetch Timestamp Update**
    - **Validates: Requirements 3.9, 3.10**
  
  - [ ] 6.5 Implement social media post storage
    - Implement store_post method
    - Extract post text, URLs, timestamps, engagement metrics
    - Store in social_posts table
    - _Requirements: 3.3, 3.5, 3.7_
  
  - [ ] 6.6 Implement article URL extraction and processing
    - Implement is_article_url method to filter non-article URLs
    - Implement process_article_url method
    - Fetch article content from extracted URLs
    - Calculate relevance scores using existing ContentAnalyzer
    - Store articles with social_source flag
    - Link articles to social posts via social_article_shares
    - _Requirements: 3.4, 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [ ]* 6.7 Write property tests for article deduplication
    - **Property 8: Article URL Deduplication Across Sources**
    - **Property 9: Social Share Tracking Completeness**
    - **Validates: Requirements 4.9, 4.10, 19.1**
  
  - [ ] 6.8 Implement social relevance scoring
    - Calculate base relevance using existing keyword analysis
    - Boost scores for articles shared by multiple accounts
    - Boost scores for articles with high engagement
    - Calculate composite relevance score
    - _Requirements: 14.1, 14.2, 14.3, 14.5, 14.6, 14.7_
  
  - [ ]* 6.9 Write property test for article merge score selection
    - **Property 10: Article Merge Score Selection**
    - **Validates: Requirements 19.5**
  
  - [ ] 6.10 Implement content filtering
    - Filter posts by wireless technology keywords
    - Filter posts by presence of article URLs
    - Skip replies and retweets without additional content
    - Log filtered post counts
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6_
  
  - [ ]* 6.11 Write property test for content filtering
    - **Property 19: Social Media Content Filtering**
    - **Validates: Requirements 24.2, 24.3**
  
  - [ ]* 6.12 Write unit tests for social media monitor
    - Test post storage with various post formats
    - Test article extraction from posts
    - Test deduplication with RSS articles
    - Test error handling for API failures
    - _Requirements: 3.8, 4.8, 19.2, 19.3, 19.4, 19.6_

- [ ] 7. Checkpoint - Verify social media integration
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Wild Wi-Fi Curator
  - [ ] 8.1 Implement WildWiFiCurator class
    - Create WildWiFiCurator with database connection
    - Define humor indicators and tech keywords
    - _Requirements: 6.1_
  
  - [ ] 8.2 Implement humor scoring algorithm
    - Implement calculate_humor_score method
    - Count humor indicators (max 3 points)
    - Analyze sentiment for unexpectedness (max 3 points)
    - Check for specific details (max 2 points)
    - Check for irony/contrast (max 2 points)
    - Use TextBlob for sentiment analysis
    - _Requirements: 6.2, 6.3_
  
  - [ ] 8.3 Implement technical relevance scoring
    - Implement calculate_tech_relevance_score method
    - Count tech keywords (max 6 points)
    - Score tech relevance explanation (max 4 points)
    - _Requirements: 6.3, 6.4_
  
  - [ ] 8.4 Implement quality score calculation
    - Implement calculate_quality_score method
    - Weight humor score 40%
    - Weight tech relevance 30%
    - Weight completeness 20% (location, source, category)
    - Weight length 10% (prefer 100-500 words)
    - _Requirements: 6.5, 6.6_
  
  - [ ]* 8.5 Write property test for humor score calculation
    - **Property 12: Humor Score Calculation and Updates**
    - **Validates: Requirements 6.1, 6.7**
  
  - [ ] 8.6 Implement story scoring updates
    - Implement update_all_scores method
    - Recalculate scores for all stories
    - Update humor_rating and quality_score in database
    - _Requirements: 6.7_
  
  - [ ] 8.7 Implement featuring logic
    - Implement update_featured_stories method
    - Sort stories by quality score with freshness boost
    - Feature top 5 stories with quality > 75
    - Unfeature stories with quality < 75
    - Apply freshness boost for stories < 30 days old
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  
  - [ ]* 8.8 Write property tests for story featuring
    - **Property 13: Quality-Based Story Featuring**
    - **Property 14: Featured Story Limit**
    - **Validates: Requirements 7.2, 7.3, 7.4**
  
  - [ ] 8.9 Implement auto-discovery from articles
    - Scan article content for potential Wild Wi-Fi stories
    - Identify stories with humor indicators
    - Extract story text and context
    - Calculate initial quality score
    - Mark as pending approval
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.9_
  
  - [ ]* 8.10 Write unit tests for Wild Wi-Fi curator
    - Test humor scoring with example stories
    - Test quality scoring with various story attributes
    - Test featuring logic with different score distributions
    - Test auto-discovery from article text
    - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5_

- [ ] 9. Checkpoint - Verify Wild Wi-Fi curation
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 10. Social Event Discoverer
  - [ ] 10.1 Implement SocialEventDiscoverer class
    - Create SocialEventDiscoverer with database connection
    - Define event patterns (CES, MWC, conferences, summits, expos)
    - Define location patterns
    - _Requirements: 9.1, 9.2_
  
  - [ ] 10.2 Implement event extraction from text
    - Implement extract_events_from_text method
    - Use regex patterns to find event mentions
    - Extract event name, year, location
    - Extract hashtags from post
    - _Requirements: 9.2, 9.3, 9.5_
  
  - [ ] 10.3 Implement event confidence scoring
    - Implement calculate_event_confidence method
    - Score known event names (40 points)
    - Score location presence (20 points)
    - Score hashtags (15 points)
    - Score date mentions (15 points)
    - Score attendance keywords (10 points)
    - _Requirements: 21.1, 21.2, 21.3, 21.4, 21.5, 21.6_
  
  - [ ]* 10.4 Write property test for event confidence scoring
    - **Property 17: Event Confidence Scoring Factors**
    - **Validates: Requirements 21.2, 21.5**
  
  - [ ] 10.5 Implement event discovery from posts
    - Implement discover_events_from_posts method
    - Scan recent social media posts (last 30 days)
    - Extract events from each post
    - Check for existing events
    - Create new events or update existing
    - Link posts to events
    - _Requirements: 9.1, 9.6, 9.7, 9.8_
  
  - [ ] 10.6 Implement event deduplication and merging
    - Implement find_existing_event method
    - Match events by name and year
    - Implement update_event_from_post method
    - Merge event information from multiple posts
    - _Requirements: 9.9, 9.10_
  
  - [ ]* 10.7 Write property test for event deduplication
    - **Property 15: Event Deduplication and Merging**
    - **Validates: Requirements 9.9, 9.10**
  
  - [ ] 10.8 Implement event date estimation
    - Implement estimate_event_dates method
    - Use known schedules for CES, MWC, IFA, NRF
    - Default to current date ± 3 days for unknown events
    - _Requirements: 9.5_
  
  - [ ] 10.9 Implement event-article linking
    - Search existing articles for event mentions
    - Search for new articles about discovered events
    - Calculate event relevance scores
    - Link articles with relevance > 0.15 to events
    - Prioritize articles shared by attending accounts
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_
  
  - [ ]* 10.10 Write property test for event-article linking
    - **Property 16: Event-Article Relevance Linking**
    - **Validates: Requirements 10.4**
  
  - [ ] 10.11 Implement network contact tracking
    - Track which contacts are attending which events
    - Mark event mentions from network contacts
    - Display contact activity in admin dashboard
    - _Requirements: 9.8, 11.6, 11.7_
  
  - [ ]* 10.12 Write unit tests for event discoverer
    - Test event extraction with known patterns
    - Test confidence scoring with various inputs
    - Test deduplication with similar event names
    - Test article linking with event keywords
    - _Requirements: 21.7, 21.8_

- [ ] 11. Checkpoint - Verify event discovery
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Admin Dashboard Extensions
  - [ ] 12.1 Create social media accounts management UI
    - Add page for listing social media accounts
    - Add form for adding new accounts
    - Add buttons for toggling account active status
    - Add buttons for removing accounts
    - Display last_fetched timestamp and post counts
    - _Requirements: 2.4, 2.5, 2.6, 16.1_
  
  - [ ] 12.2 Create API credentials configuration UI
    - Add form for entering API credentials
    - Mask credentials display (show only last 4 characters)
    - Validate credentials before saving
    - Display validation status
    - _Requirements: 23.3, 23.4, 23.5, 23.6, 23.7_
  
  - [ ] 12.3 Create social media statistics dashboard
    - Display posts fetched count
    - Display articles discovered count
    - Display rate limit status for each platform
    - Display last fetch timestamp
    - Add manual trigger button for social media fetch
    - _Requirements: 16.2, 16.3, 16.8_
  
  - [ ] 12.4 Create Wild Wi-Fi curation management UI
    - Display list of pending stories for approval
    - Display quality scores and humor ratings
    - Add buttons for approving/rejecting stories
    - Add form for manually adjusting scores
    - Add manual trigger button for curation
    - Display featuring statistics
    - _Requirements: 7.8, 7.9, 7.10, 8.6, 8.7, 8.8, 16.4, 16.5, 16.9_
  
  - [ ] 12.5 Create event discovery dashboard
    - Display discovered events with confidence scores
    - Display social media mentions for each event
    - Display network contact activity
    - Add manual trigger button for event discovery
    - Allow filtering events by confidence score
    - _Requirements: 16.6, 16.7, 16.10, 21.6, 21.7_
  
  - [ ] 12.6 Create image scraping statistics dashboard
    - Display success rates by extraction strategy
    - Display average extraction time
    - Display cache hit rate
    - Display image quality distribution
    - _Requirements: 13.7, 13.8, 16.11, 18.7_
  
  - [ ]* 12.7 Write unit tests for admin dashboard
    - Test all new admin endpoints
    - Test form validation
    - Test manual trigger buttons
    - Test statistics display

- [ ] 13. Scheduler Integration
  - [ ] 13.1 Add social media fetch to scheduler
    - Schedule social media fetch every 6 hours
    - Run at same time as RSS feed fetch
    - Log execution with timestamps and results
    - _Requirements: 22.1, 22.2, 22.6_
  
  - [ ] 13.2 Add Wild Wi-Fi curation to scheduler
    - Schedule curation every 8 hours
    - Update scores and featured status
    - Log execution with statistics
    - _Requirements: 22.3, 22.6_
  
  - [ ] 13.3 Add event discovery to scheduler
    - Schedule event discovery every 6 hours
    - Run after social media fetch
    - Log execution with discovered events count
    - _Requirements: 22.4, 22.6_
  
  - [ ] 13.4 Add manual trigger support
    - Allow manual triggering of any scheduled task
    - Display next scheduled execution time in admin dashboard
    - _Requirements: 22.5, 22.7_
  
  - [ ]* 13.5 Write unit tests for scheduler integration
    - Test scheduled task execution
    - Test manual trigger functionality
    - Test task execution logging

- [ ] 14. Integration and Testing
  - [ ] 14.1 Implement database migration script
    - Create migration script for schema extensions
    - Handle existing data preservation
    - Test migration on copy of production database
    - _Requirements: 25.3_
  
  - [ ] 14.2 Test backward compatibility
    - Run all existing RSS feed tests
    - Run all existing article display tests
    - Run all existing event detection tests
    - Run all existing image generation tests
    - Verify no regressions
    - _Requirements: 25.1, 25.2_
  
  - [ ]* 14.3 Write property test for backward compatibility
    - **Property 20: Backward Compatibility Preservation**
    - **Validates: Requirements 25.1, 25.2**
  
  - [ ] 14.4 Test graceful degradation
    - Test system with missing social media credentials
    - Test system with social media APIs unavailable
    - Verify RSS feeds continue working
    - _Requirements: 25.4, 25.5_
  
  - [ ] 14.5 Implement test mode for social media integration
    - Create test mode flag
    - Use test data instead of real API calls in test mode
    - Verify all features work in test mode
    - _Requirements: 25.7_
  
  - [ ]* 14.6 Write integration tests
    - Test end-to-end social media flow
    - Test end-to-end image scraping flow
    - Test end-to-end Wild Wi-Fi curation flow
    - Test end-to-end event discovery flow
  
  - [ ]* 14.7 Write performance tests
    - Test social media fetch with 100 accounts
    - Test image scraping with 1000 articles
    - Test Wild Wi-Fi scoring with 500 stories
    - Test event discovery with 10,000 posts
    - Verify performance targets are met

- [ ] 15. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. Documentation and Deployment
  - [ ] 16.1 Update README with new features
    - Document social media integration setup
    - Document API credential configuration
    - Document new admin dashboard features
    - Document new scheduled tasks
  
  - [ ] 16.2 Create deployment guide
    - Document database migration steps
    - Document dependency installation
    - Document environment variable configuration
    - Document service restart procedure
  
  - [ ] 16.3 Create troubleshooting guide
    - Document common API authentication issues
    - Document rate limit handling
    - Document image scraping failures
    - Document error log locations

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end flows
- The implementation builds incrementally: database → API clients → features → integration
- Social media features can be disabled if APIs are unavailable
- Enhanced image scraping falls back to existing generation if needed
