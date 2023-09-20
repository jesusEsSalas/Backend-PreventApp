# Usa una imagen base de Python
FROM python:3.9.12

# Establece el directorio de trabajo
WORKDIR /MODULAR

# Copia los archivos necesarios
COPY . /MODULAR

# Instala las dependencias de Python
RUN pip install -r requirements.txt

ADD odbcinst.ini /etc/odbcinst.ini
RUN apt-get update
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt-get update && apt-get install -y ca-certificates
RUN apt-get clean -y

# Copia el controlador de ODBC
# COPY C:/Users/salasje/Downloads/msodbcsql.msi .

#RUN msiexec /i msodbcsql.msi /qn

# Expone el puerto que la aplicación Flask utilizará
# EXPOSE 5000

# Inicia la aplicación
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]