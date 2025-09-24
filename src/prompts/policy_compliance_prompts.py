"""
Policy compliance prompt handlers for MCP Memory Server.
Handles policy compliance guidance, violation recovery, and checklist prompts.
"""

from datetime import datetime
from typing import Dict, Any

try:
    from ..server_config import get_logger
except ImportError:
    import logging

    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("policy-compliance-prompts")


class PolicyCompliancePrompts:
    """Handles policy compliance and governance guidance prompts."""

    def __init__(self):
        """Initialize policy compliance prompts handler."""
        pass

    def get_prompt_definitions(self) -> list[dict]:
        """Get definitions for policy compliance prompts."""
        return [
            {
                "name": "final_checklist",
                "description": (
                    "Pre-finalization policy compliance checklist"
                ),
                "arguments": []
            },
            {
                "name": "policy_compliance_guide",
                "description": (
                    "Comprehensive guide for following the policy rulebook"
                ),
                "arguments": []
            },
            {
                "name": "policy_violation_recovery",
                "description": (
                    "Recovery procedures when policy conflicts arise"
                ),
                "arguments": []
            }
        ]

    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get a policy compliance prompt by name."""
        method_map = {
            "final_checklist": self._get_final_checklist_prompt,
            "policy_compliance_guide": self._get_policy_compliance_guide_prompt,
            "policy_violation_recovery": 
                self._get_policy_violation_recovery_prompt
        }

        if name in method_map:
            return method_map[name]()
        else:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Unknown policy compliance prompt: {name}"
                    }
                ]
            }

    def _get_final_checklist_prompt(self) -> Dict[str, Any]:
        """Pre-finalization policy compliance checklist."""
        content = """# Final Checklist - Policy Compliance

## Pre-Finalization Verification

### 1. Data Integrity Checks
- [ ] **Content Validation**
  - All stored content is accurate and complete
  - No corrupted or malformed data detected
  - Content metadata is properly populated
  - File references and links are valid

- [ ] **Deduplication Verification**
  - Duplicate content scan completed
  - Near-duplicates reviewed and resolved
  - Content consolidation performed where appropriate
  - Deduplication logs reviewed and approved

### 2. Memory Type Compliance
- [ ] **Global Memory Validation**
  - Only shared, authoritative content stored
  - All global content follows documentation standards
  - No personal or temporary information present
  - Content is accessible to all authorized agents

- [ ] **Learned Memory Validation**
  - Contains patterns, insights, and best practices
  - No raw data or personal information
  - Knowledge is properly abstracted and generalized
  - Content represents validated learning outcomes

- [ ] **Agent Memory Validation**
  - Personal and task-specific content appropriately segregated
  - No sensitive information stored without encryption
  - Agent-specific content properly isolated
  - Temporary information tagged for cleanup

### 3. Access Control Verification
- [ ] **Permission Matrix Review**
  - Agent roles properly configured
  - Memory layer access rights validated
  - No unauthorized access permissions granted
  - Admin access properly restricted and logged

- [ ] **Security Compliance**
  - Sensitive data handling follows policy
  - Encryption applied where required
  - Access logs properly maintained
  - Authentication mechanisms validated

### 4. Quality Assurance
- [ ] **Content Quality Standards**
  - All content meets minimum quality thresholds
  - Metadata is comprehensive and accurate
  - Tagging is consistent and meaningful
  - Search functionality works as expected

- [ ] **System Performance**
  - Query response times within acceptable limits
  - Memory usage within operational parameters
  - No performance bottlenecks identified
  - System health metrics all green

### 5. Documentation and Audit Trail
- [ ] **Process Documentation**
  - All processing steps documented
  - Decision rationales recorded
  - Exception handling properly documented
  - Change history maintained

- [ ] **Compliance Evidence**
  - Policy adherence demonstrated
  - Audit trail complete and verifiable
  - Review checkpoints documented
  - Sign-off processes completed

## Policy Specific Checks

### Data Governance
- [ ] Data classification completed and accurate
- [ ] Retention policies properly applied
- [ ] Privacy requirements satisfied
- [ ] Regulatory compliance verified

### Operational Excellence
- [ ] Monitoring and alerting configured
- [ ] Backup and recovery procedures validated
- [ ] Disaster recovery plans updated
- [ ] Performance baselines established

### Security Requirements
- [ ] Security controls implemented and tested
- [ ] Vulnerability assessments completed
- [ ] Incident response procedures updated
- [ ] Security training requirements met

## Final Approval Process

### Technical Review
- [ ] System architecture reviewed by technical lead
- [ ] Code quality standards met
- [ ] Security review completed
- [ ] Performance testing passed

### Business Review
- [ ] Business requirements fully satisfied
- [ ] Stakeholder acceptance obtained
- [ ] User acceptance testing completed
- [ ] Training materials prepared

### Governance Review
- [ ] Policy compliance verified by governance team
- [ ] Risk assessment completed and approved
- [ ] Change management process followed
- [ ] Final approval from authorized signatory

## Post-Finalization Requirements

### Deployment Readiness
- [ ] Production environment prepared
- [ ] Deployment procedures tested
- [ ] Rollback procedures validated
- [ ] Support team notified and trained

### Ongoing Monitoring
- [ ] Monitoring dashboards configured
- [ ] Alerting thresholds set appropriately
- [ ] Regular review schedule established
- [ ] Continuous improvement process defined

## Checklist Completion

**Final Verification:**
- [ ] All checklist items completed
- [ ] No outstanding issues or exceptions
- [ ] Required approvals obtained
- [ ] System ready for production deployment

**Sign-off Required:**
- Technical Lead: _________________ Date: _______
- Security Officer: ________________ Date: _______
- Governance Lead: ________________ Date: _______
- Project Manager: ________________ Date: _______

---
*This checklist ensures comprehensive policy compliance before finalization*"""

        return {
            "status": "success",
            "prompt": {
                "name": "final_checklist",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }

    def _get_policy_compliance_guide_prompt(self) -> Dict[str, Any]:
        """Comprehensive guide for following the policy rulebook."""
        content = """# Policy Compliance Guide

## Understanding the Policy Framework

### Policy Hierarchy
1. **Core Policies:** Fundamental rules that cannot be violated
2. **Operational Policies:** Guidelines for day-to-day operations
3. **Best Practice Policies:** Recommended approaches and methods
4. **Context-Specific Policies:** Rules for specific situations or domains

### Policy Application Principles
- **Mandatory Compliance:** Core policies must always be followed
- **Justified Exceptions:** Operational policy exceptions require docs
- **Continuous Improvement:** Best practices evolve based on experience
- **Context Awareness:** Apply appropriate policies for each situation

## Memory System Policy Compliance

### 1. Data Classification and Storage
```
Policy: Store data in appropriate memory types based on classification

Implementation:
✅ Global: Shared, authoritative, reference material
✅ Learned: Patterns, insights, validated knowledge
✅ Agent: Personal, task-specific, temporary information

Validation:
- Review content classification before storage
- Verify memory type selection rationale
- Document any exceptions or edge cases
```

### 2. Access Control and Permissions
```
Policy: Ensure appropriate access controls for each memory layer

Implementation:
✅ Role-based access control (RBAC) implemented
✅ Principle of least privilege applied
✅ Regular access review and validation
✅ Admin access properly restricted and logged

Validation:
- Audit agent permissions quarterly
- Review access logs for anomalies
- Test access controls regularly
- Document access decisions
```

### 3. Data Quality and Integrity
```
Policy: Maintain high data quality and prevent corruption

Implementation:
✅ Content validation before storage
✅ Deduplication processes active
✅ Metadata accuracy verification
✅ Regular integrity checks

Validation:
- Monitor data quality metrics
- Perform random content audits
- Validate search functionality
- Review error logs regularly
```

## Operational Compliance Procedures

### Daily Operations
1. **Morning Checklist**
   - [ ] System health check completed
   - [ ] Security alerts reviewed
   - [ ] Performance metrics within normal ranges
   - [ ] Backup status verified

2. **Content Processing**
   - [ ] Memory type selection follows policy guidelines
   - [ ] Deduplication checks performed
   - [ ] Quality validation completed
   - [ ] Metadata properly populated

3. **Evening Review**
   - [ ] Processing logs reviewed
   - [ ] Any exceptions documented
   - [ ] Performance issues addressed
   - [ ] Next-day priorities set

### Weekly Reviews
- **Policy Adherence Review:** Assess week's compliance
- **Exception Analysis:** Review and categorize policy exceptions
- **Performance Analysis:** Check system performance trends
- **Security Review:** Validate security controls and logs

### Monthly Audits
- **Comprehensive Compliance Audit:** Full policy adherence review
- **Access Rights Review:** Validate all agent permissions
- **Data Quality Assessment:** Comprehensive quality metrics review
- **Policy Update Review:** Assess need for policy updates

## Exception Handling

### When Exceptions Are Acceptable
- **Technical Limitations:** Current technology cannot support policy
- **Business Critical Need:** Immediate business need overrides policy
- **Temporary Workaround:** Short-term solution while permanent fix
- **Emergency Situation:** Policy compliance would prevent crisis response

### Exception Documentation Process
```
Exception Request:
1. Identify specific policy being violated
2. Provide detailed justification
3. Assess risk and impact
4. Define mitigation measures
5. Set review and expiration dates
6. Obtain required approvals
7. Document in exception register
```

### Exception Monitoring
- **Regular Review:** All exceptions reviewed monthly
- **Risk Assessment:** Ongoing risk evaluation for active exceptions
- **Remediation Tracking:** Progress toward policy compliance
- **Exception Closure:** Formal closure when compliance achieved

## Compliance Monitoring

### Key Performance Indicators (KPIs)
- **Policy Adherence Rate:** Percentage of operations in compliance
- **Exception Rate:** Number of active policy exceptions
- **Resolution Time:** Time to resolve compliance issues
- **Training Completion:** Staff policy training completion rate

### Monitoring Tools
- **Automated Checks:** System-automated compliance monitoring
- **Manual Audits:** Regular manual verification processes
- **User Reporting:** Mechanism for users to report compliance issues
- **Third-Party Assessment:** External compliance verification

## Training and Awareness

### Required Training
- **New User Orientation:** Policy overview for all new users
- **Role-Specific Training:** Specialized training for different roles
- **Annual Refresher:** Yearly policy update and refresher training
- **Exception Handling:** Training on proper exception procedures

### Awareness Programs
- **Policy Updates:** Communication of policy changes
- **Best Practice Sharing:** Sharing compliance success stories
- **Issue Awareness:** Communication about compliance challenges
- **Recognition Programs:** Acknowledging good compliance behavior

## Continuous Improvement

### Policy Evolution
- **Regular Review:** Policies reviewed annually or as needed
- **Stakeholder Input:** Feedback from users and stakeholders
- **Industry Changes:** Updates based on industry best practices
- **Lessons Learned:** Improvements based on compliance experience

### Implementation Improvement
- **Process Optimization:** Streamlining compliance procedures
- **Tool Enhancement:** Improving compliance monitoring tools
- **Training Enhancement:** Improving training effectiveness
- **Communication Improvement:** Better compliance communication

---
*Effective policy compliance requires understanding, commitment, and 
continuous attention to both letter and spirit of policies*"""

        return {
            "status": "success",
            "prompt": {
                "name": "policy_compliance_guide",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }

    def _get_policy_violation_recovery_prompt(self) -> Dict[str, Any]:
        """Recovery procedures when policy conflicts arise."""
        content = """# Policy Violation Recovery Procedures

## Immediate Response Protocol

### 1. Stop and Assess (STOP)
- **Halt Current Operations:** Immediately cease activities that may 
  worsen the violation
- **Secure the System:** Prevent further unauthorized access or exposure
- **Document Initial State:** Capture current system state for analysis
- **Notify Stakeholders:** Alert relevant parties per escalation matrix

### 2. Identify and Classify (CLASSIFY)
```
Violation Severity Levels:

🔴 CRITICAL (Level 1):
- Security breach or data exposure
- System compromise or unauthorized access
- Regulatory compliance violation
- Safety risk to personnel or systems

🟡 HIGH (Level 2):
- Policy deviation with business impact
- Data quality or integrity issues
- Access control problems
- Performance degradation

🟢 MEDIUM (Level 3):
- Process deviation without immediate impact
- Documentation or reporting issues
- Minor configuration problems
- Training or awareness gaps
```

### 3. Immediate Containment (CONTAIN)
- **Isolate Affected Systems:** Limit scope of potential damage
- **Preserve Evidence:** Maintain logs and forensic information
- **Implement Temporary Controls:** Apply immediate protective measures
- **Communication Management:** Control information flow to prevent panic

## Recovery Procedures by Violation Type

### Security Violations

#### Unauthorized Access
```
Recovery Steps:
1. Disable compromised accounts immediately
2. Change all potentially affected passwords
3. Review access logs for full scope assessment
4. Implement additional authentication controls
5. Conduct security assessment of affected systems
6. Report to security team and management
```

#### Data Exposure
```
Recovery Steps:
1. Identify what data was exposed and to whom
2. Secure exposed data and prevent further access
3. Assess regulatory reporting requirements
4. Notify affected parties per legal requirements
5. Implement additional data protection measures
6. Conduct thorough security review
```

### Data Quality Violations

#### Content Corruption
```
Recovery Steps:
1. Identify extent of corrupted data
2. Restore from last known good backup
3. Validate restored data integrity
4. Analyze root cause of corruption
5. Implement preventive measures
6. Update data validation procedures
```

#### Classification Errors
```
Recovery Steps:
1. Identify misclassified content
2. Assess impact of misclassification
3. Reclassify content to appropriate memory types
4. Review and update classification procedures
5. Provide additional training if needed
6. Monitor for similar issues
```

### Access Control Violations

#### Permission Escalation
```
Recovery Steps:
1. Revoke inappropriate permissions immediately
2. Review all recent access grants
3. Audit affected accounts and resources
4. Implement principle of least privilege
5. Review permission granting procedures
6. Provide additional training to administrators
```

#### Role Boundary Violations
```
Recovery Steps:
1. Identify scope of boundary violations
2. Restore proper role boundaries
3. Review all role assignments
4. Update role definitions if necessary
5. Implement better role enforcement
6. Monitor for compliance going forward
```

## Investigation and Root Cause Analysis

### Evidence Collection
- **System Logs:** Collect all relevant system and application logs
- **User Actions:** Document all user actions leading to violation
- **Timeline Reconstruction:** Create detailed timeline of events
- **Impact Assessment:** Assess full scope and impact of violation

### Root Cause Categories
1. **Human Error:** Mistakes in judgment, process, or execution
2. **System Failure:** Technical system or infrastructure failure
3. **Process Gap:** Inadequate or unclear procedures
4. **Training Deficit:** Insufficient knowledge or awareness
5. **Design Flaw:** Fundamental issue with system design
6. **External Factor:** Outside influence or attack

### Analysis Framework
```
5 Why Analysis:
1. Why did the violation occur?
2. Why did the underlying cause exist?
3. Why was this cause not prevented?
4. Why were controls inadequate?
5. Why was the risk not identified?

Result: Root cause identification and corrective action plan
```

## Corrective Action Planning

### Short-term Actions (24-48 hours)
- **Immediate Fixes:** Address urgent safety and security issues
- **Temporary Controls:** Implement interim risk mitigation
- **Communication:** Stakeholder notification and updates
- **Monitoring:** Enhanced monitoring of affected systems

### Medium-term Actions (1-4 weeks)
- **Process Updates:** Revise procedures based on lessons learned
- **Training Programs:** Additional training for affected personnel
- **System Enhancements:** Implement technical improvements
- **Control Implementation:** Add preventive controls

### Long-term Actions (1-6 months)
- **Systematic Review:** Comprehensive review of related processes
- **Culture Change:** Address underlying cultural issues
- **Technology Upgrade:** Major system or infrastructure changes
- **Policy Updates:** Revise policies based on lessons learned

## Recovery Validation

### Recovery Verification Checklist
- [ ] Root cause identified and addressed
- [ ] All affected systems restored to normal operation
- [ ] Security vulnerabilities closed
- [ ] Process improvements implemented
- [ ] Training completed where needed
- [ ] Monitoring enhanced to prevent recurrence

### Post-Recovery Activities
- **Lessons Learned Session:** Document insights and improvements
- **Process Documentation:** Update procedures based on experience
- **Training Updates:** Incorporate new knowledge into training
- **Risk Assessment Update:** Revise risk assessments as needed

## Communication and Reporting

### Internal Communication
- **Immediate Notification:** Alert stakeholders of violation and response
- **Progress Updates:** Regular updates during recovery process
- **Resolution Report:** Final report on resolution and lessons learned
- **Training Communication:** Share learnings with broader organization

### External Reporting
- **Regulatory Reporting:** Meet all regulatory notification requirements
- **Customer Communication:** Notify affected customers appropriately
- **Partner Notification:** Inform business partners as required
- **Public Disclosure:** Handle public communication per policy

## Continuous Improvement

### Recovery Process Improvement
- **Response Time:** Analyze and improve violation response times
- **Effectiveness:** Measure recovery effectiveness and completeness
- **Cost Optimization:** Reduce cost of violation recovery
- **Prevention Focus:** Shift emphasis from recovery to prevention

### Organizational Learning
- **Knowledge Sharing:** Share recovery insights across organization
- **Best Practice Development:** Develop best practices from experience
- **Culture Enhancement:** Strengthen compliance culture
- **System Resilience:** Build more resilient systems and processes

---
*Effective violation recovery requires swift action, thorough analysis, 
and commitment to preventing recurrence*"""

        return {
            "status": "success",
            "prompt": {
                "name": "policy_violation_recovery",
                "content": content,
                "arguments_used": {},
                "timestamp": datetime.now().isoformat()
            }
        }