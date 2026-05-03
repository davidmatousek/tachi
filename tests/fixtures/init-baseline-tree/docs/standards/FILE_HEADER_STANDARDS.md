<!--
File: FILE_HEADER_STANDARDS.md
Description: Standardized file header requirements for all project files
Author/Agent: architect
Created: 2025-09-17
Last Updated: 2025-09-17
-->

# File Header Standards

All new or updated files must include a standardized header at the top to maintain consistency and provide essential metadata.

## Documentation Files (.md)

```markdown
<!--
File: [filename]
Description: [Brief description of file purpose and contents]
Author/Agent: [Creating agent name or human author]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]
-->
```

### Example:
```markdown
<!--
File: PROJECT_OVERVIEW.md
Description: Comprehensive overview of AI Security Scanner project status and features
Author/Agent: architect
Created: 2025-09-17
Last Updated: 2025-09-17
-->
```

## Code Files (.py, .js, .ts, etc.)

```python
"""
File: [filename]
Description: [Brief description of file purpose and functionality]
Author/Agent: [Creating agent name or human author]
Created: [YYYY-MM-DD]
Last Updated: [YYYY-MM-DD]
"""
```

### Example:
```python
"""
File: security_orchestrator.py
Description: Multi-agent coordination system for security vulnerability detection
Author/Agent: senior-backend-engineer
Created: 2025-08-15
Last Updated: 2025-09-10
"""
```

## Configuration Files (.json, .yaml, .env, etc.)

```bash
# File: [filename]
# Description: [Brief description of configuration purpose]
# Author/Agent: [Creating agent name or human author]
# Created: [YYYY-MM-DD]
# Last Updated: [YYYY-MM-DD]
```

### Example:
```yaml
# File: docker-compose.yml
# Description: Docker Compose configuration for local development environment
# Author/Agent: devops
# Created: 2025-08-20
# Last Updated: 2025-09-12
```

## Header Guidelines

### **Required Fields:**
- **File**: Exact filename (not path)
- **Description**: Concise but informative purpose statement
- **Author/Agent**: Creating agent name or human author
- **Created**: Initial creation date (YYYY-MM-DD format)
- **Last Updated**: Most recent significant change date

### **Best Practices:**

#### **Author/Agent Field:**
- **Agent work**: Use agent name (`architect`, `head-honcho`, `devops`, etc.)
- **Human work**: Use human name or username
- **Collaborative**: Use primary author/agent

#### **Description Field:**
- **Be specific**: "User authentication system" not "Auth stuff"
- **Include scope**: "Frontend components for user dashboard"
- **Mention key features**: "Multi-agent coordination with deduplication"

#### **Date Management:**
- **ISO format**: Always use YYYY-MM-DD
- **Update Last Updated**: When making significant changes
- **Preserve Created**: Never change the original creation date

#### **When to Update:**
- **Significant functionality changes**
- **Major refactoring or restructuring**
- **Adding new features or capabilities**
- **Don't update for**: Minor typos, formatting, comment changes

## Implementation Requirements

### **For New Files:**
- **Always include headers** before first commit
- **Use appropriate template** based on file type
- **Fill all required fields** accurately

### **For Existing Files:**
- **Add headers when editing** files that lack them
- **Update Last Updated date** when making significant changes
- **Preserve git history** - don't mass-update just for headers

### **Quality Checks:**
- **Filename matches**: Header filename matches actual filename
- **Description accuracy**: Description reflects actual file purpose
- **Date consistency**: Dates are logical (created ≤ last updated)
- **Agent attribution**: Correct agent/author for the work type

## Examples by File Type

### **Architecture Documentation:**
```markdown
<!--
File: 01-system-overview.md
Description: Primary system architecture and current production status
Author/Agent: architect
Created: 2025-09-07
Last Updated: 2025-09-17
-->
```

### **Agent Planning Documents:**
```markdown
<!--
File: strategic-api-key-system-2025-09-15.md
Description: Strategic plan for API key generation system implementation
Author/Agent: head-honcho
Created: 2025-09-15
Last Updated: 2025-09-15
-->
```

### **Backend Implementation:**
```python
"""
File: mcp_server.py
Description: MCP server implementation with authentication and agent orchestration
Author/Agent: senior-backend-engineer
Created: 2025-08-30
Last Updated: 2025-09-14
"""
```

### **Frontend Components:**
```typescript
/**
 * File: AuthModal.tsx
 * Description: Authentication modal component with OAuth and API key flows
 * Author/Agent: code-monkey
 * Created: 2025-09-10
 * Last Updated: 2025-09-13
 */
```

### **Deployment Configuration:**
```yaml
# File: production.yml
# Description: Production deployment configuration for Google Cloud Run
# Author/Agent: devops
# Created: 2025-09-05
# Last Updated: 2025-09-16
```

---

*These standards ensure consistent documentation and maintainability across all project files.*