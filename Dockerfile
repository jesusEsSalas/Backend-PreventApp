# Usa una imagen base de Python
FROM python:3.9.12

# Establece el directorio de trabajo
WORKDIR /Backend-PreventApp

# Copia los archivos necesarios
COPY . /Backend-PreventApp

RUN apt-get update \
 && apt-get install unixodbc -y \
 && apt-get install unixodbc-dev -y \
 && apt-get install freetds-dev -y \
 && apt-get install freetds-bin -y \
 && apt-get install tdsodbc -y \
 && apt-get install --reinstall build-essential -y
RUN apt-get update && apt-get install -y ca-certificates

RUN echo "[FreeTDS]\n\
Description = FreeTDS Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Instala las dependencias de Python
RUN pip install -r requirements.txt
# Copia el controlador de ODBC
# COPY C:/Users/salasje/Downloads/msodbcsql.msi .

#RUN msiexec /i msodbcsql.msi /qn

# Expone el puerto que la aplicación Flask utilizará
EXPOSE 5000

# Inicia la aplicación
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]