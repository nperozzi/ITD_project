# Electronic Shelf Label (ESL) System

A production-ready IoT system for managing electronic shelf labels in supermarkets, built with Next.js, ESP32/Arduino, and Raspberry Pi.

## 🏗️ System Overview

This system enables real-time price updates for electronic shelf labels across large-scale retail environments. It features:

- **Web Dashboard**: Next.js application for product and label management
- **Gateway Devices**: Raspberry Pi units that coordinate in-store label communication
- **Shelf Labels**: ESP32/Arduino devices with LED displays showing product prices
- **Mobile App**: (Planned) Simplified provisioning and setup workflow

## 📚 Documentation

- **[Architecture Documentation](./docs/architecture.md)** - Comprehensive system architecture with Mermaid diagrams highlighting current implementation and proposed improvements based on teacher feedback
- **[API Documentation](./docs/api-documentation.md)** - REST API endpoints for gateway communication
- **[Hardware Setup Guide](./docs/hardware-setup.md)** - Complete setup instructions for all hardware components
- **[Service Guide](./docs/service-guide.md)** - Code structure and best practices for services
- **[Team Ground Rules](./docs/team_ground_rules.md)** - Team collaboration guidelines

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ or Bun
- Raspberry Pi Pico 2 W (for gateway)
- ESP32 or Arduino Uno R4 WiFi (for labels)

### Installation

```bash
# Install dependencies
bun install

# Setup database
bun db:push

# Start development server
bun dev
```

### First-Time Setup

1. **Create gateway and label serial numbers:**
   ```bash
   bun admin gateway:create 1
   bun admin label:create 1
   ```

2. **Configure and start gateway daemon** (see [Hardware Setup Guide](./docs/hardware-setup.md))

3. **Flash Arduino with label firmware** (see [Hardware Setup Guide](./docs/hardware-setup.md))

4. **Access web dashboard** at `http://localhost:3000`

## 🛠️ Technology Stack

### Backend
- **Framework**: Next.js 15
- **Database**: SQLite/Turso with Drizzle ORM
- **APIs**: REST + tRPC
- **Auth**: Better Auth

### Gateway
- **Hardware**: Raspberry Pi Pico 2 W
- **Language**: Python
- **Communication**: MQTT over TLS, BLE

### Labels
- **Hardware**: ESP32 / Arduino Uno R4 WiFi
- **Communication**: ESP-NOW / BLE Mesh
- **Display**: LED Matrix

## 📋 Available Scripts

```bash
# Development
bun dev              # Start dev server with Turbo
bun build            # Build for production
bun start            # Start production server

# Database
bun db:push          # Push schema changes
bun db:studio        # Open Drizzle Studio
bun db:generate      # Generate migrations
bun db:migrate       # Run migrations

# Admin
bun admin            # Run admin CLI

# Quality
bun lint             # Run ESLint
bun lint:fix         # Fix lint issues
bun typecheck        # Check TypeScript types
bun format:check     # Check code formatting
bun format:write     # Format code
```

## 🏛️ Architecture Highlights

The system follows a resilient, distributed architecture:

- **Gateway-centric design**: Gateways store local state and schedules
- **Offline-capable**: Stores continue functioning even if backend is down
- **Dual gateway redundancy**: Hot failover for high availability
- **Secure communication**: MQTT over TLS, device certificates
- **Scalable**: Designed for thousands of labels per store

See the [Architecture Documentation](./docs/architecture.md) for detailed diagrams and component descriptions.

## 🔧 Teacher Feedback & Improvements

Based on recent teacher feedback, the following improvements are planned:

1. ✅ **Architecture Documentation**: Comprehensive documentation with visual diagrams
2. 🔄 **Mobile Provisioning App**: Simplify setup with QR scanning and local intelligence
3. 🔄 **Local Schedule Storage**: Store discount expiry dates on gateways for offline operation
4. 🔄 **ELK Stack Integration**: Centralized logging and monitoring

See [Architecture Documentation](./docs/architecture.md) for the complete improvement roadmap.

## 📂 Project Structure

```
├── docs/                    # Documentation
├── drizzle/                 # Database migrations
├── public/                  # Static assets
├── scripts/
│   ├── admin.ts            # Admin CLI tool
│   ├── arduino/            # Arduino firmware
│   └── gateway/            # Raspberry Pi gateway code
├── src/
│   ├── app/                # Next.js app router
│   ├── components/         # React components
│   ├── lib/                # Utilities
│   ├── server/             # Server configuration
│   └── services/           # Business logic & tRPC routers
└── tests/                  # Test files
```

## 🤝 Contributing

This is a university project. Please follow the guidelines in [Team Ground Rules](./docs/team_ground_rules.md) and [Service Guide](./docs/service-guide.md) when contributing.

## 📄 License

This project is for educational purposes as part of a university course.
