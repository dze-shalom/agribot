# PWA Icons Required

The PWA manifest requires the following icon sizes. You can use any tool to generate these from your logo:

## Required Sizes:
- icon-16x16.png (favicon)
- icon-32x32.png (favicon)
- icon-72x72.png
- icon-96x96.png
- icon-128x128.png
- icon-144x144.png
- icon-152x152.png
- icon-180x180.png (Apple touch icon)
- icon-192x192.png (Android)
- icon-384x384.png
- icon-512x512.png (Android splash)

## Tools to Generate Icons:

### Option 1: Online Tools (Easiest)
- https://realfavicongenerator.net/ - Upload your logo, generates all sizes
- https://favicon.io/ - Free favicon generator
- https://www.pwabuilder.com/ - PWA icon generator

### Option 2: ImageMagick (Command line)
```bash
# Convert your logo to all required sizes
convert company-logo.png -resize 16x16 icon-16x16.png
convert company-logo.png -resize 32x32 icon-32x32.png
convert company-logo.png -resize 72x72 icon-72x72.png
convert company-logo.png -resize 96x96 icon-96x96.png
convert company-logo.png -resize 128x128 icon-128x128.png
convert company-logo.png -resize 144x144 icon-144x144.png
convert company-logo.png -resize 152x152 icon-152x152.png
convert company-logo.png -resize 180x180 icon-180x180.png
convert company-logo.png -resize 192x192 icon-192x192.png
convert company-logo.png -resize 384x384 icon-384x384.png
convert company-logo.png -resize 512x512 icon-512x512.png
```

### Option 3: Python Script
```python
from PIL import Image

sizes = [16, 32, 72, 96, 128, 144, 152, 180, 192, 384, 512]
logo = Image.open('company-logo.png')

for size in sizes:
    resized = logo.resize((size, size), Image.Resampling.LANCZOS)
    resized.save(f'icon-{size}x{size}.png')
```

## Screenshots (Optional but recommended)
- screenshot-mobile.png (540x720) - Mobile view
- screenshot-desktop.png (1280x720) - Desktop view

## Temporary Solution
For now, the app will work without icons, but installation prompts won't show.
You can add icons later without breaking functionality.
