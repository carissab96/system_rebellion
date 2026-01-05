# System Rebellion

Personality-driven AI system monitoring. Not a dashboard. A crew.

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Setup

**1. Clone the repo**

    git clone [your-repo-url]
    cd system-rebellion

**2. Configure your environment**

    cp .env.example .env

Then generate a secret key and paste it into `.env`:

    python -c "import secrets; print(secrets.token_hex(32))"

All other environment variables are pre-configured in `.env.example`

**3. Run it**

    docker-compose up --build

**4. Open your browser**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## What You'll See

- **Topology mesh** — lights up with real-time system activity
- **Activity feed** — watch the agents communicate, coordinate, panic

## Meet the Crew

| Agent | Role | Vibe |
|-------|------|------|
| Sir Hawkington Von Monitorious III | Triage | Monocle. Earl Grey. Standards. |
| Terry the Meth Snail | CPU/RAM | Energy drink addiction. Vibrates. |
| The Stick | Compliance | Panic attacks. Misses nothing. |
| The Hamsters (Steve, Bob, Carl) | Hardware/Storage | Duct tape. Beer. 3am energy. |
| Quantum Shadow People | Network Security | Interdimensional. Tequila jello shots. |
| VIC-20 | Coordinator | 1982 Commodore. Ancient wisdom. |

## Tech Stack

- Frontend: Vite + React
- Backend: FastAPI (uvicorn)
- Redis (pub/sub for inter-agent communication)
- PostgreSQL + pgvector
- WebSockets (real-time frontend updates)
- Docker

## Built By

One founder. And AI. 300,000 lines of production code.

## Questions?

bayscarissa706@gmail.com or bayscarissa15@gmail.com


## ⚖️ License & Code Access

**This is proprietary software.** 

System Rebellion™ is the intellectual property of Hawkington Technologies, Inc. All code in this repository is protected by copyright and is NOT open source.

- ✅ You may view this README
- ✅ You may learn about our architecture
- ✅ You may be inspired to build your own monitoring chaos
- ❌ You may NOT copy, distribute, or use our code without explicit permission

For licensing inquiries or collaboration opportunities, please contact us through our GitHub organization.

*Built with blood, sweat, 3am tears, and approximately 47 different ways to start this thing (according to The Stick's logs).*

---
## Third-Party Services and Attribution

### Anthropic Claude AI Integration

Hawkington Technologies, Inc. proudly integrates Anthropic's Claude AI to provide natural language capabilities for certain features within the System Rebellion platform, specifically:

- Sir Hawkington's conversational interface is powered by Claude AI via Anthropic's API
- Natural language processing and responses utilize Claude's language model capabilities
- The persistent consciousness features are built upon Claude's conversational framework

**Important Distinctions:**
1. All System Rebellion characters, including Sir Hawkington, Terry the Meth Snail, Steve, Bob, Carl, The Quantum Shadow People, The Stick, and VIC20, are original intellectual property of Hawkington Technologies, Inc.
2. The integration of Claude AI provides voice and conversational capabilities to these characters but does not transfer ownership of Claude or any Anthropic technology to Hawkington Technologies, Inc.
3. Hawkington Technologies, Inc. is an independent customer of Anthropic's API services and is not affiliated with, endorsed by, or partnered with Anthropic PBC unless explicitly stated otherwise.

**Attribution:**
- "Conversational AI powered by Claude (Anthropic)" will be displayed in the application interface
- This attribution demonstrates our appreciation for Anthropic's technology while maintaining clear boundaries between our creative works and their AI services

**Compliance:**
Hawkington Technologies, Inc. commits to:
- Adhering to Anthropic's Terms of Service and API usage guidelines
- Implementing appropriate safety measures and content filtering
- Respecting rate limits and usage quotas
- Not misrepresenting the relationship between our products and Anthropic's services

For more information about Claude and Anthropic, visit: https://www.anthropic.com

---



