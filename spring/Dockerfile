FROM eclipse-temurin:21.0.2_13-jdk-jammy AS builder

RUN apt-get update && apt-get install -y \
    git \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY wait-for-mysql.sh .
RUN chmod +x /opt/app/wait-for-mysql.sh

RUN git clone https://github.com/Assiminee/Tickefy-Spring-React.git && \
    cp -R Tickefy/Tickefy/. . &&  \
    rm -rf ./Tickefy

RUN chmod +x mvnw
RUN ./mvnw dependency:go-offline
RUN ./mvnw clean install -DskipTests

FROM eclipse-temurin:21.0.2_13-jre-jammy AS final

WORKDIR /opt/app
EXPOSE 8080

RUN apt-get update && apt-get install -y netcat-openbsd

COPY --from=builder /opt/app/target/*.jar /opt/app/*.jar
COPY --from=builder /opt/app/wait-for-mysql.sh /opt/app/wait-for-mysql.sh
RUN chmod +x /opt/app/wait-for-mysql.sh

ENTRYPOINT ["/opt/app/wait-for-mysql.sh", "mysql", "3306", "java", "-jar", "/opt/app/*.jar"]
