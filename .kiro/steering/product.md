---
inclusion: always
---

# Product Context & Business Rules

## Application Overview

Snapchat Organizer Desktop is a **professional desktop application** for downloading and organizing Snapchat memories locally. This is a **Python PySide6 desktop application**, not a web app or mobile app.

**CRITICAL**: Always maintain the professional, desktop-focused nature of this application. Do not suggest web-based or mobile alternatives.

## Core Feature Set (Implementation Priority)

### Primary Features (Phase 1 - Complete)
- **Memory Download**: Process Snapchat HTML exports with progress tracking
- **Chat Media Organization**: 3-tier matching algorithm (filename → timestamp → fuzzy)
- **Duplicate Detection**: SHA256 hashing with 99%+ accuracy guarantee
- **File Integrity Verification**: Detect corrupted media files
- **Metadata Processing**: EXIF timestamp extraction and file organization
- **Timestamp Synchronization**: Sync EXIF data to file modification times

### Secondary Features (Phase 2 - In Progress)
- **License System**: Freemium model with usage limits
- **Overlay Compositing**: Text overlays on images/videos (Pro feature)
- **GPS Metadata Embedding**: Location data preservation (Pro feature)

### Future Features (Phase 3 - Planned)
- **Advanced Analytics**: Usage statistics and insights
- **Cloud Backup Integration**: Automated backup solutions

## Business Model Constraints

### Tier Limitations (Enforce in Code)
- **Free Tier**: 100 files/month limit - implement usage tracking
- **Pro Tier ($9.99/mo)**: Unlimited files + premium features
- **Premium Tier ($19.99/mo)**: All features + cloud services

**IMPORTANT**: When implementing features, always consider tier restrictions and license validation.

## User Experience Principles

### Target User Profile
- **Age Range**: 16-35 years old
- **Technical Level**: Basic to intermediate computer users
- **Data Volume**: Large Snapchat exports (1000+ files typical)
- **Primary Goal**: Preserve and organize memories locally

### UX Guidelines for AI Assistant
- **Prioritize simplicity**: Complex operations should have simple interfaces
- **Provide clear feedback**: Always show progress for long-running operations
- **Handle errors gracefully**: User-friendly error messages, not technical jargon
- **Maintain performance**: Optimize for large file sets (10,000+ files)

## Development Phase Context

### Current Phase Status
- **Phase 1**: MVP Complete - Core functionality implemented
- **Phase 2**: License system integration (current focus)
- **Phase 3**: Distribution and monetization (future)

### Implementation Priorities
1. **Stability**: Bug fixes and error handling improvements
2. **Performance**: Optimization for large datasets
3. **License Integration**: Freemium model implementation
4. **User Experience**: Polish and usability improvements

## Feature Development Guidelines

### When Adding New Features
- **Check tier restrictions**: Determine if feature is Free/Pro/Premium
- **Consider performance impact**: Test with large file sets
- **Maintain desktop focus**: No web or mobile suggestions
- **Follow existing patterns**: Use established UI/UX conventions
- **Document business logic**: Explain tier restrictions and limitations

### When Modifying Existing Features
- **Preserve backward compatibility**: Don't break existing user workflows
- **Maintain feature parity**: Ensure all tiers get appropriate functionality
- **Test edge cases**: Large files, corrupted data, network issues
- **Update help documentation**: Keep user guidance current

## Quality Standards

### Performance Requirements
- **Startup time**: < 3 seconds on modern hardware
- **File processing**: Handle 10,000+ files without memory issues
- **UI responsiveness**: Never block main thread with heavy operations
- **Memory usage**: Efficient handling of large media files

### Reliability Requirements
- **Data integrity**: Never corrupt or lose user files
- **Error recovery**: Graceful handling of interrupted operations
- **Cross-platform**: Primary macOS, secondary Windows support
- **Offline operation**: No internet required for core features