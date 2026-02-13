# Diagram Source Prompt

```text
Create a system for a Simple E-commerce System using file storage.
Components:
- ecommerce-web-client [container:node.js] [tier:frontend]
- api-ecommerce-gateway [container:go] [tier:gateway]
- api-product-service [container:node.js] [tier:service]
- api-order-service [container:node.js] [tier:service]
- E-commerce File Storage [tier:database]

Connections:
- ecommerce-web-client uses api-ecommerce-gateway
- api-ecommerce-gateway routes to api-product-service
- api-ecommerce-gateway routes to api-order-service
- api-product-service reads/writes E-commerce File Storage
- api-order-service reads/writes E-commerce File Storage
```

**Generated Config**:
- Multiplier: 1.0
- Components: 8
