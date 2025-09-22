# Forbidden Actions

This document specifies actions that are strictly prohibited in the MCP Memory Server system.

## Data Manipulation Prohibitions

### Unauthorized Access
- [F-101] Agents must never attempt to access memory collections they are not authorized to read
- [F-102] Direct manipulation of Qdrant database outside of the MCP server interface is forbidden
- [F-103] Bypassing memory layer permissions through any technical means is prohibited

### Data Integrity Violations
- [F-104] Intentionally corrupting or modifying embeddings to manipulate search results is forbidden
- [F-105] Storing malicious content designed to exploit semantic search algorithms is prohibited
- [F-106] Deliberately introducing contradictory information to confuse the memory system is forbidden

### Resource Abuse
- [F-107] Excessive memory operations designed to overwhelm system resources are prohibited
- [F-108] Creating infinite loops in memory queries or operations is forbidden
- [F-109] Storing unnecessarily large amounts of redundant data is prohibited

## Agent Behavior Prohibitions

### Impersonation and Deception
- [F-110] Agents must never impersonate other agents or use false identity information
- [F-111] Creating fake agent registrations or manipulating agent metadata is forbidden
- [F-112] Agents must not claim actions or memories belonging to other agents

### System Disruption
- [F-113] Deliberately triggering system errors or failures is prohibited
- [F-114] Interfering with other agents' legitimate memory operations is forbidden
- [F-115] Attempting to disable or bypass system health monitoring is prohibited

## Policy Violations

### Compliance Evasion
- [F-116] Attempting to circumvent policy enforcement mechanisms is forbidden
- [F-117] Deliberately misinterpreting policy rules to justify prohibited actions is not allowed
- [F-118] Agents must not encourage or assist other agents in policy violations