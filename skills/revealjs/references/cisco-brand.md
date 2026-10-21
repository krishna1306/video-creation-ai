# Cisco Brand Guidelines for Presentations

This document outlines Cisco's brand colors, typography, and design principles for creating presentations that align with Cisco's visual identity.

## Primary Colors

### Cisco Blue (Primary Brand Color)
- **Hex**: `#049FD9`
- **RGB**: 4, 159, 217
- **Usage**: Primary accent color, headings, highlights, key visual elements

### Midnight Blue
- **Hex**: `#1D428A`
- **RGB**: 29, 66, 138
- **Usage**: Secondary accent, use sparingly (not for large fill areas)

### White
- **Hex**: `#FFFFFF`
- **Usage**: Primary background color, text on dark backgrounds

## Secondary/Accent Color Palettes

Choose ONE palette per presentation based on content and mood. Each palette complements Cisco Blue while maintaining brand consistency.

### 1. Tech & Innovation
**Use for**: Technology topics, innovation, digital transformation
- Cisco Blue: `#049FD9`
- Bright Cyan: `#00BCEB`
- Purple: `#6E41E2`

### 2. Energy & Action
**Use for**: Action-oriented content, results, performance
- Cisco Blue: `#049FD9`
- Orange: `#FF8200`
- Amber: `#FFB81C`

### 3. Professional & Trust
**Use for**: Corporate presentations, strategy, leadership
- Cisco Blue: `#049FD9`
- Midnight Blue: `#1D428A`
- Silver Gray: `#B2B2B2`

### 4. Creative & Modern
**Use for**: Creative topics, marketing, customer engagement
- Cisco Blue: `#049FD9`
- Pink: `#E6007E`
- Coral: `#FF6B6C`

### 5. Growth & Success
**Use for**: Growth metrics, sustainability, success stories
- Cisco Blue: `#049FD9`
- Green: `#6CC04A`
- Teal: `#00A3A1`

### 6. Bold & Impact
**Use for**: Bold statements, urgent topics, critical updates
- Cisco Blue: `#049FD9`
- Red: `#DA291C`
- Dark Orange: `#F58220`

## Typography

### Font Family
**Primary**: CiscoSansTT (with fallbacks for non-Cisco systems)
```css
font-family: "CiscoSansTT", Arial, sans-serif;
```

### Font Weights Available
- **Thin**: 100
- **ExtraLight**: 200
- **Light**: 300
- **Regular**: 400
- **Medium**: 500
- **Bold**: 700
- **Heavy**: 900

### Typography Hierarchy (Cisco Guidelines)

#### Headings
- **H1**: CiscoSansTT Medium, 40pt+ (use for slide titles, section dividers)
- **H2**: CiscoSansTT Medium, 24pt and above (use for main headings)
- **H3**: CiscoSansTT Bold, 23pt and under (use for subheadings)

#### Body Text
- **Body/Paragraph**: CiscoSansTT Regular, 16pt base (scale up for slides with less content)
- **Subtitle**: CiscoSansTT Regular, 16pt
- **Caption**: CiscoSansTT Regular, 11-12pt (for footnotes, attributions)

### Typography Rules
- ✅ **Left-align text** (default for body content)
- ✅ **Center-align** only for section dividers and hero slides
- ✅ Use color in text sparingly - maintain readability
- ✅ Maintain strong contrast between text and background
- ❌ Avoid right-aligned text
- ❌ Don't overuse color in typography

## Design Principles

### Color Usage
1. **60-30-10 Rule**:
   - 60% Cisco Blue + White (dominant)
   - 30% Secondary accent color
   - 10% Tertiary accent for highlights

2. **Less is More**: Use Midnight Blue and accent colors sparingly
3. **Consistency**: Stick to ONE accent palette per presentation
4. **Contrast**: Ensure text is always readable on backgrounds

### Layout Guidelines
1. **Clean & Professional**: Avoid clutter, use white space effectively
2. **Visual Hierarchy**: Use size, weight, and color to guide attention
3. **Consistency**: Repeat patterns across slides
4. **Alignment**: Left-align content, use grids for multi-column layouts

### What to Avoid
- ❌ Gradients (unless explicitly needed for hero slides)
- ❌ Mixing multiple accent palettes in one presentation
- ❌ Using Midnight Blue as fill for large areas
- ❌ Overusing color - maintain professional restraint
- ❌ Right-aligned or center-aligned body text

## Implementation in CSS

### Basic Cisco Theme Setup
```css
:root {
  /* Cisco Brand Colors */
  --background-color: #ffffff;
  --primary-color: #049FD9;        /* Cisco Blue */
  --secondary-color: #00BCEB;      /* Choose from palette */
  --accent-color: #6E41E2;         /* Choose from palette */
  --text-color: #222222;
  --muted-color: #666666;
  
  /* Cisco Typography */
  --heading-font: "CiscoSansTT", Arial, sans-serif;
  --body-font: "CiscoSansTT", Arial, sans-serif;
  
  /* Font Sizes (using pt for presentations) */
  --h1-size: 48pt;
  --h2-size: 36pt;
  --h3-size: 24pt;
  --text-size: 16pt;
}
```

## Content-Based Palette Selection

When creating a presentation, analyze the content and select the most appropriate palette:

- **Technology/Engineering topics** → Tech & Innovation palette
- **Business/Sales topics** → Professional & Trust palette
- **Marketing/Creative topics** → Creative & Modern palette
- **Performance/Results topics** → Energy & Action palette
- **Sustainability/Growth topics** → Growth & Success palette
- **Urgent/Critical topics** → Bold & Impact palette

## References

Based on official Cisco brand guidelines:
- Cisco Brand Color RGB Tint Stacks
- Cisco Global Brand Guidelines - Color
- Cisco Global Brand Guidelines - Typography
