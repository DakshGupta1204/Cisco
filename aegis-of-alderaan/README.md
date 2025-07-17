# Aegis of Alderaan - Distributed Security Mesh System

**🛡️ Revolutionary AI-Powered Network Security with Lightning-Fast Response**

A distributed security mesh system that deploys intelligent AI agents across your network infrastructure for sub-5-second threat detection and automated response.

## 📁 Project Structure

```
aegis-of-alderaan/
│
├── agent/                       # Intelligent security agents
│   ├── main.py                  # Entry point for agent
│   ├── metrics_collector.py     # Collects system info
│   ├── communicator.py          # WebSocket client
│   ├── jwt_auth.py              # Secure token generation & validation
│   ├── anomaly_detector.py      # Lightweight rule-based or ML detection
│   ├── self_healer.py           # Handles agent recovery / mirroring
│   └── config.yaml              # Hostname, server URL, peer config
│
├── guardian-server/             # Central coordination server
│   ├── app.py                   # FastAPI/Flask server for Guardian
│   ├── models/                  # Data models
│   │   ├── agent.py             # Agent schema
│   │   ├── metrics.py           # Metrics schema
│   │   └── auth.py              # Auth schema
│   ├── db/                      # Database handlers
│   │   ├── mongo_handler.py     # Mongo/Postgres interface
│   │   └── neo4j_handler.py     # Graph DB handler
│   ├── websocket_handler.py     # Manages real-time agent connections
│   ├── remediation_engine.py    # Triggers automated healing actions
│   ├── jwt_utils.py             # JWT utilities
│   └── requirements.txt         # Python dependencies
│
├── dashboard/                   # Next.js admin & peer UI
│   ├── pages/                   # Next.js pages
│   ├── components/              # React components
│   ├── utils/                   # Utility functions
│   └── public/                  # Public assets
│
└── README.md                    # This file
```

## 🚀 Getting Started

1. **Agent Setup**: Configure and deploy intelligent security agents
2. **Guardian Server**: Launch central coordination server
3. **Dashboard**: Start the web-based monitoring interface

## 🎯 Key Features

- **5-second threat detection** vs 15+ minutes traditional
- **AI-powered anomaly detection** with explainable decisions
- **Automated response actions** without human intervention
- **Self-healing network** with agent recovery capabilities
- **Real-time dashboard** with network topology visualization

## 📋 Development Status

**Current Phase**: Initial project structure setup
**Next Steps**: Implement core agent functionality and communication protocols

---

*For detailed documentation, see the parent directory's comprehensive project documentation.*
