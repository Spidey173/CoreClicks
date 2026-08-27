import math
import re
import secrets
import string
from typing import Any, Dict, List

COMMON_BREACH_PASSWORDS = {
    "123456", "password", "123456789", "12345678", "12345", "111111", "1234567",
    "sunshine", "qwerty", "iloveyou", "princess", "admin", "welcome", "football",
    "monkey", "charlie", "donald", "password123", "secret", "master", "shadow",
    "superman", "batman", "trustno1", "computer", "access", "dragon", "baseball",
}

WORDS_LIST = [
    "amber", "blaze", "crystal", "delta", "echo", "falcon", "glacier", "horizon",
    "island", "jungle", "knight", "lunar", "matrix", "nebula", "orbit", "phoenix",
    "quantum", "radar", "shadow", "titan", "ultra", "vector", "wizard", "zenith",
    "beacon", "canyon", "drift", "ember", "frost", "galaxy", "harbor", "impact",
    "kinetic", "laser", "mirage", "nova", "omega", "pulse", "quasar", "stellar",
]


def mask_password(password: str) -> str:
    """Generates non-reversible masked representation (e.g. 'pa****rd')."""
    if not password:
        return ""
    length = len(password)
    if length <= 4:
        return "*" * length
    return f"{password[:2]}{'*' * (length - 4)}{password[-2:]}"


def calculate_entropy(password: str) -> float:
    """Calculates Shannon Entropy in bits for a given password."""
    if not password:
        return 0.0

    charset_size = 0
    if any(c in string.ascii_lowercase for c in password):
        charset_size += 26
    if any(c in string.ascii_uppercase for c in password):
        charset_size += 26
    if any(c in string.digits for c in password):
        charset_size += 10
    if any(c in string.punctuation or c in " ~`!@#$%^&*()-_=+[{]}\\|;:'\",<.>/?" for c in password):
        charset_size += 33

    if charset_size == 0:
        return 0.0

    entropy = len(password) * math.log2(charset_size)
    return round(entropy, 2)


def estimate_crack_time(entropy_bits: float) -> str:
    """Estimates time to crack at 10 billion guesses/second."""
    if entropy_bits <= 0:
        return "Instant"

    total_combinations = 2 ** entropy_bits
    guesses_per_sec = 10_000_000_000  # 10 billion/sec GPU cluster
    seconds = total_combinations / guesses_per_sec

    if seconds < 1:
        return "Instant"
    elif seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        return f"{int(seconds / 60)} minutes"
    elif seconds < 86400:
        return f"{int(seconds / 3600)} hours"
    elif seconds < 31536000:
        return f"{int(seconds / 86400)} days"
    elif seconds < 31536000 * 1000:
        return f"{int(seconds / 31536000)} years"
    elif seconds < 31536000 * 1_000_000:
        return f"{int(seconds / (31536000 * 1000))} millennia"
    return "Trillions of years"


def analyze_password(password: str) -> Dict[str, Any]:
    """Comprehensive NIST-aligned password strength auditor."""
    length = len(password)
    entropy = calculate_entropy(password)

    has_lower = bool(re.search(r"[a-z]", password))
    has_upper = bool(re.search(r"[A-Z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>[\]\\/`~_+=';-]", password))
    is_common = password.lower() in COMMON_BREACH_PASSWORDS

    # Score out of 100
    score = 0
    if length >= 8:
        score += 20
    if length >= 12:
        score += 15
    if length >= 16:
        score += 10
    if has_lower:
        score += 10
    if has_upper:
        score += 15
    if has_digit:
        score += 15
    if has_symbol:
        score += 15

    # Penalties
    if is_common:
        score = min(score, 10)
    elif length < 6:
        score = min(score, 15)

    # Classify strength
    if score < 30:
        strength = "Very Weak"
    elif score < 50:
        strength = "Weak"
    elif score < 70:
        strength = "Fair"
    elif score < 85:
        strength = "Strong"
    else:
        strength = "Very Strong"

    recommendations = []
    if length < 12:
        recommendations.append("Increase length to at least 12-16 characters.")
    if not has_upper:
        recommendations.append("Add uppercase letters (A-Z).")
    if not has_digit:
        recommendations.append("Include numerical digits (0-9).")
    if not has_symbol:
        recommendations.append("Add special symbols (!@#$%^&*).")
    if is_common:
        recommendations.append("This password appears in known breach dictionaries. Do not use!")

    return {
        "score": score,
        "strength": strength,
        "entropy_bits": entropy,
        "crack_time": estimate_crack_time(entropy),
        "length": length,
        "masked": mask_password(password),
        "is_breached": is_common,
        "character_breakdown": {
            "lowercase": has_lower,
            "uppercase": has_upper,
            "digits": has_digit,
            "symbols": has_symbol,
        },
        "recommendations": recommendations,
    }


def generate_secure_password(length: int = 16, uppercase: bool = True, numbers: bool = True, symbols: bool = True) -> str:
    """Generates a cryptographically secure random password."""
    length = max(8, min(64, length))
    charset = string.ascii_lowercase
    guaranteed = [secrets.choice(string.ascii_lowercase)]

    if uppercase:
        charset += string.ascii_uppercase
        guaranteed.append(secrets.choice(string.ascii_uppercase))
    if numbers:
        charset += string.digits
        guaranteed.append(secrets.choice(string.digits))
    if symbols:
        symbols_set = "!@#$%^&*()-_=+"
        charset += symbols_set
        guaranteed.append(secrets.choice(symbols_set))

    remaining = [secrets.choice(charset) for _ in range(length - len(guaranteed))]
    password_chars = guaranteed + remaining
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


def generate_passphrase(word_count: int = 4, separator: str = "-", include_number: bool = True) -> str:
    """Generates a memorable, high-entropy Diceware-style passphrase."""
    word_count = max(3, min(8, word_count))
    selected_words = [secrets.choice(WORDS_LIST) for _ in range(word_count)]
    passphrase = separator.join(selected_words)

    if include_number:
        num = secrets.randbelow(100)
        passphrase += f"{separator}{num}"

    return passphrase
