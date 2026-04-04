---
id: java-springboot-new
language: Java
framework: Spring Boot
state: new
phase: 1
priority: high
fixture: java-springboot
---

# Java Spring Boot — New Project

## Project Description
A new Spring Boot web application with Maven as the build tool, generated via Spring Initializr with web and JPA starters.

## Fixture Contents
- pom.xml
- src/main/java/com/example/demo/DemoApplication.java
- src/main/resources/application.properties
- mvnw

## /generate Evaluation Focus
- Maven commands (mvn clean, mvn test, mvn package, mvn spring-boot:run)
- Java package structure awareness (com.example.demo)
- Spring security annotations and configuration patterns
- Maven wrapper (./mvnw) recognition

## /audit Evaluation Focus
- Maven build and test command detection (mvn test or ./mvnw test)
- Java project structure recognition (src/main/java, src/test/java)
- Spring Boot starter dependency awareness
