#!/usr/bin/env python3
"""Populate database with sample data for demo purposes"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.database import SessionLocal, init_db, Problem, Mention
from app.utils.text_processing import compute_content_hash, get_sentiment_score, extract_excerpt

# Sample problems for each product
SAMPLE_PROBLEMS = {
    'VPC': [
        {
            'summary': 'VPC peering connection fails intermittently',
            'description': 'Users report that VPC peering connections drop randomly, causing connectivity issues between different VPCs. This happens 2-3 times per week and requires manual intervention to restore.',
            'severity': 8.5,
            'mentions': [
                ('reddit', 'I\'ve been having issues with VPC peering on DigitalOcean. The connection just drops randomly and I have to recreate it. Very frustrating for production workloads.', 'user_reddit_123'),
                ('stackoverflow', 'How do I debug VPC peering failures in DigitalOcean? My peering connection keeps disconnecting without any error messages.', 'dev_stackoverflow'),
                ('twitter', '@digitalocean VPC peering is unreliable. Connections drop multiple times per week. This is affecting our production services!', 'angry_user'),
            ]
        },
        {
            'summary': 'Cannot assign custom IP ranges to VPC',
            'description': 'DigitalOcean VPC only allows specific predefined IP ranges. Users need ability to specify custom CIDR blocks for better network planning and avoiding conflicts with on-premise networks.',
            'severity': 6.5,
            'mentions': [
                ('digitalocean_ideas', 'Please add support for custom IP ranges in VPC. The current limitation to specific ranges makes it hard to integrate with our existing infrastructure.', 'feature_requester'),
                ('reddit', 'Does anyone know how to use custom IP ranges in DO VPC? I need 10.50.0.0/16 but can\'t configure it.', 'confused_user'),
            ]
        },
        {
            'summary': 'VPC network latency higher than expected',
            'description': 'Users experiencing higher than expected latency (5-10ms) within VPC networks, especially when communicating across availability zones.',
            'severity': 7.0,
            'mentions': [
                ('reddit', 'Anyone else noticing high latency in DigitalOcean VPC? I\'m seeing 8-10ms between droplets in same VPC but different AZs.', 'performance_user'),
                ('hackernews', 'DigitalOcean VPC latency is concerning. Internal network should be faster than this.', 'hn_user'),
            ]
        }
    ],
    'Load Balancer': [
        {
            'summary': 'Load balancer health checks too aggressive causing false positives',
            'description': 'Health check intervals are too frequent and timeout values too strict, marking healthy backends as unhealthy during temporary spikes, causing unnecessary traffic disruption.',
            'severity': 9.0,
            'mentions': [
                ('reddit', 'DO load balancer health checks are killing me. My backend is healthy but LB keeps marking it down during load spikes. Need configurable timeouts!', 'ops_engineer'),
                ('stackoverflow', 'DigitalOcean load balancer marks backends as unhealthy even when they respond within 2 seconds. How to tune health check settings?', 'backend_dev'),
                ('twitter', '@digitalocean Load balancer health checks are too aggressive. Backends go down unnecessarily during traffic spikes.', 'frustrated_ops'),
                ('trustpilot', 'The load balancer health checks need better configuration options. Our services get marked unhealthy during normal operation.', 'trustpilot_user'),
            ]
        },
        {
            'summary': 'No support for WebSocket connection draining',
            'description': 'When removing a backend from load balancer, active WebSocket connections are dropped immediately instead of being drained gracefully, causing disconnections for real-time applications.',
            'severity': 8.0,
            'mentions': [
                ('digitalocean_ideas', 'Add WebSocket connection draining to load balancers. Current behavior drops all WS connections immediately when removing backend.', 'realtime_dev'),
                ('stackoverflow', 'How to gracefully drain WebSocket connections in DigitalOcean load balancer? My chat app users get disconnected during deployments.', 'chat_developer'),
            ]
        },
        {
            'summary': 'Load balancer SSL certificate renewal causes brief downtime',
            'description': 'Automatic SSL certificate renewal on load balancers causes 30-60 seconds of downtime during the renewal process, affecting availability.',
            'severity': 7.5,
            'mentions': [
                ('reddit', 'DigitalOcean LB SSL renewal just caused 45 seconds of downtime. Is this expected? Shouldn\'t it be zero-downtime?', 'ssl_user'),
                ('hackernews', 'Disappointed that DO load balancer SSL renewals aren\'t zero-downtime. Every 90 days we get a brief outage.', 'hn_critic'),
            ]
        }
    ],
    'NAT Gateway': [
        {
            'summary': 'NAT Gateway bandwidth limits not documented',
            'description': 'NAT Gateway has undocumented bandwidth limitations that cause throttling during high traffic periods, with no clear way to increase limits or monitor current usage.',
            'severity': 8.0,
            'mentions': [
                ('reddit', 'Hit some kind of bandwidth limit on DO NAT Gateway but can\'t find documentation on what the limits are. Traffic is being throttled.', 'network_admin'),
                ('stackoverflow', 'What are the bandwidth limits for DigitalOcean NAT Gateway? My traffic is being throttled but I can\'t find specs anywhere.', 'confused_admin'),
            ]
        },
        {
            'summary': 'NAT Gateway single point of failure with no HA option',
            'description': 'NAT Gateway doesn\'t support high availability configuration. If NAT Gateway fails, all outbound connectivity is lost with no automatic failover.',
            'severity': 9.0,
            'mentions': [
                ('digitalocean_ideas', 'Please add HA option for NAT Gateway. Current setup is single point of failure for entire VPC outbound connectivity.', 'reliability_engineer'),
                ('reddit', 'DO NAT Gateway went down and took out all our outbound traffic. Need HA support ASAP!', 'incident_responder'),
                ('twitter', '@digitalocean NAT Gateway needs HA support. Single point of failure is not acceptable for production.', 'enterprise_user'),
            ]
        }
    ],
    'Floating IP': [
        {
            'summary': 'Floating IP reassignment takes too long',
            'description': 'Reassigning floating IP to different droplet takes 30-60 seconds, which is too slow for automatic failover scenarios and causes extended downtime.',
            'severity': 8.5,
            'mentions': [
                ('reddit', 'Floating IP failover on DigitalOcean takes almost a minute. This is way too slow for automatic HA setups.', 'ha_builder'),
                ('stackoverflow', 'How to speed up DigitalOcean floating IP reassignment? Takes 45 seconds which breaks our failover requirements.', 'devops_team'),
                ('hackernews', 'DO floating IP reassignment latency makes it unsuitable for true HA. Need sub-second failover.', 'hn_architect'),
            ]
        },
        {
            'summary': 'Limited number of floating IPs per account',
            'description': 'Account is limited to small number of floating IPs (default 5) which is insufficient for larger deployments, and increase requests are slow to process.',
            'severity': 6.0,
            'mentions': [
                ('reddit', 'Only 5 floating IPs allowed per account? I need at least 20 for my infrastructure. Limit increase request is still pending after 3 days.', 'scaling_user'),
                ('digitalocean_ideas', 'Increase default floating IP limit or make it easier to request increases. Current process is too slow.', 'enterprise_customer'),
            ]
        }
    ],
    'Firewall': [
        {
            'summary': 'Firewall rules limited to 50 per firewall',
            'description': 'Firewall limited to 50 rules maximum, which is insufficient for complex security requirements. Need support for hundreds of rules or rule groups.',
            'severity': 7.5,
            'mentions': [
                ('stackoverflow', 'DigitalOcean firewall has 50 rule limit. How to handle more complex security requirements?', 'security_engineer'),
                ('digitalocean_ideas', 'Increase firewall rule limit from 50 to at least 500. Current limit is too restrictive for enterprise security policies.', 'security_team'),
                ('reddit', 'Hit the 50 firewall rule limit on DO. This is a major limitation for implementing proper security controls.', 'infosec_user'),
            ]
        },
        {
            'summary': 'No firewall logging or traffic visibility',
            'description': 'DigitalOcean firewalls don\'t provide any logging of blocked or allowed traffic, making it impossible to debug connectivity issues or audit security.',
            'severity': 9.0,
            'mentions': [
                ('reddit', 'How do I see what traffic is being blocked by DO firewall? No logging available anywhere!', 'debugging_dev'),
                ('digitalocean_ideas', 'PLEASE add firewall logging! Need to see blocked traffic for debugging and compliance. This is a critical missing feature.', 'compliance_officer'),
                ('twitter', '@digitalocean Firewall needs logging. Can\'t debug issues or meet compliance requirements without visibility into blocked traffic.', 'security_advocate'),
                ('stackoverflow', 'DigitalOcean firewall blocks my traffic but I can\'t see any logs. How to troubleshoot firewall rules?', 'network_troubleshooter'),
            ]
        },
        {
            'summary': 'Firewall changes take long time to apply',
            'description': 'When updating firewall rules, changes take 2-5 minutes to apply across all droplets, causing delays in incident response and deployment processes.',
            'severity': 7.0,
            'mentions': [
                ('reddit', 'DO firewall rule updates are so slow. Takes 3-4 minutes to apply, which is problematic during incidents.', 'ops_manager'),
                ('hackernews', 'DigitalOcean firewall rule propagation is painfully slow. Need near-instant updates for security incidents.', 'hn_security'),
            ]
        }
    ],
    'Networking': [
        {
            'summary': 'No private DNS for VPC resources',
            'description': 'VPC lacks built-in private DNS service, forcing users to maintain their own DNS infrastructure or use public DNS for internal resources.',
            'severity': 8.0,
            'mentions': [
                ('digitalocean_ideas', 'Add private DNS service for VPC. Need automatic DNS records for droplets within VPC without managing own DNS server.', 'cloud_architect'),
                ('reddit', 'Missing private DNS in DO VPC is a major gap. Every other cloud provider has this. Having to run own DNS server.', 'migration_user'),
                ('stackoverflow', 'What\'s the best way to handle DNS in DigitalOcean VPC? No built-in private DNS available.', 'infrastructure_dev'),
            ]
        },
        {
            'summary': 'Bandwidth monitoring and alerting insufficient',
            'description': 'Network bandwidth monitoring lacks granularity and doesn\'t support alerting on traffic spikes or quota exhaustion before overages occur.',
            'severity': 6.5,
            'mentions': [
                ('reddit', 'DO bandwidth monitoring is too basic. Need per-hour granularity and alerts before hitting quota limits.', 'billing_watcher'),
                ('twitter', '@digitalocean Need better bandwidth monitoring and alerts. Got surprised by overage charges.', 'cost_conscious'),
            ]
        }
    ]
}

SOURCES = ['reddit', 'twitter', 'stackoverflow', 'hackernews', 'digitalocean_ideas', 'trustpilot', 'google_trends']

def create_sample_data():
    """Create sample data in database"""
    print("Initializing database...")
    init_db()

    db = SessionLocal()

    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(Mention).delete()
        db.query(Problem).delete()
        db.commit()

        print("Creating sample problems and mentions...")

        for product, problems_data in SAMPLE_PROBLEMS.items():
            for problem_data in problems_data:
                # Create problem
                problem = Problem(
                    problem_summary=problem_data['summary'],
                    problem_description=problem_data['description'],
                    product=product,
                    severity_score=problem_data['severity'],
                    sentiment_score=random.uniform(-0.8, -0.2),  # Mostly negative
                    frequency=len(problem_data['mentions']),
                    first_seen=datetime.utcnow() - timedelta(days=random.randint(10, 60)),
                    last_seen=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
                    trend=random.choice(['rising', 'stable', 'declining'])
                )

                db.add(problem)
                db.flush()  # Get problem ID

                # Create mentions
                for source, text, author in problem_data['mentions']:
                    created_at = datetime.utcnow() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23)
                    )

                    mention = Mention(
                        problem_id=problem.id,
                        source=source,
                        source_url=f"https://{source}.com/post/{random.randint(1000, 9999)}",
                        raw_text=text,
                        excerpt=extract_excerpt(text),
                        author=author,
                        sentiment_score=get_sentiment_score(text),
                        created_at=created_at,
                        scraped_at=datetime.utcnow(),
                        content_hash=compute_content_hash(text)
                    )

                    db.add(mention)

                print(f"Created problem: {problem.problem_summary}")

        db.commit()

        # Print statistics
        total_problems = db.query(Problem).count()
        total_mentions = db.query(Mention).count()

        print(f"\n✅ Sample data created successfully!")
        print(f"   Total problems: {total_problems}")
        print(f"   Total mentions: {total_mentions}")
        print(f"\nYou can now start the backend server and view the dashboard.")

    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
