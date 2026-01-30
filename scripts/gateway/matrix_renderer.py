"""
LED Matrix Renderer

Converts product data to 12x8 LED matrix patterns for Arduino UNO R4 WiFi.
The Arduino has a 12x8 LED matrix that we can use to display:
- Price digits
- Simple icons
- Patterns

Since 12x8 is very limited, we focus on displaying the price as digits.
"""

from typing import Optional

# 5x3 digit font (height x width)
# Each digit is represented as a list of 5 rows, each row is 3 bits
DIGITS_5X3 = {
    '0': [
        [1, 1, 1],
        [1, 0, 1],
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    '1': [
        [0, 1, 0],
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 0],
        [1, 1, 1],
    ],
    '2': [
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
    ],
    '3': [
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
    ],
    '4': [
        [1, 0, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
    ],
    '5': [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
    ],
    '6': [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    '7': [
        [1, 1, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
    ],
    '8': [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    '9': [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
        [0, 0, 1],
        [1, 1, 1],
    ],
    '.': [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 1, 0],
    ],
    '$': [
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 1],
        [1, 1, 0],
        [0, 1, 0],
    ],
    ' ': [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ],
}

# Decimal point is 1 column wide
DECIMAL_POINT = [
    [0],
    [0],
    [0],
    [0],
    [1],
]


def create_empty_matrix() -> list[list[int]]:
    """Create an empty 8x12 matrix."""
    return [[0 for _ in range(12)] for _ in range(8)]


def render_digit(matrix: list[list[int]], digit: str, x: int, y: int) -> int:
    """
    Render a single digit onto the matrix.
    
    Args:
        matrix: 8x12 matrix to render onto
        digit: Character to render
        x: Starting x position (column)
        y: Starting y position (row)
        
    Returns:
        Width of the rendered character
    """
    if digit not in DIGITS_5X3:
        return 0
    
    font = DIGITS_5X3[digit]
    
    for row_idx, row in enumerate(font):
        for col_idx, pixel in enumerate(row):
            mx = x + col_idx
            my = y + row_idx
            
            if 0 <= mx < 12 and 0 <= my < 8:
                matrix[my][mx] = pixel
    
    return 3 if digit != '.' else 1


def render_price(price: float, currency_symbol: str = "", decimal_places: int = 2) -> list[list[int]]:
    """
    Render a price onto a 12x8 matrix.
    
    Only renders digits that will fit completely on screen.
    No centering - displays from top-left.
    
    Args:
        price: Price value (e.g., 4.99)
        currency_symbol: Currency symbol to display (e.g., "$", "€")
        decimal_places: Number of decimal places to show
        
    Returns:
        8x12 matrix
    """
    matrix = create_empty_matrix()
    
    # Format price with specified decimal places
    price_str = f"{price:.{decimal_places}f}"
    
    # Add currency symbol if provided
    if currency_symbol and currency_symbol in DIGITS_5X3:
        price_str = currency_symbol + price_str
    
    # Start from top-left corner
    x = 0
    y = 0
    
    # Render each character only if it fits completely
    for char in price_str:
        # Calculate width for this character
        if char == '.':
            char_width = 2  # 1 for dot + 1 spacing
        else:
            char_width = 4  # 3 for digit + 1 spacing
        
        # Check if character will fit (don't render if it would overflow)
        if x + char_width - 1 > 12:  # -1 because we don't need trailing space
            break
            
        width = render_digit(matrix, char, x, y)
        x += width + 1  # Add spacing
    
    return matrix


def render_clear() -> list[list[int]]:
    """Render a clear/empty matrix."""
    return create_empty_matrix()


def render_check() -> list[list[int]]:
    """Render a checkmark pattern (for success)."""
    matrix = create_empty_matrix()
    
    # Simple checkmark
    checkmark = [
        (9, 1), (8, 2), (7, 3), (6, 4), (5, 5), (4, 4), (3, 3)
    ]
    
    for x, y in checkmark:
        if 0 <= x < 12 and 0 <= y < 8:
            matrix[y][x] = 1
    
    return matrix


def render_x() -> list[list[int]]:
    """Render an X pattern (for error/not assigned)."""
    matrix = create_empty_matrix()
    
    # Draw X
    for i in range(6):
        x1 = 3 + i
        y1 = 1 + i
        x2 = 8 - i
        y2 = 1 + i
        
        if 0 <= x1 < 12 and 0 <= y1 < 8:
            matrix[y1][x1] = 1
        if 0 <= x2 < 12 and 0 <= y2 < 8:
            matrix[y2][x2] = 1
    
    return matrix


def render_waiting() -> list[list[int]]:
    """Render a waiting/hourglass pattern."""
    matrix = create_empty_matrix()
    
    # Simple hourglass shape
    pattern = [
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
    ]
    
    return pattern


def render_product(product: Optional[dict]) -> list[list[int]]:
    """
    Render product info to LED matrix.
    
    If product is provided, displays the price (discounted if available).
    If product is None, displays the X pattern.
    
    Args:
        product: Product dict with 'priceDetails' field from database, or None
        
    Returns:
        8x12 matrix
    """
    if product is None:
        return render_x()
    
    # Extract price from priceDetails (database format)
    price_details = product.get("priceDetails")
    
    if not price_details:
        return render_x()
    
    # Get currency info
    currency = price_details.get("currency", {})
    decimal_places = currency.get("decimalPlaces", 2)
    
    # Extract currency symbol (can be prefix or suffix)
    symbol_config = currency.get("symbol", {})
    currency_symbol = symbol_config.get("prefix", "") or symbol_config.get("suffix", "")
    
    # Check for discounted price first
    discount = price_details.get("discount")
    if discount:
        percentage = discount.get("percentage", 0)
        price_in_cents = price_details.get("priceInCents", 0)
        # Calculate discounted price
        discounted_cents = int(price_in_cents * (1 - percentage / 100))
        price = discounted_cents / (10 ** decimal_places)
    else:
        # Use regular price
        price_in_cents = price_details.get("priceInCents", 0)
        price = price_in_cents / (10 ** decimal_places)
    
    if price <= 0:
        return render_x()
    
    return render_price(price, currency_symbol, decimal_places)


def matrix_to_bytes(matrix: list[list[int]]) -> bytes:
    """
    Convert 8x12 matrix to 96-byte frame for Arduino.
    
    Args:
        matrix: 8x12 matrix (row-major)
        
    Returns:
        96 bytes (12*8), row-major order
    """
    frame = []
    for row in matrix:
        for pixel in row:
            frame.append(1 if pixel else 0)
    return bytes(frame)


def print_matrix(matrix: list[list[int]]) -> None:
    """Print matrix for debugging."""
    for row in matrix:
        print("".join("█" if p else "·" for p in row))


# For testing
if __name__ == "__main__":
    print("Price $4.99:")
    matrix = render_price(4.99)
    print_matrix(matrix)
    
    print("\nPrice $12.50:")
    matrix = render_price(12.50)
    print_matrix(matrix)
    
    print("\nPrice $9.99:")
    matrix = render_price(9.99)
    print_matrix(matrix)
    
    print("\nNo product (X):")
    matrix = render_x()
    print_matrix(matrix)
    
    print("\nWaiting:")
    matrix = render_waiting()
    print_matrix(matrix)
