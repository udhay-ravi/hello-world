import hashlib
import re
from textblob import TextBlob
from typing import Tuple

def compute_content_hash(text: str) -> str:
    """Generate SHA-256 hash of text content for deduplication"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    # Remove URLs
    text = re.sub(r'http\S+|www.\S+', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?\-\'"]', '', text)
    return text.strip()

def get_sentiment_score(text: str) -> float:
    """Get sentiment polarity score using TextBlob (-1 to 1)"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except:
        return 0.0

def extract_excerpt(text: str, max_length: int = 200) -> str:
    """Extract a meaningful excerpt from text"""
    cleaned = clean_text(text)
    if len(cleaned) <= max_length:
        return cleaned

    # Try to break at sentence boundary
    sentences = cleaned[:max_length + 50].split('.')
    if len(sentences) > 1:
        excerpt = sentences[0] + '.'
        if len(excerpt) <= max_length:
            return excerpt

    # Break at word boundary
    excerpt = cleaned[:max_length].rsplit(' ', 1)[0]
    return excerpt + '...'

def detect_product(text: str) -> str:
    """Detect which DigitalOcean product is mentioned"""
    text_lower = text.lower()

    products = {
        'VPC': ['vpc', 'virtual private cloud', 'private network'],
        'Load Balancer': ['load balancer', 'load balancing', 'lb', 'loadbalancer'],
        'NAT Gateway': ['nat gateway', 'nat', 'network address translation'],
        'Floating IP': ['floating ip', 'reserved ip', 'elastic ip'],
        'Firewall': ['firewall', 'security group', 'firewall rule'],
        'Networking': ['networking', 'network', 'connectivity', 'bandwidth']
    }

    for product, keywords in products.items():
        for keyword in keywords:
            if keyword in text_lower:
                return product

    return 'Networking'  # Default category

def extract_keywords(text: str, top_n: int = 5) -> list:
    """Extract important keywords from text"""
    blob = TextBlob(text)
    words = [word.lower() for word in blob.words if len(word) > 3]

    # Filter common words
    stop_words = {'this', 'that', 'with', 'from', 'have', 'been', 'were', 'their', 'there'}
    keywords = [w for w in words if w not in stop_words]

    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1

    # Return top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]
