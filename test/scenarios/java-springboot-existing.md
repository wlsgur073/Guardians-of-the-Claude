---
id: java-springboot-existing
language: Java
framework: Spring Boot
state: existing
phase: 1
priority: medium
fixture: java-springboot
---

# Java Spring Boot — Existing Project

## Project Description
An existing Spring Boot web application with Maven, featuring established layered architecture with service and controller layers.

## Fixture Contents
- pom.xml
- mvnw
- src/main/java/com/example/demo/DemoApplication.java
- src/main/java/com/example/demo/controller/UserController.java
- src/main/java/com/example/demo/service/UserService.java
- src/main/java/com/example/demo/model/User.java
- src/main/resources/application.properties

## /generate Evaluation Focus
- Detect layered architecture (controller, service, model/entity)
- Recognize existing service patterns and naming conventions
- Preserve existing package structure and Spring annotations
- Merge configuration without overwriting application.properties

## /audit Evaluation Focus
- Recognize Spring Boot project maturity from layer depth
- Identify existing test patterns or missing test coverage
- Appropriate suggestions for an established Spring Boot codebase
