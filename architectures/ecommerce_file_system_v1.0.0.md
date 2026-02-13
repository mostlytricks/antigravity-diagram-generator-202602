# Diagram Source Prompt

```text
Create a simple file-based E-commerce system.
Components:
- ecommerce-web-client [container:node.js] [tier:frontend]
- api-ecommerce-service [container:python] [tier:service]
- Local File System [tier:database]

Connections:
- ecommerce-web-client uses api-ecommerce-service
- api-ecommerce-service reads/writes Local File System
```

**Generated Config**:
- Multiplier: 1.0
- Components: 6
