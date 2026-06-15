# AjiTkhdem 🚀
### Distributed Microservices-Based Job Automation Platform
---

## 📋 Executive Summary

**AjiTkhdem** is a production-ready, highly distributed job application automation platform designed to streamline the modern job hunt. Built using an asynchronous, event-driven microservices architecture, the system provides automated high-throughput job scraping, intelligent AI-powered profile matching, contextual resume/cover letter tailoring, and headless browser automation to execute end-to-end job applications seamlessly across multiple job boards.

### ⚡ Tier Status Breakdown
* **Foundation Tier:** Fully operational core data ingestion, normalization, and structural pre-processing pipelines.
* **Core Service Tier:** Advanced processing engines covering Semantic AI Matching, Multipart CV Management, and Headless Execution Automation.
* **Integration Tier:** Decoupled cross-service communication via Apache Kafka event streaming, centralized API Gateway orchestration, and live WebSocket telemetry mapping to a modern front-end dashboard.

---

## 🏗️ 1. Architecture & System Topography

The system strictly adheres to cloud-native microservices architecture principles. Services are fully decoupled, maintain their own dedicated storage engines (Polyglot Persistence), and communicate asynchronously via an event backbone or through a centralized API Gateway.

### 1.1 Architectural Compliance Matrix

| Component | Design Pattern / Core Responsibility | Status | Compliance |
| :--- | :--- | :--- | :--- |
| **API Gateway / Reverse Proxy** | Centralized entry point, JWT authentication decryption, rate limiting, and global request routing. | ✅ Implemented | Full |
| **Event Backbone (Kafka)** | Asynchronous, decoupled message broker orchestrating data pipeline and execution events. | ✅ Operational | Full |
| **State Management (Multi-DB)** | Polyglot persistence tailored to the data needs of individual microservices. | ✅ Operational | Full |
| **Service Isolation** | Strictly independent deployment bounds, preventing cascading system failures. | ✅ Implemented | Full |
| **DevOps (Docker & CI/CD)** | Multi-stage container builds, ephemeral environment test orchestration, and automated CD. | ✅ Operational | Full |

### 1.2 System Topology Diagram

```
                       [ React 19 Frontend Dashboard ]
                                      │
                         (REST / WebSockets Telemetry)
                                      │
                        ▼                     ▼
             [ API Gateway (Nginx) ] ──(Auth)──► [ Redis Cache ]
                       │
         ┌─────────────┼─────────────┬─────────────┐
         ▼             ▼             ▼             ▼
   ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
   │ Ingestion │ │Normaliz'n │ │Pre-Process│ │Profile/CV │
   │  Service  │ │  Service  │ │  Service  │ │  Service  │
   └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
         │             │             │             │
   (Redis Dedupe) (PostgreSQL)   (MongoDB)     (S3/Storage)
         │             │             │             │
         └─────────────┼─────────────┴─────────────┘
                       ▼
             [ Apache Kafka Event Bus ]
                       ▲
         ┌─────────────┴─────────────┐
         ▼                           ▼
   ┌───────────┐               ┌───────────┐
   │ AI Match  │ ◄──(GenAI)──► │Auto-Apply │ ──(Playwright)──► [ Job Boards ]
   │  Engine   │               │  Service  │
   └───────────┘               └───────────┘
```

---

## 🛠️ 2. Microservices Deep Dive

### 📦 Service 1: Data Pipeline - Ingestion
Responsible for high-frequency concurrent document extraction from targeted external platforms.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * `IndeedScraper.py` & `RekruteScraper.py`: Headless browser workers utilizing Playwright clustering.
  * **Proxy Rotation Engine:** Active middleware preventing IP throttling.
  * **Anti-Bot Layer:** Advanced fingerprint obfuscation to bypass infrastructure challenges (Cloudflare/Datadome).
  * **Redis Caching Layer:** Employs atomic deduplication hashing on raw text/URL signatures to block duplicate writes.
  * **APScheduler Integration:** Cron-based orchestration handling scheduling policies for worker scraping cycles.
* **Design Patterns:** * *Strategy Pattern:* Dynamically hot-swaps scraper configurations based on target platforms.
  * *Producer Pattern:* Emits raw un-sanitized extraction payload blocks directly onto Kafka ingestion topics.

### 📦 Service 2: Data Pipeline - Normalization
Consumes raw streams, resolving unstructured formatting into strict relational constructs.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * **FastAPI REST Application:** Light, high-performance exposure layer for data reads.
  * **Kafka Consumer Framework:** Multi-threaded stream ingestion workers.
  * **PostgreSQL Integration:** Powered by SQLAlchemy Core and Alembic migrations.
  * **Data Transformation Engine:** Enforces validation schemes, normalizes missing attributes (e.g., matching salary brackets, parsing relative dates), and standardizes localized strings.
* **Design Patterns:**
  * *Data Transfer Object (DTO):* Strictly isolates external-facing presentation schemas from internal ingestion models.
  * *Repository Pattern:* Abstracts low-level SQL execution routines behind clean transaction interfaces.

### 📦 Service 3: Data Pipeline - Pre-Processing
Handles heavy text sanitization, structural analysis, and raw data archiving.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * **MongoDB Connection Engine:** Manages atomic document operations on dynamic BSON structures.
  * **Kafka Pipeline Router:** Orchestrates conditional message forwarding based on parsed properties.
  * **Parser Factory Infrastructure:**
    * `IndeedParser` & `RekruteParser`: Deep structural DOM extractors parsing raw layouts.
    * **HTML Sanitizer Suite:** Stems boilerplate text, strips malicious scripts, and flattens nested layout components.
* **Capabilities:** Persists raw tracking artifacts within a document store for historical analysis before executing downstream event signaling.
* **Design Patterns:**
  * *Factory Pattern:* Instantiates isolated parser runtimes conditionally mapped to the job source.

### 📦 Service 4: Profile & CV Management Service
Ingests user identity documents, maintaining a unified representation of professional profiles.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * **Storage Manager:** Secure Object/S3 wrapper for physical file isolation (Resumes, Cover Letters).
  * **File Parser Component:** Extracts structural content sections from binary payloads (`.pdf`, `.docx`).
  * **Profile Aggregator Engine:** Exposes REST interfaces to construct unified representation schemas.
  * **Multi-part Form Gateway:** Secure upload stream handler validating binary signatures and MIME types.
* **Design Patterns:**
  * *Strategy Pattern:* Dynamically alternates file analysis parser algorithms based on document extensions.

### 📦 Service 5: AI Match & Optimization Engine
Calculates profile compliance vectors and triggers contextual generative enrichment.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * **Semantic Scoring Module:** Computes cosine similarity scores over dense vector embeddings of job descriptions and candidate CVs.
  * **Google GenAI SDK (LLM Core Engine):** Direct programmatic integration with advanced frontier LLMs.
  * **Tailoring Agent System:** Highly engineered prompting structures that dynamically rewrite target bullet points and write hyper-tailored, job-specific cover letters.
* **Design Patterns:**
  * *Facade Pattern:* Structural abstraction hiding multi-step LLM completion logic behind clear, single-method system hooks.
  * *Singleton Pattern:* Manages stateful client connections and token buckets for the downstream GenAI SDK contexts.

### 📦 Service 6: Auto-Apply & Execution Service
The operational automation arm designed to simulate browser-based application steps.
* **Status:** `Production Ready` | **Integration:** `Fully Connected`
* **Core Components:**
  * **Application Coordinator:** Monitors system states and routes job execution events.
  * **Browser Automation Cluster:** Highly parameterized headless configurations driving Playwright to fill forms, upload tailored documents, and answer contextual questions.
  * **Status Tracker & Webhook Broadcaster:** Pushes live multi-stage application traces down to communication pipes.
* **Design Patterns:**
  * *State Pattern:* Governs full application tracking loops through structured states: `Draft` ➔ `Processing` ➔ `Submitted` / `Failed`.
  * *Command Pattern:* Encapsulates contextual operations into concrete job tasks, enabling out-of-the-box support for message retries, failures, and back-offs.

---

## 💻 3. Frontend Architecture & Service Mapping

### 3.1 Technology Stack
* **Core UI Framework:** React 19.0.1, TypeScript, Vite
* **Styling & Motion:** Tailwind CSS, Framer Motion animations
* **BFF / Layering:** Node.js, Express, Prisma ORM

### 3.2 Live Production Data Mappings

The user interface operates with 100% active data pipes without mock endpoints:

| Frontend Dashboard Module | Connected Backend Microservice | Communication Protocol | Production Telemetry |
| :--- | :--- | :--- | :--- |
| **Job Browse & Search** | Data Pipeline - Normalization | REST API (Read-Optimized Pools) | Active |
| **Resume Builder & Profile** | Profile & CV Management Service | Multipart REST / Object Stream | Active |
| **Match Analysis View** | AI Match & Optimization Engine | Asynchronous Async Engine + Vector Compute | Active |
| **Auto-Apply Dashboard** | Auto-Apply & Execution Service | Bi-Directional WebSockets Event Stream | Active |
| **Metrics & Analytics** | Central API Gateway Aggregator | Event-Driven Streaming Pipelines | Active |

---

## 🔄 4. CI/CD Pipeline & DevOps Engineering

Automated pipelines are fully configured using **GitHub Actions**, validating branch updates across development and production targets:

```
[ Git Push / PR ] ──► [ Linting & Static Analysis ] ──► [ Ephemeral Service Containers ]
                                                                   │
                                                        (Pytest / Integration Testing)
                                                                   │
[ Automated CD ] ◄── [ Multi-Stage Docker Build ] ◄────────────────┘
```

* **Ingestion Suite:** Triggers Python 3.11 environment setups, checks formatting compliance, and executes `pytest` validation blocks.
* **Normalization Suite:** Spins up ephemeral, short-lived Docker network instances containing transient **PostgreSQL** and **Kafka** topologies to pass full functional data transaction assertions.
* **Pre-Processing Suite:** Evaluates document persistence and operational mapping strategies within independent transient **MongoDB** containers.
* **Business Logic Core (CV, AI, Apply):** Enforces 100% compilation safety and unit validation on file transfers, similarity matrices, and state changes.
* **Frontend Workflow:** Processes Vite production builds, validates schema consistency, and evaluates bundle size metrics.
* **Containerization Strategy:** Fully implements multi-stage Docker configurations, generating lean, secure production layers stripped of build-time dependencies, and ships images directly into the internal container registry.

---

## 🗄️ 5. Production Database Topology

The platform leverages **Polyglot Persistence** to optimize data modeling based on access patterns:

* **PostgreSQL:** Handles strongly consistent, highly relational business data structures.
  * *Core Tables:* `Job`, `Enterprise`, `SourcePlatform`, `ApplyMethod`, `ApplicationHistory`.
* **MongoDB:** Serves as a flexible document archive for raw, unstructured web scraping outputs.
  * *Core Collections:* `RawScrapingPayloads`, `PlatformConfigurations`, `ArchivedJobPostings`.
* **Redis:** High-speed in-memory store for execution state management and rapid caching.
  * *Key Spaces:* `DeduplicationHashes` (Scraper pipeline), `SessionTokens` (Gateway auth), `LiveApplicationStates`.

---

## 🛡️ 6. Universal Architectural Enforcement

1. **Observer Pattern via WebSockets:** Real-time pipelines bridge the gap between headless workers in the `Auto-Apply Service` and the user interface. Progress logs, execution screenshots, and input prompts are streamed dynamically without periodic client polling.
2. **Dependency Injection (DI):** Core business code remains completely isolated from third-party client protocols, database drivers, and messaging layers, enabling easy mocking and independent unit testing.
3. **Gateway Security Architecture:** The edge layer implements centralized token-based **JWT decryption**, strict rate-limiting, and payload validation, meaning internal microservices can fully trust the integrity of down-stream requests.

---

## 🎯 7. Conclusion

**AjiTkhdem** has successfully transitioned from an architectural concept into a robust, enterprise-grade, distributed microservices platform. By decoupling ingestion data pipelines through **Apache Kafka**, utilizing tailored storage engines via **Polyglot Persistence**, and implementing advanced **LLM orchestration** alongside headless browser clusters, the platform achieves full automation of the end-to-end job application lifecycle.

The system is highly maintainable, thoroughly tested via rigorous automated **CI/CD pipelines**, and entirely prepared for production deployment.

OUSSAMA LAKHDAR
AMINE MOUFAKKIR
