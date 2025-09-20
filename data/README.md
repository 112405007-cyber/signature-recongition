# Data Directory

This directory contains data files for the Signature Recognition System.

## Structure

```
data/
├── templates/          # User signature templates
├── test_signatures/    # Test signature images
└── README.md          # This file
```

## Templates Directory

The `templates/` directory stores user signature templates that are used for comparison and verification. Each template includes:

- Original signature image
- Extracted features (JSON format)
- Metadata (creation date, user info, etc.)

## Test Signatures Directory

The `test_signatures/` directory contains sample signature images for testing and development purposes. These can be used to:

- Test the signature analysis algorithms
- Validate feature extraction
- Benchmark system performance
- Train machine learning models

## File Formats

Supported image formats:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

## Security Note

- Never commit real user signatures to version control
- Use test data only for development and testing
- Ensure proper access controls for production data
- Consider encryption for sensitive signature data

## Usage

1. **Adding Test Data**: Place test signature images in `test_signatures/`
2. **Template Storage**: Templates are automatically stored in `templates/` when users save signatures
3. **Data Backup**: Regularly backup the data directory in production environments
