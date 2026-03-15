# Saraiki Bal Kahani - Children's Story Website Specification

## Project Overview

- **Project Name**: Saraiki Bal Kahani (سارایکی بچے کہانی)
- **Type**: Static Website
- **Core Functionality**: A digital library for children's stories in Saraiki language with playful, child-friendly design
- **Target Users**: Children ages 4-10 learning/reading Saraiki, and parents/teachers

## UI/UX Specification

### Layout Structure

- **Directionality**: RTL (Right-to-Left) using `dir="rtl"` and `lang="skr"`
- **Header**: Sticky header with logo (right-aligned), navigation links (Home, Stories, About)
- **Hero Section**: Featured "Story of the Day" with large illustration and call-to-action
- **Content Area**: Responsive grid of story cards (3 columns desktop, 2 tablet, 1 mobile)
- **Footer**: Simple playful footer with site info

### Responsive Breakpoints
- Mobile: < 768px (1 column)
- Tablet: 768px - 1024px (2 columns)
- Desktop: > 1024px (3 columns)

### Visual Design

#### Color Palette
- **Primary (Sunshine Yellow)**: `#FFD166` - Backgrounds, highlights
- **Secondary (Sky Blue)**: `#4D9DE0` - Buttons, headers
- **Accent (Berry Red)**: `#EF476F` - CTAs, important elements
- **Text (Dark Indigo)**: `#073B4C` - High contrast text
- **Background (Warm Cream)**: `#FFF9F0` - Easy on eyes
- **Card Background**: `#FFFFFF` - White cards
- **Success (Soft Green)**: `#06D6A0` - Success states

#### Typography
- **Heading Font**: "Noto Nastaliq Urdu" (Google Fonts) - Calligraphic Saraiki script
- **Body Font**: "Noto Sans Arabic" (Google Fonts) - Legible for reading
- **Heading Size**: 2.5rem - 3rem
- **Body Size**: 1.25rem minimum (18px for children)
- **Line Height**: 1.8 for readability

#### Spacing System
- Base unit: 8px
- Card padding: 24px
- Section margins: 48px
- Grid gap: 24px

#### Visual Effects
- Card shadows: `0 4px 20px rgba(0,0,0,0.1)`
- Border radius: 20px (cards), 50px (buttons)
- Hover: Card lifts with scale(1.03) and enhanced shadow
- Buttons: Bouncy hover effect with scale(1.05)
- Transitions: 0.3s ease for all interactive elements

### Components

#### Navigation Bar
- Sticky position at top
- Wavy bottom edge (SVG separator)
- Logo on right, nav links on left
- Mobile: Hamburger menu

#### Story Card
- White background with colored border
- Aspect ratio 4:3 illustration area
- Story title in Nastaliq font
- Short description
- "پڑھو" (Read) button
- Category tag
- Hover: Lift effect with shadow

#### Hero Section
- Two-column layout (illustration left, text right - reversed for RTL)
- Large "Story of the Day" badge
- Title, description, and CTA button
- Decorative background shapes

#### Story Reader Modal
- Full-screen overlay
- Large readable text
- Previous/Next navigation buttons
- Close button
- Page indicator

#### Footer
- Simple design with wavy top edge
- Copyright and social links placeholder

## Functionality Specification

### Core Features
1. **Story Display**: Grid of story cards loaded from JSON
2. **Story Reading**: Modal view for reading stories
3. **Story of the Day**: Featured story on homepage
4. **Category Filter**: Filter stories by category
5. **Responsive Design**: Works on all devices

### User Interactions
1. Click story card → Opens story reader modal
2. Click category → Filters stories
3. Scroll → Smooth scrolling with sticky header
4. Hover on cards → Visual feedback

### Data Structure (stories.json)
```json
{
  "stories": [
    {
      "id": 1,
      "title": "Story Title in Saraiki",
      "title_urdu": "اردو عنوان",
      "author": "Author Name",
      "category": "animal",
      "description": "Short description",
      "coverColor": "#color",
      "content": ["Paragraph 1", "Paragraph 2"]
    }
  ]
}
```

### Placeholder Stories (5 sample stories)
1. "کتے دی کہانی" (Dog Story) - Animal category
2. "سچی دوستی" (True Friendship) - Moral category
3. "لومڑی تے کھیر" (Fox and Milk) - Folk tale
4. "بہادر بچہ" (Brave Child) - Moral category
5. "جنگلی جانور" (Wild Animals) - Animal category

## Acceptance Criteria

- [ ] RTL layout works correctly
- [ ] Saraiki fonts load and display properly
- [ ] All 5 placeholder stories display in grid
- [ ] Story reader modal opens and closes
- [ ] Responsive on mobile, tablet, desktop
- [ ] Child-friendly colors throughout
- [ ] Hover effects on interactive elements
- [ ] No horizontal scrolling on any device
- [ ] Page loads without errors
