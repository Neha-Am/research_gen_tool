import re
from typing import Dict, List, Tuple

class MathFormatter:
    """Handles mathematical notation formatting and validation for IEEE papers"""
    
    def __init__(self):
        # Define common mathematical symbols and their proper representations
        self.greek_letters = {
            'phi': 'φ', 'theta': 'θ', 'alpha': 'α', 'beta': 'β', 'gamma': 'γ',
            'delta': 'δ', 'epsilon': 'ε', 'mu': 'μ', 'sigma': 'σ', 'lambda': 'λ',
            'omega': 'ω', 'pi': 'π', 'rho': 'ρ', 'tau': 'τ', 'upsilon': 'υ',
            'chi': 'χ', 'psi': 'ψ', 'zeta': 'ζ', 'eta': 'η', 'iota': 'ι',
            'kappa': 'κ', 'nu': 'ν', 'xi': 'ξ', 'omicron': 'ο'
        }
        
        self.math_symbols = {
            'hadamard': '⊙', 'tensor': '⊗', 'assignment': '←', 'element_of': '∈',
            'summation': '∑', 'product': '∏', 'integral': '∫', 'partial': '∂',
            'nabla': '∇', 'infinity': '∞', 'not_equal': '≠', 'less_equal': '≤',
            'greater_equal': '≥', 'subset': '⊂', 'superset': '⊃', 'union': '∪',
            'intersection': '∩', 'empty_set': '∅', 'forall': '∀', 'exists': '∃',
            'implies': '⇒', 'iff': '⇔', 'approximate': '≈', 'proportional': '∝'
        }
        
        # Enhanced patterns that need fixing for better PDF compatibility
        self.fix_patterns = [
            (r'■', ''),  # Remove black squares
            (r'phi\b', 'φ'),  # Replace "phi" text with φ symbol
            (r'theta\b', 'θ'),  # Replace "theta" text with θ symbol
            (r'alpha\b', 'α'),  # Replace "alpha" text with α symbol
            (r'beta\b', 'β'),  # Replace "beta" text with β symbol
            (r'gamma\b', 'γ'),  # Replace "gamma" text with γ symbol
            (r'delta\b', 'δ'),  # Replace "delta" text with δ symbol
            (r'epsilon\b', 'ε'),  # Replace "epsilon" text with ε symbol
            (r'mu\b', 'μ'),  # Replace "mu" text with μ symbol
            (r'sigma\b', 'σ'),  # Replace "sigma" text with σ symbol
            (r'lambda\b', 'λ'),  # Replace "lambda" text with λ symbol
            (r'omega\b', 'ω'),  # Replace "omega" text with ω symbol
            (r'pi\b', 'π'),  # Replace "pi" text with π symbol
            (r'rho\b', 'ρ'),  # Replace "rho" text with ρ symbol
            (r'tau\b', 'τ'),  # Replace "tau" text with τ symbol
            (r'upsilon\b', 'υ'),  # Replace "upsilon" text with υ symbol
            (r'chi\b', 'χ'),  # Replace "chi" text with χ symbol
            (r'psi\b', 'ψ'),  # Replace "psi" text with ψ symbol
            (r'zeta\b', 'ζ'),  # Replace "zeta" text with ζ symbol
            (r'eta\b', 'η'),  # Replace "eta" text with η symbol
            (r'iota\b', 'ι'),  # Replace "iota" text with ι symbol
            (r'kappa\b', 'κ'),  # Replace "kappa" text with κ symbol
            (r'nu\b', 'ν'),  # Replace "nu" text with ν symbol
            (r'xi\b', 'ξ'),  # Replace "xi" text with ξ symbol
            (r'omicron\b', 'ο'),  # Replace "omicron" text with ο symbol
            # Additional mathematical symbol patterns
            (r'hadamard\b', '⊙'),  # Replace "hadamard" with ⊙
            (r'tensor\b', '⊗'),  # Replace "tensor" with ⊗
            (r'assignment\b', '←'),  # Replace "assignment" with ←
            (r'element_of\b', '∈'),  # Replace "element_of" with ∈
            (r'summation\b', '∑'),  # Replace "summation" with ∑
            (r'product\b', '∏'),  # Replace "product" with ∏
            (r'integral\b', '∫'),  # Replace "integral" with ∫
            (r'partial\b', '∂'),  # Replace "partial" with ∂
            (r'nabla\b', '∇'),  # Replace "nabla" with ∇
            (r'infinity\b', '∞'),  # Replace "infinity" with ∞
            (r'not_equal\b', '≠'),  # Replace "not_equal" with ≠
            (r'less_equal\b', '≤'),  # Replace "less_equal" with ≤
            (r'greater_equal\b', '≥'),  # Replace "greater_equal" with ≥
            (r'subset\b', '⊂'),  # Replace "subset" with ⊂
            (r'superset\b', '⊃'),  # Replace "superset" with ⊃
            (r'union\b', '∪'),  # Replace "union" with ∪
            (r'intersection\b', '∩'),  # Replace "intersection" with ∩
            (r'empty_set\b', '∅'),  # Replace "empty_set" with ∅
            (r'forall\b', '∀'),  # Replace "forall" with ∀
            (r'exists\b', '∃'),  # Replace "exists" with ∃
            (r'implies\b', '⇒'),  # Replace "implies" with ⇒
            (r'iff\b', '⇔'),  # Replace "iff" with ⇔
            (r'approximate\b', '≈'),  # Replace "approximate" with ≈
            (r'proportional\b', '∝'),  # Replace "proportional" with ∝
        ]
    
    def format_equation(self, equation: str) -> str:
        """Format an equation to use proper mathematical notation"""
        formatted = equation
        
        # Apply fix patterns
        for pattern, replacement in self.fix_patterns:
            formatted = re.sub(pattern, replacement, formatted, flags=re.IGNORECASE)
        
        # Ensure proper superscript notation
        formatted = self._fix_superscripts(formatted)
        
        # Ensure proper subscript notation
        formatted = self._fix_subscripts(formatted)
        
        # Ensure proper mathematical symbols
        formatted = self._fix_math_symbols(formatted)
        
        # Additional PDF-specific formatting
        formatted = self._fix_pdf_compatibility(formatted)
        
        return formatted
    
    def _fix_superscripts(self, text: str) -> str:
        """Fix superscript notation in equations"""
        # Fix common superscript patterns
        patterns = [
            (r'(\w+)_T\b', r'\1^T'),  # Convert _T to ^T for transpose
            (r'(\w+)_(\d+)\^T', r'\1^\2^T'),  # Fix double superscripts
            (r'(\w+)\^(\w+)_(\w+)', r'\1^\2_\3'),  # Fix mixed superscript/subscript order
            (r'(\w+)_(\w+)\^(\w+)', r'\1_\2^\3'),  # Fix mixed subscript/superscript order
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _fix_subscripts(self, text: str) -> str:
        """Fix subscript notation in equations"""
        # Ensure proper subscript formatting
        patterns = [
            (r'(\w+)_(\w+)', r'\1_\2'),  # Ensure proper subscript formatting
        ]
        
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def _fix_math_symbols(self, text: str) -> str:
        """Fix mathematical symbols in equations"""
        # Replace common text representations with proper symbols
        replacements = {
            'hadamard': '⊙',
            'tensor': '⊗',
            'assignment': '←',
            'element_of': '∈',
            'summation': '∑',
            'product': '∏',
            'integral': '∫',
            'partial': '∂',
            'nabla': '∇',
            'infinity': '∞',
            'not_equal': '≠',
            'less_equal': '≤',
            'greater_equal': '≥',
            'subset': '⊂',
            'superset': '⊃',
            'union': '∪',
            'intersection': '∩',
            'empty_set': '∅',
            'forall': '∀',
            'exists': '∃',
            'implies': '⇒',
            'iff': '⇔',
            'approximate': '≈',
            'proportional': '∝'
        }
        
        for text_symbol, math_symbol in replacements.items():
            text = re.sub(rf'\b{text_symbol}\b', math_symbol, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_pdf_compatibility(self, text: str) -> str:
        """Fix issues specific to PDF rendering"""
        # AGGRESSIVE REMOVAL OF BLACK SQUARES AND CORRUPTED CHARACTERS
        # Remove all variations of black squares and corrupted characters
        black_square_patterns = [
            r'■',  # Standard black square
            r'□',  # White square (sometimes used as placeholder)
            r'▢',  # White square with rounded corners
            r'▣',  # Black square with white square inside
            r'▤',  # Black square with white square inside
            r'▥',  # Black square with white square inside
            r'▦',  # Black square with white square inside
            r'▧',  # Black square with white square inside
            r'▨',  # Black square with white square inside
            r'▩',  # Black square with white square inside
            r'▪',  # Black small square
            r'▫',  # White small square
            r'▬',  # Black rectangle
            r'▭',  # White rectangle
            r'▮',  # Black vertical rectangle
            r'▯',  # White vertical rectangle
            r'▰',  # Black parallelogram
            r'▱',  # White parallelogram
            r'▲',  # Black up-pointing triangle
            r'△',  # White up-pointing triangle
            r'▼',  # Black down-pointing triangle
            r'▽',  # White down-pointing triangle
            r'◆',  # Black diamond
            r'◇',  # White diamond
            r'●',  # Black circle
            r'○',  # White circle
            r'◐',  # Circle with left half black
            r'◑',  # Circle with right half black
            r'◒',  # Circle with lower half black
            r'◓',  # Circle with upper half black
            r'◔',  # Circle with upper right quadrant black
            r'◕',  # Circle with all but upper left quadrant black
            r'◖',  # Left half black circle
            r'◗',  # Right half black circle
            r'◘',  # Inverse bullet
            r'◙',  # Inverse white circle
            r'◚',  # Upper half inverse white circle
            r'◛',  # Lower half inverse white circle
            r'◜',  # Upper left quadrant circular arc
            r'◝',  # Upper right quadrant circular arc
            r'◞',  # Lower right quadrant circular arc
            r'◟',  # Lower left quadrant circular arc
            r'◠',  # Upper half circle
            r'◡',  # Lower half circle
            r'◢',  # Black lower right triangle
            r'◣',  # Black lower left triangle
            r'◤',  # Black upper left triangle
            r'◥',  # Black upper right triangle
            r'◦',  # White bullet
            r'◧',  # Square with left half black
            r'◨',  # Square with right half black
            r'◩',  # Square with upper half black
            r'◪',  # Square with lower half black
            r'◫',  # Square with upper left diagonal half black
            r'◬',  # Square with lower right diagonal half black
            r'◭',  # Square with upper right diagonal half black
            r'◮',  # Square with lower left diagonal half black
            r'◯',  # Large circle
            r'◰',  # White square with upper left quadrant
            r'◱',  # White square with lower left quadrant
            r'◲',  # White square with lower right quadrant
            r'◳',  # White square with upper right quadrant
            r'◴',  # White circle with upper left quadrant black
            r'◵',  # White circle with lower left quadrant black
            r'◶',  # White circle with lower right quadrant black
            r'◷',  # White circle with upper right quadrant black
            r'◸',  # Upper left triangle
            r'◹',  # Upper right triangle
            r'◺',  # Lower left triangle
            r'◻',  # White medium square
            r'◼',  # Black medium square
            r'◽',  # White medium small square
            r'◾',  # Black medium small square
            r'◿',  # Lower right triangle
        ]
        
        # Remove all black squares and corrupted characters
        for pattern in black_square_patterns:
            text = re.sub(pattern, '', text)
        
        # Remove any non-printable characters that might cause issues
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Ensure proper spacing around mathematical symbols
        math_symbols = 'φθαβγδεμσλωπρχψζηικνξο⊙⊗←∈∑∏∫∂∇∞≠≤≥⊂⊃∪∩∅∀∃⇒⇔≈∝'
        for symbol in math_symbols:
            # Add space before symbol if followed by letter
            text = re.sub(rf'([a-zA-Z])({re.escape(symbol)})', r'\1 \2', text)
            # Add space after symbol if followed by letter
            text = re.sub(rf'({re.escape(symbol)})([a-zA-Z])', r'\1 \2', text)
        
        # Fix common mathematical notation issues
        text = re.sub(r'(\w+)_(\w+)\^(\w+)', r'\1_\2^\3', text)  # Ensure proper order: subscript then superscript
        
        # Final cleanup: remove any remaining black squares that might have been missed
        text = re.sub(r'[■□]', '', text)
        
        return text
    
    def validate_equation(self, equation: str) -> Dict[str, any]:
        """Validate an equation for proper mathematical notation"""
        issues = []
        warnings = []
        
        # Check for black squares or corrupted characters
        if '■' in equation:
            issues.append("Equation contains black squares (■) - corrupted characters detected")
        
        # Check for missing superscripts in common patterns
        if re.search(r'\bE\s*[^T]', equation) and 'E^T' not in equation:
            warnings.append("Consider using E^T for transpose notation")
        
        # Check for text-based Greek letters
        for greek_name, greek_symbol in self.greek_letters.items():
            if greek_name in equation.lower() and greek_symbol not in equation:
                warnings.append(f"Consider using {greek_symbol} instead of '{greek_name}'")
        
        # Check for missing mathematical symbols
        if 'hadamard' in equation.lower() and '⊙' not in equation:
            warnings.append("Consider using ⊙ for Hadamard product")
        
        if 'assignment' in equation.lower() and '←' not in equation:
            warnings.append("Consider using ← for assignment operations")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'formatted_equation': self.format_equation(equation)
        }
    
    def get_equation_template(self, equation_type: str) -> str:
        """Get a template for common equation types"""
        templates = {
            'attention': 'E ← E + P W_V E φ((E^T W_K^T W_Q E) ⊙ M)',
            'matrix_multiplication': 'C = A × B',
            'vector_norm': '||v|| = √(v^T v)',
            'gradient_descent': 'θ ← θ - α ∇J(θ)',
            'softmax': 'σ(x)_i = e^(x_i) / ∑_j e^(x_j)',
            'cross_entropy': 'L = -∑_i y_i log(ŷ_i)',
            'convolution': 'y = x ⊗ w',
            'pooling': 'y = max(x_i, x_{i+1}, ..., x_{i+k})',
            'activation': 'f(x) = max(0, x)',
            'regularization': 'L_total = L + λ||θ||²'
        }
        
        return templates.get(equation_type, '')
    
    def format_content_with_equations(self, content: str) -> str:
        """Format all equations in a content string"""
        # Split content into lines
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Check if line contains mathematical content
            if self._is_math_line(line):
                formatted_line = self.format_equation(line)
                formatted_lines.append(formatted_line)
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _is_math_line(self, line: str) -> bool:
        """Check if a line contains mathematical content"""
        math_indicators = [
            '=', '←', '→', '∈', '∑', '∏', '∫', '∂', '∇', '⊙', '⊗',
            'φ', 'θ', 'α', 'β', 'γ', 'δ', 'ε', 'μ', 'σ', 'λ', 'ω', 'π'
        ]
        
        return any(indicator in line for indicator in math_indicators) 