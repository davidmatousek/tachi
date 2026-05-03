<!--
File: definition-of-done.md
Description: Comprehensive Definition of Done requirements and validation procedures
Author/Agent: claude
Created: 2025-09-16
Last Updated: 2025-09-16
-->

# Definition of Done (DoD) Requirements

**CRITICAL: All deliverables must meet the complete Definition of Done before being marked as "DELIVERED"**

## **3-Step DoD Validation Process**

Every development phase and deliverable must complete ALL three validation steps:

### **1. ✅ Pushed to Production**
- Code changes deployed to production environment
- All features accessible to end users
- Production environment validated and operational

### **2. ✅ Tested with Playwright MCP Server**
- Complete user workflows validated using MCP browser automation
- End-to-end functionality confirmed through actual browser testing
- UI components and user interactions verified working

### **3. ✅ Validated by User Personal Testing**
- User confirms functionality works as expected
- Real-world usage scenarios tested and approved
- User experience meets requirements and expectations

## **DoD Status Terminology**

- **"Local Dev Completed"**: Development work finished in local environment only
- **"DoD In Progress"**: Working through the 3-step validation process
- **"DELIVERED"**: ALL three DoD criteria met and validated

## **Phase DoD Checklist Template**

Every phase must include:
```
Definition of Done Checklist for Phase X:
- [ ] Pushed to Production
- [ ] Playwright MCP Tested
- [ ] User Validated
```

## **DoD Enforcement**

- **No phase is "DELIVERED" until all DoD criteria are met**
- **Phases may be "completed" in local development but require full DoD validation**
- **Production deployment issues block DoD completion**
- **Testing failures require remediation before DoD completion**
- **User validation failures require rework before DoD completion**

## **DoD Exceptions**

- **Documentation-only phases**: May not require production deployment
- **Architecture phases**: Validated through implementation phases
- **Planning phases**: Delivered when plans are approved and handed off

## **Implementation Guidelines**

### **Phase Completion vs. Delivery**
- **Phase completion** ≠ **Delivery**: Local dev completion requires DoD validation for delivery
- **Production deployment issues** block DoD completion
- **Testing failures** require remediation before DoD completion
- **User validation failures** require rework before DoD completion

### **Quality Assurance**
The Definition of Done ensures that all deliverables provide real value to users and meet production quality standards. No shortcuts or exceptions allowed for core functionality phases.

### **DoD Integration with Development Workflow**
1. **Planning Phase**: Include DoD checklist in phase planning
2. **Development Phase**: Track DoD progress throughout implementation
3. **Validation Phase**: Complete all three DoD steps before marking as delivered
4. **Documentation Phase**: Update project documentation with DoD completion status

**IMPORTANT**: The Definition of Done is non-negotiable for core functionality phases. It ensures quality, user value, and production readiness across all deliverables.